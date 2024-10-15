import json
import logging
import requests

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from accounts.models import CustomUser
from .models import MajorCategory, Payment, Enrollment
from .serializers import PaymentDetailSerializer
from .permissions import IsAuthenticatedAndAllowed

from drf_spectacular.utils import extend_schema, OpenApiParameter


logger = logging.getLogger(__name__)


@extend_schema(
    summary="아임포트 결제정보",
    description="대분류명(대카테고리 수강명), 수강금액 정보를 아임포트 결제창에 전달합니다.",
    parameters=[
        OpenApiParameter(
            name="major_category_id",
            description="ID of the major category",
            required=True,
            type=int,
        ),
    ],
    responses={
        200: {
            "type": "object",
            "properties": {
                "major_category_id": {"type": "integer"},
                "major_category_name": {"type": "string"},
                "major_category_price": {"type": "number"},
                "user_id": {"type": "integer"},
                "imp_key": {"type": "string"},
            },
        },
        404: {"description": "Major category not found"},
    },
)
class PaymentInfoAPIView(APIView):
    """
    아임포트 결제 정보를 제공하는 APIView.

    사용자와 선택한 수강 카테고리 정보를 바탕으로 아임포트 결제창에 필요한 데이터를 반환합니다.

    Attributes:
        permission_classes (list): 접근 권한을 정의하는 클래스 리스트.
    """

    permission_classes = [IsAuthenticatedAndAllowed]

    def get(self, request, major_category_id):
        """
        GET 요청을 처리하여 아임포트 결제창에 필요한 정보를 반환합니다.

        Args:
            request (Request): Django의 HTTP 요청 객체.
            major_category_id (int): 수강 카테고리 ID.

        Returns:
            Response: 결제창에 필요한 정보가 담긴 응답 객체.
        """
        try:
            major_category = MajorCategory.objects.get(id=major_category_id)
            user = request.user
            data = {
                "major_category_id": major_category.id,
                "major_category_name": major_category.name,
                "major_category_price": major_category.price,
                "user_id": user.id,
                "imp_key": settings.IAMPORT["IMP_KEY"],
            }
            return Response(data, status=status.HTTP_200_OK)
        except MajorCategory.DoesNotExist:
            return Response(
                {"error": "해당 강의를 찾을 수 없습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )


@extend_schema(
    summary="결제 생성(수강정보,수강신청 저장)",
    description="수강 결제가 생성되면 해당 수강상품에 대한 enrollment 데이터가 등록됩니다.",
    request={
        "type": "object",
        "properties": {
            "user_id": {"type": "integer"},
            "imp_uid": {"type": "string"},
            "merchant_uid": {"type": "string"},
            "major_category_id": {"type": "integer"},
            "total_amount": {"type": "number"},
        },
        "required": [
            "user_id",
            "imp_uid",
            "merchant_uid",
            "major_category_id",
            "total_amount",
        ],
    },
    responses={
        201: {
            "type": "object",
            "properties": {
                "message": {"type": "string"},
                "payment_id": {"type": "integer"},
                "enrollment_id": {"type": "integer"},
                "status": {"type": "string"},
                "refund_deadline": {"type": "string", "format": "date-time"},
            },
        },
        400: {"description": "올바르지 않은 결제정보이거나 중복 결제입니다."},
        404: {"description": "사용자 혹은 major category 정보가 확인되지 않습니다."},
    },
)
class PaymentCompleteAPIView(APIView):
    """
    결제 완료 처리 APIView.

    사용자로부터 결제 정보를 받아 처리하고, 수강 등록(enrollment)을 생성합니다.

    Attributes:
        permission_classes (list): 접근 권한을 정의하는 클래스 리스트.
        http_method_names (list): 허용되는 HTTP 메서드 목록.
    """

    permission_classes = [IsAuthenticatedAndAllowed]
    http_method_names = ["post"]

    def get_iamport_token(self):
        """
        아임포트 API로부터 인증 토큰을 획득합니다.

        Returns:
            str: 인증 토큰.
        """
        url = "https://api.iamport.kr/users/getToken"
        headers = {
            "Content-Type": "application/json",
            "charset": "UTF-8",
            "Accept": "*/*",
        }
        body = {
            "imp_key": settings.IAMPORT["IMP_KEY"],
            "imp_secret": settings.IAMPORT["IMP_SECRET"],
        }
        try:
            response = requests.post(
                url,
                headers=headers,
                data=json.dumps(body, ensure_ascii=False, indent="\t"),
            )
            if response.status_code == 200:
                json_object = json.loads(response.text)
                return json_object["response"]["access_token"]
            logger.error(
                f"Failed to get Iamport token: {response.status_code}, {response.text}"
            )
            return None
        except requests.RequestException as ex:
            logger.error(f"Request to Iamport failed: {ex}")
            return None

    def verify_iamport_payment(self, imp_uid, amount, token):
        """
        아임포트 결제 정보를 검증합니다.

        Args:
            imp_uid (str): 아임포트 거래 고유 번호.
            amount (int): 결제 금액.
            token (str): 아임포트 API 인증 토큰.

        Returns:
            bool: 결제 정보가 유효한 경우 True, 그렇지 않으면 False.
        """
        url = f"https://api.iamport.kr/payments/{imp_uid}"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        }
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            payment_data = response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"아임포트 API 호출 실패: {e}")
            raise ValidationError("결제 정보 확인 실패")
        except ValueError as e:
            logger.error(f"아임포트 API 응답 파싱 오류: {e}")
            raise ValidationError("결제 정보 처리 중 오류가 발생했습니다.")

        if payment_data.get("code") != 0:
            logger.error(f"아임포트 결제 데이터 획득 실패: {payment_data}")
            raise ValidationError("결제 정보를 받아올 수 없습니다.")

        iamport_amount = int(payment_data["response"]["amount"])
        iamport_status = payment_data["response"]["status"]

        if iamport_status != "paid" or iamport_amount != int(amount):
            logger.warning(
                f"결제 검증 실패: status={iamport_status}, amount={iamport_amount} vs {amount}"
            )
            raise ValidationError("결제 금액 또는 상태가 일치하지 않습니다.")

        return True

    @transaction.atomic
    def post(self, request):
        """
        결제 완료 후 수강 등록을 처리합니다.

        Args:
            request (Request): HTTP 요청 객체.

        Returns:
            Response: 결제 및 수강 등록 완료 메시지를 포함한 응답 객체.
        """
        user_id = request.data.get("user_id")
        imp_uid = request.data.get("imp_uid")
        merchant_uid = request.data.get("merchant_uid")
        major_category_id = request.data.get("major_category_id")
        total_amount = request.data.get("total_amount")

        logger.info(f"Received payment data: {request.data}")

        if not all([user_id, imp_uid, merchant_uid, major_category_id, total_amount]):
            logger.error("Missing required payment information")
            raise ValidationError("필수 결제 정보가 누락되었습니다.")

        try:
            user = CustomUser.objects.get(id=user_id)
            major_category = MajorCategory.objects.get(id=major_category_id)
        except CustomUser.DoesNotExist:
            logger.error(f"User not found: user_id={user_id}")
            raise ValidationError("해당 사용자를 찾을 수 없습니다.")
        except MajorCategory.DoesNotExist:
            logger.error(
                f"Major category not found: major_category_id={major_category_id}"
            )
            raise ValidationError("해당 강의를 찾을 수 없습니다.")

        if Payment.objects.filter(imp_uid=imp_uid).exists():
            logger.warning(f"Duplicate payment attempt: imp_uid={imp_uid}")
            raise ValidationError("이미 처리된 결제입니다.")

        # Payment 생성
        try:
            payment = Payment.objects.create(
                user=user,
                major_category=major_category,
                total_amount=total_amount,
                merchant_uid=merchant_uid,
                payment_status="paid",
                receipt_url=f"https://api.iamport.kr/payments/{imp_uid}",
                imp_uid=imp_uid,
                refund_deadline=timezone.now()
                + timezone.timedelta(days=7),  # 7일 환불 기한 설정
            )
            logger.info(f"Payment created successfully: id={payment.id}")
        except Exception as e:
            logger.error(f"Failed to create payment: {str(e)}")
            raise ValidationError("결제 정보 생성 중 오류가 발생했습니다.")

        # Enrollment 생성
        try:
            enrollment = Enrollment.objects.create(
                user=user,
                major_category=major_category,
                enrollment_date=timezone.now(),
                expiry_date=timezone.now() + timezone.timedelta(days=365 * 2 - 1),
                status="active",
            )
            logger.info(f"Enrollment created successfully: id={enrollment.id}")

            payment.enrollment = enrollment
            payment.save()
            logger.info(
                f"Payment updated with enrollment: payment_id={payment.id}, enrollment_id={enrollment.id}"
            )
        except Exception as e:
            logger.error(f"Failed to create enrollment: {str(e)}")
            raise ValidationError(f"수강 등록 중 오류가 발생했습니다: {str(e)}")

        return Response(
            {
                "message": "결제 및 수강 등록이 성공적으로 완료되었습니다.",
                "payment_id": payment.id,
                "enrollment_id": enrollment.id,
                "status": payment.payment_status,
                "refund_deadline": payment.refund_deadline,
            },
            status=status.HTTP_201_CREATED,
        )


class UserPaymentsView(APIView):
    """
    사용자의 결제 내역을 조회하는 APIView.

    사용자와 관련된 모든 결제 내역을 조회하여 반환합니다.
    결제일 기준으로 내림차순으로 정렬되며, 각 결제의 환불 가능 여부를 포함합니다.
    """

    permission_classes = [IsAuthenticatedAndAllowed]
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        """
        사용자의 결제 내역을 조회하고 반환합니다.

        Args:
            request: HTTP 요청 객체.

        Returns:
            Response: 사용자의 결제 내역 목록을 포함한 JSON 응답.
        """
        payments = (
            Payment.objects.filter(user=request.user)
            .prefetch_related("major_category")
            .order_by("-payment_date")
        )
        current_time = timezone.now()

        payment_list = []
        for payment in payments:
            days_since_payment = (current_time - payment.payment_date).days
            is_refundable = days_since_payment < 7
            payment_list.append(
                {
                    "id": payment.id,
                    "amount": payment.total_amount,
                    "date": payment.payment_date,
                    "status": payment.payment_status,
                    "is_refundable": is_refundable,
                    "days_since_payment": days_since_payment,
                    "major_category": payment.major_category.name,
                }
            )

        return Response(payment_list)


class PaymentDetailView(APIView):
    """
    특정 결제 정보를 불러오는 APIView.
    """

    permission_classes = [IsAuthenticatedAndAllowed]
    authentication_classes = [JWTAuthentication]

    def get(self, request, payment_id):
        """
        특정 결제의 세부 정보를 조회합니다.

        Args:
            request: HTTP 요청 객체.
            payment_id: 조회할 결제의 ID.

        Returns:
            Response: 결제 세부 정보를 포함한 JSON 응답.
        """
        try:
            payment = Payment.objects.get(id=payment_id, user=request.user)
            serializer = PaymentDetailSerializer(payment)
            return Response(serializer.data)
        except Payment.DoesNotExist:
            return Response(
                {"error": "결제 정보를 찾을 수 없습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )


class RefundAPIView(APIView):
    """
    결제 환불을 처리하는 APIView.
    """

    permission_classes = [IsAuthenticatedAndAllowed]
    authentication_classes = [JWTAuthentication]

    def get_iamport_token(self):
        """
        아임포트 API로부터 인증 토큰을 요청합니다.

        Returns:
            str: 아임포트 인증 토큰.
        """
        url = "https://api.iamport.kr/users/getToken"
        headers = {
            "Content-Type": "application/json",
            "charset": "UTF-8",
            "Accept": "*/*",
        }
        body = {
            "imp_key": settings.IAMPORT["IMP_REST_API_KEY"],
            "imp_secret": settings.IAMPORT["IMP_SECRET"],
        }
        try:
            response = requests.post(
                url,
                headers=headers,
                data=json.dumps(body, ensure_ascii=False, indent="\t"),
            )
            if response.status_code == 200:
                json_object = json.loads(response.text)
                return json_object["response"]["access_token"]
            return None
        except requests.RequestException:
            logging.error("아임포트 토큰 획득 중 오류 발생")
            return None

    def post(self, request, payment_id):
        """
        환불을 요청하고 처리 결과를 반환합니다.

        Args:
            request: HTTP 요청 객체.
            payment_id: 환불할 결제의 ID.

        Returns:
            Response: 환불 처리 결과.
        """
        try:
            payment = Payment.objects.get(id=payment_id, user=request.user)
        except Payment.DoesNotExist:
            return Response(
                {"error": "결제 정보를 찾을 수 없습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if payment.refund_status != "NOT_REQUESTED":
            return Response(
                {"error": "이미 환불이 진행 중이거나 완료되었습니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        access_token = self.get_iamport_token()
        if not access_token:
            return Response(
                {"error": "결제 시스템 연결에 실패했습니다."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        try:
            refund_result = self.request_refund(
                access_token, payment.imp_uid, payment.total_amount
            )

            if refund_result.get("code") == 0:
                payment.refund_status = "COMPLETED"
                payment.payment_status = "cancelled"
                payment.save()
                return Response(
                    {"message": "환불이 성공적으로 처리되었습니다."},
                    status=status.HTTP_200_OK,
                )
            else:
                payment.refund_status = "FAILED"
                payment.save()
                logging.error("Refund failed")
                return Response(
                    {"error": "환불 처리에 실패했습니다."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except Exception:
            payment.refund_status = "FAILED"
            payment.save()
            logging.exception("Exception during refund process")
            return Response(
                {"error": "환불 처리 중 오류가 발생했습니다."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def request_refund(self, access_token, imp_uid, amount):
        """
        아임포트 API로 환불 요청을 전송합니다.

        Args:
            access_token (str): 아임포트 인증 토큰.
            imp_uid (str): 환불할 결제의 아임포트 고유 ID.
            amount (int): 환불할 금액.

        Returns:
            dict: 환불 요청에 대한 응답 데이터.
        """
        url = "https://api.iamport.kr/payments/cancel"
        headers = {"Authorization": access_token, "Content-Type": "application/json"}
        data = {"imp_uid": imp_uid, "amount": amount, "reason": "고객 환불 요청"}
        try:
            response = requests.post(
                url,
                data=json.dumps(data, ensure_ascii=False).encode("utf-8"),
                headers=headers,
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.exception(f"Request failed during request_refund: {str(e)}")
            raise
