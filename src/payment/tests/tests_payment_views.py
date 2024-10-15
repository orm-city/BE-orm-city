import pytest
from datetime import timedelta

from django.urls import reverse
from django.core.exceptions import ValidationError
from django.utils import timezone

from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import CustomUser
from courses.models import MajorCategory
from payment.models import Payment
from payment.serializers import PaymentDetailSerializer

from unittest.mock import patch


@pytest.fixture
def api_client():
    """
    APIClient 인스턴스를 생성하고 반환합니다.

    Returns:
        APIClient: REST API 테스트를 위한 APIClient 객체.
    """
    return APIClient()


@pytest.fixture
def user():
    """
    테스트용 사용자 생성.

    Returns:
        CustomUser: 테스트용으로 생성된 사용자 객체.
    """
    return CustomUser.objects.create_user(
        email="test@test.com", username="testuser", password="test1234"
    )


@pytest.fixture
def payment(user):
    """
    테스트용 결제 정보 생성.

    Args:
        user (CustomUser): 결제를 할 사용자 객체.

    Returns:
        Payment: 생성된 Payment 객체.
    """
    return Payment.objects.create(
        user=user,
        merchant_uid="test_merchant_uid",
        imp_uid="test_imp_uid",
        total_amount=10000,
        payment_status="paid",
        payment_date=timezone.now(),
        refund_status="NOT_REQUESTED",
    )


@pytest.mark.django_db
class TestPaymentInfoAPIView:
    """
    PaymentInfoAPIView 테스트 클래스.

    API를 호출하여 결제 정보가 제대로 반환되는지 확인하는 테스트 케이스들을 포함합니다.
    """

    @pytest.fixture(autouse=True)
    def setup(self):
        """
        테스트를 위한 사용자와 API 클라이언트를 설정합니다.
        """
        self.client = APIClient()
        self.user = CustomUser.objects.create_user(
            email="test@test.com", username="testuser", password="test1234"
        )
        self.major_category = MajorCategory.objects.create(
            name="Test Course", price=50000
        )

    def test_payment_info_api_view_success(self):
        """
        PaymentInfoAPIView가 주어진 강의(MajorCategory) ID에 대해 올바른 정보를 반환하는지 확인합니다.

        - API 엔드포인트를 호출하고 200 OK 상태 코드를 확인합니다.
        - 반환된 데이터가 생성한 강의 정보와 일치하는지 검증합니다.
        """
        self.client.force_authenticate(user=self.user)

        url = reverse("payment:payment-info", args=[self.major_category.id])
        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["major_category_name"] == self.major_category.name
        assert response.data["major_category_price"] == self.major_category.price

    def test_payment_info_api_view_not_found(self):
        """
        존재하지 않는 강의 ID로 요청 시 적절한 오류 응답을 반환하는지 확인합니다.

        - API 엔드포인트 호출 시 404 Not Found 응답을 확인합니다.
        - 반환된 오류 메시지가 예상된 내용을 포함하는지 검증합니다.
        """
        self.client.force_authenticate(user=self.user)

        url = reverse("payment:payment-info", args=[999])  # 존재하지 않는 ID 사용
        response = self.client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "해당 강의를 찾을 수 없습니다." in response.data["error"]


class PaymentCompleteAPIView(APIView):
    """
    결제 완료 및 수강 등록 처리 APIView.

    사용자가 제출한 결제 정보를 바탕으로 결제를 처리하고, 수강 등록을 완료합니다.
    """

    def post(self, request):
        """
        결제 정보를 처리하고, 수강 등록을 완료합니다.

        Args:
            request: 사용자 ID, 강의 ID, merchant_uid 등의 데이터를 포함한 HTTP 요청 객체.

        Returns:
            Response: 결제 완료 또는 오류 메시지를 포함한 응답 객체.

        Raises:
            ValidationError: 요청된 데이터가 유효하지 않은 경우.
            Exception: 기타 예기치 못한 오류 발생 시 500 응답을 반환합니다.
        """
        try:
            user_id = request.data.get("user_id")
            major_category_id = request.data.get("major_category_id")
            merchant_uid = request.data.get("merchant_uid")

            # 사용자 확인
            try:
                user = CustomUser.objects.get(id=user_id)
            except CustomUser.DoesNotExist:
                return Response(
                    {"error": "해당 사용자를 찾을 수 없습니다."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # 강의 확인
            try:
                major_category = MajorCategory.objects.get(id=major_category_id)
            except MajorCategory.DoesNotExist:
                return Response(
                    {"error": "해당 강의를 찾을 수 없습니다."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # 중복 결제 확인
            if Payment.objects.filter(merchant_uid=merchant_uid).exists():
                return Response(
                    {"error": "이미 처리된 결제입니다."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # 결제 정보 저장
            Payment.objects.create(
                user=user,
                major_category=major_category,
                total_amount=major_category.price,
                merchant_uid=merchant_uid,
                payment_status="paid",
                imp_uid=request.data.get("imp_uid"),
            )

            return Response(
                {"message": "결제 및 수강 등록이 성공적으로 완료되었습니다."},
                status=status.HTTP_201_CREATED,
            )

        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            return Response(
                {"error": "결제 처리 중 오류가 발생했습니다."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


@pytest.mark.django_db
class TestUserPaymentsView:
    """
    사용자 결제 내역 API 테스트 클래스.

    이 클래스는 사용자 결제 내역을 조회하는 API의 기능을 검증합니다.
    """

    @pytest.fixture(autouse=True)
    def setup(self):
        """
        테스트를 위한 기본 설정을 수행합니다.

        사용자와 API 클라이언트를 생성하고, 테스트 강의를 생성합니다.
        """
        self.client = APIClient()
        self.user = CustomUser.objects.create_user(
            email="test@example.com", username="testuser", password="testpass"
        )
        self.major_category = MajorCategory.objects.create(
            name="Test Course", price=50000
        )
        self.url = reverse("payment:user-payments")

    def create_payment(self, days_ago, status="paid"):
        """
        테스트용 결제 정보를 생성하는 헬퍼 메서드.

        Args:
            days_ago (int): 결제가 이루어진 날짜(과거 날짜를 설정).
            status (str): 결제 상태 (기본값: 'paid').

        Returns:
            Payment: 생성된 결제 정보 객체.
        """
        payment_date = timezone.now() - timedelta(days=days_ago)
        return Payment.objects.create(
            user=self.user,
            major_category=self.major_category,
            total_amount=self.major_category.price,
            payment_status=status,
            payment_date=payment_date,
        )


@pytest.mark.django_db
class TestPaymentDetailView:
    """
    결제 상세 정보 API 테스트 클래스.

    특정 결제 정보의 상세 내용을 조회하는 API의 기능을 검증합니다.
    """

    @pytest.fixture(autouse=True)
    def setup(self, api_client, user, payment):
        """
        테스트를 위한 기본 설정을 수행합니다.

        사용자와 결제 정보, 그리고 API 클라이언트를 설정합니다.
        """
        self.client = api_client
        self.user = user
        self.payment = payment
        self.url = reverse(
            "payment:payment-detail", kwargs={"payment_id": self.payment.id}
        )

    def test_get_payment_detail_success(self):
        """
        결제 상세 정보 API가 올바른 결제 정보를 반환하는지 확인합니다.
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data == PaymentDetailSerializer(self.payment).data

    def test_get_payment_detail_not_found(self):
        """
        존재하지 않는 결제 ID로 요청 시 404 오류를 반환하는지 확인합니다.
        """
        self.client.force_authenticate(user=self.user)
        non_existent_url = reverse(
            "payment:payment-detail", kwargs={"payment_id": 99999}
        )
        response = self.client.get(non_existent_url)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.data == {"error": "결제 정보를 찾을 수 없습니다."}

    def test_get_payment_detail_unauthorized(self):
        """
        인증되지 않은 상태에서 결제 상세 정보를 요청할 경우 401 오류를 반환하는지 확인합니다.
        """
        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_payment_detail_wrong_user(self):
        """
        다른 사용자가 결제 정보를 조회하려고 할 경우 404 오류를 반환하는지 확인합니다.
        """
        other_user = CustomUser.objects.create_user(
            email="other@test.com", username="otheruser", password="otherpass"
        )
        self.client.force_authenticate(user=other_user)
        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.data == {"error": "결제 정보를 찾을 수 없습니다."}

    @pytest.mark.parametrize(
        "permission_class",
        [
            "IsAuthenticatedAndAllowed",
        ],
    )
    def test_permission_classes(self, permission_class):
        """
        결제 상세 정보 뷰에서 사용되는 권한 클래스가 올바른지 확인합니다.
        """
        from payment.views import PaymentDetailView

        assert permission_class in [
            p.__name__ for p in PaymentDetailView.permission_classes
        ]

    @pytest.mark.parametrize(
        "authentication_class",
        [
            "JWTAuthentication",
        ],
    )
    def test_authentication_classes(self, authentication_class):
        """
        결제 상세 정보 뷰에서 사용되는 인증 클래스가 올바른지 확인합니다.
        """
        from payment.views import PaymentDetailView

        assert authentication_class in [
            a.__name__ for a in PaymentDetailView.authentication_classes
        ]


@pytest.mark.django_db
class TestRefundAPIView:
    """
    환불 API 테스트 클래스.

    결제 환불 처리 기능을 검증합니다.
    """

    @pytest.fixture(autouse=True)
    def setup(self, api_client, user, payment):
        """
        테스트를 위한 기본 설정을 수행합니다.

        사용자, 결제 정보, 그리고 API 클라이언트를 설정합니다.
        """
        self.client = api_client
        self.user = user
        self.payment = payment
        self.url = reverse(
            "payment:payment-refund", kwargs={"payment_id": self.payment.id}
        )

    @patch("payment.views.RefundAPIView.get_iamport_token")
    @patch("payment.views.RefundAPIView.request_refund")
    def test_refund_success(self, mock_request_refund, mock_get_token):
        """
        환불 요청이 성공적으로 처리되는지 테스트합니다.

        mock을 이용해 환불 요청 성공 시나리오를 검증합니다.
        """
        mock_get_token.return_value = "fake_token"
        mock_request_refund.return_value = {"code": 0, "message": "success"}

        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data == {"message": "환불이 성공적으로 처리되었습니다."}

        self.payment.refresh_from_db()
        assert self.payment.refund_status == "COMPLETED"
        assert self.payment.payment_status == "cancelled"

    def test_refund_unauthenticated(self):
        """
        인증되지 않은 상태에서 환불 요청 시 401 오류를 반환하는지 테스트합니다.
        """
        response = self.client.post(self.url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_refund_payment_not_found(self):
        """
        존재하지 않는 결제 ID로 요청 시 404 오류를 반환하는지 테스트합니다.
        """
        self.client.force_authenticate(user=self.user)
        url = reverse("payment:payment-refund", kwargs={"payment_id": 99999})
        response = self.client.post(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.data == {"error": "결제 정보를 찾을 수 없습니다."}

    def test_refund_already_requested(self):
        """
        이미 환불 요청된 결제에 대해 다시 요청할 경우 400 오류를 반환하는지 테스트합니다.
        """
        self.payment.refund_status = "REQUESTED"
        self.payment.save()

        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data == {"error": "이미 환불이 진행 중이거나 완료되었습니다."}

    @patch("payment.views.RefundAPIView.get_iamport_token")
    def test_refund_token_failure(self, mock_get_token):
        """
        결제 시스템 토큰을 가져오지 못했을 때의 처리 상황을 테스트합니다.
        """
        mock_get_token.return_value = None

        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url)

        assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
        assert response.data == {"error": "결제 시스템 연결에 실패했습니다."}

    # @patch("payment.views.RefundAPIView.get_iamport_token")
    # @patch("payment.views.RefundAPIView.request_refund")
    # def test_refund_failure(self, mock_request_refund, mock_get_token):
    #     mock_get_token.return_value = "fake_token"
    #     mock_request_refund.return_value = {"code": 1, "message": "refund failed"}

    #     self.client.force_authenticate(user=self.user)
    #     response = self.client.post(self.url)

    #     assert response.status_code == status.HTTP_400_BAD_REQUEST
    #     assert response.data == {"error": "refund failed"}

    #     self.payment.refresh_from_db()
    #     assert self.payment.refund_status == "FAILED"

    @patch("payment.views.RefundAPIView.get_iamport_token")
    @patch("payment.views.RefundAPIView.request_refund")
    def test_refund_exception(self, mock_request_refund, mock_get_token):
        """
        환불 처리 중 예상치 못한 오류가 발생하는 상황을 테스트합니다.
        """
        mock_get_token.return_value = "fake_token"
        mock_request_refund.side_effect = Exception("Unexpected error")

        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url)

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert response.data == {"error": "환불 처리 중 오류가 발생했습니다."}

        self.payment.refresh_from_db()
        assert self.payment.refund_status == "FAILED"
