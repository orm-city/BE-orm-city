import requests
import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from .models import MajorCategory, Payment
from django.conf import settings
import json


class PaymentInfoAPIView(APIView):
    """
    결제 정보를 제공하는 API 뷰

    """

    permission_classes = [AllowAny]

    def get(self, request, major_category_id):
        try:
            major_category = MajorCategory.objects.get(id=major_category_id)
            data = {
                "major_category_id": major_category.id,
                "major_category_name": major_category.name,
                "major_category_price": major_category.price,
                "imp_key": settings.IAMPORT["IMP_KEY"],
            }
            return Response(data, status=status.HTTP_200_OK)
        except MajorCategory.DoesNotExist:
            return Response(
                {"error": "해당 강의를 찾을 수 없습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )


logger = logging.getLogger(__name__)


class PaymentCompleteAPIView(APIView):
    permission_classes = [AllowAny]

    def get_iamport_token(self):
        url = "https://api.iamport.kr/users/getToken"
        headers = {
            "Content-Type": "application/json",
            "charset": "UTF-8",
            "Accept": "*/*",
        }
        body = {
            "imp_key": settings.IAMPORT["IMP_SECRET"],
            "imp_secret": settings.IAMPORT["IMP_SECRET"],
        }
        try:
            response = requests.post(
                url,
                headers=headers,
                data=json.dumps(body, ensure_ascii=False, indent="\t"),
            )
            return response
        except Exception as ex:
            print(ex)

    def verify_iamport_payment(self, imp_uid, amount, token):
        url = f"https://api.iamport.kr/payments/{imp_uid}"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        }
        response = requests.get(url, headers=headers)
        payment_data = response.json()
        logger.info(f"Iamport payment data: {payment_data}")

        if payment_data["code"] == 0:
            iamport_amount = payment_data["response"]["amount"]
            iamport_status = payment_data["response"]["status"]
            logger.info(
                f"Verification check: status={iamport_status}, amount={iamport_amount} vs {amount}"
            )
            return iamport_status == "paid" and iamport_amount == int(amount)
        else:
            logger.error(f"Failed to get payment data from Iamport: {payment_data}")
            return False

    def post(self, request):
        user = request.user
        imp_uid = request.data.get("imp_uid")
        merchant_uid = request.data.get("merchant_uid")
        major_category_id = request.data.get("major_category_id")
        total_amount = request.data.get("total_amount")

        logger.info(f"Payment request received: {request.data}")

        try:
            major_category = MajorCategory.objects.get(id=major_category_id)
        except MajorCategory.DoesNotExist:
            logger.error(f"MajorCategory not found: id={major_category_id}")
            return Response(
                {"error": "해당 강의를 찾을 수 없습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )

        iamport_token = self.get_iamport_token()
        if not iamport_token:
            return Response(
                {"error": "아임포트 인증에 실패했습니다."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        if self.verify_iamport_payment(imp_uid, total_amount, iamport_token):
            payment = Payment.objects.create(
                user=user,
                major_category=major_category,
                total_amount=total_amount,
                merchant_uid=merchant_uid,
                payment_status="paid",
                receipt_url=f"https://api.iamport.kr/payments/{imp_uid}",
            )
            logger.info(f"Payment created successfully: id={payment.id}")
            return Response(
                {
                    "message": "결제가 성공적으로 완료되었습니다.",
                    "payment_id": payment.id,
                    "status": payment.payment_status,
                },
                status=status.HTTP_201_CREATED,
            )
        else:
            logger.warning(f"Payment verification failed: imp_uid={imp_uid}")
            return Response(
                {"error": "결제 검증에 실패했습니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )
