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


logger = logging.getLogger(__name__)


class PaymentInfoAPIView(APIView):
    permission_classes = [IsAuthenticatedAndAllowed]

    def get(self, request, major_category_id):
        try:
            major_category = MajorCategory.objects.get(id=major_category_id)
            user = request.user
            data = {
                "major_category_id": major_category.id,
                "major_category_name": major_category.name,
                "major_category_price": major_category.price,
                "user_id": user.id,  # 사용자 ID 사용
                "imp_key": settings.IAMPORT["IMP_KEY"],
            }
            return Response(data, status=status.HTTP_200_OK)
        except MajorCategory.DoesNotExist:
            return Response(
                {"error": "해당 강의를 찾을 수 없습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )


class PaymentCompleteAPIView(APIView):
    permission_classes = [IsAuthenticatedAndAllowed]
    http_method_names = ["post"]

    def get_iamport_token(self):
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
            # 응답 상태 코드 확인
            if response.status_code == 200:
                json_object = json.loads(response.text)
                Token = json_object["response"]["access_token"]
                return Token
            else:
                logger.error(
                    f"Failed to get Iamport token: {response.status_code}, {response.text}"
                )
                return None
        except requests.RequestException as ex:
            logger.error(f"Request to Iamport failed: {ex}")
            return None

    def verify_iamport_payment(self, imp_uid, amount, token):
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
    permission_classes = [IsAuthenticatedAndAllowed]
    authentication_classes = [JWTAuthentication]

    def get(self, request):
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
    해당 결제 정보 불러오기
    """

    permission_classes = [IsAuthenticatedAndAllowed]
    authentication_classes = [JWTAuthentication]

    def get(self, request, payment_id):
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
    환불 처리
    """

    permission_classes = [IsAuthenticatedAndAllowed]
    authentication_classes = [JWTAuthentication]

    def get_iamport_token(self):
        url = "https://api.iamport.kr/users/getToken"
        headers = {"Content-Type": "application/json"}
        data = {
            "imp_key": settings.IAMPORT["IMP_REST_API_KEY"],
            "imp_secret": settings.IAMPORT["IMP_SECRET"],
        }
        try:
            response = requests.post(url, data=json.dumps(data), headers=headers)
            response.raise_for_status()
            result = response.json()
            logger.info(f"아임포트 API 응답: {result}")  # 전체 응답 로깅
            if result.get("code") == 0:
                return result.get("response", {}).get("access_token")
            else:
                logger.error(f"아임포트 토큰 발급 실패: {result}")
                return None
        except requests.RequestException as e:
            # 기존 로깅 유지
            logger.error(
                f"아임포트 인증 실패. 사용된 IMP_KEY: {settings.IAMPORT['IMP_KEY']}"
            )
            logger.error(
                f"전체 응답 내용: {e.response.text if hasattr(e.response, 'text') else 'No response text'}"
            )
        return None

    def post(self, request, payment_id):
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

        try:
            access_token = self.get_iamport_token()
            if not access_token:
                return Response(
                    {"error": "결제 시스템 연결에 실패했습니다."},
                    status=status.HTTP_503_SERVICE_UNAVAILABLE,
                )

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
                error_message = refund_result.get(
                    "message", "환불 처리에 실패했습니다."
                )
                logger.error(f"Refund failed: {error_message}")
                return Response(
                    {"error": error_message}, status=status.HTTP_400_BAD_REQUEST
                )
        except Exception as e:
            payment.refund_status = "FAILED"
            payment.save()
            logger.exception(f"Exception during refund process: {str(e)}")
            return Response(
                {"error": "환불 처리 중 오류가 발생했습니다."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def request_refund(self, access_token, imp_uid, amount):
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
