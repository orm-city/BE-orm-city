import requests
import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from .models import MajorCategory, Payment
from django.conf import settings
from django.db import transaction
from django.core.exceptions import ValidationError, ObjectDoesNotExist
import json


class PaymentInfoAPIView(APIView):
    """
    결제 정보를 제공하는 API 뷰
    """

    permission_classes = [AllowAny]

    def get(self, request, major_category_id):
        try:
            major_category = MajorCategory.objects.get(id=major_category_id)
            user = request.user
            data = {
                "major_category_id": major_category.id,
                "major_category_name": major_category.name,
                "major_category_price": major_category.price,
                "username": user.username,
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
            # 여기까진 문제가 없어야 맞는데 말이죠
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
        user = request.user
        imp_uid = request.data.get("imp_uid")
        merchant_uid = request.data.get("merchant_uid")
        major_category_id = request.data.get("major_category_id")
        total_amount = request.data.get("total_amount")

        if not all([imp_uid, merchant_uid, major_category_id, total_amount]):
            raise ValidationError("필수 결제 정보가 누락되었습니다.")

        logger.info(f"결제 요청 수신: {request.data}")

        try:
            major_category = MajorCategory.objects.get(id=major_category_id)
        except ObjectDoesNotExist:
            logger.error(f"해당 강의를 찾을 수 없음: id={major_category_id}")
            raise ValidationError("해당 강의를 찾을 수 없습니다.")

        # 중복 결제 확인
        if Payment.objects.filter(imp_uid=imp_uid).exists():
            logger.warning(f"중복 결제 시도: imp_uid={imp_uid}")
            raise ValidationError("이미 처리된 결제입니다.")

        iamport_token = self.get_iamport_token()
        if iamport_token:
            self.verify_iamport_payment(imp_uid, total_amount, iamport_token)
        else:
            logger.info(f"{iamport_token}")

        payment = Payment.objects.create(
            user=user,
            major_category=major_category,
            total_amount=total_amount,
            merchant_uid=merchant_uid,
            payment_status="paid",
            receipt_url=f"https://api.iamport.kr/payments/{imp_uid}",
            imp_uid=imp_uid,
        )
        logger.info(f"결제 정보 생성 완료: id={payment.id}")

        return Response(
            {
                "message": "결제가 성공적으로 완료되었습니다.",
                "payment_id": payment.id,
                "status": payment.payment_status,
            },
            status=status.HTTP_201_CREATED,
        )


# class PaymentCompleteAPIView(APIView):
#     permission_classes = [AllowAny]
#     http_method_names = ['post', 'options']

#     def get_iamport_token(self):
#         url = "https://api.iamport.kr/users/getToken"
#         headers = {
#             "Content-Type": "application/json",
#             "charset": "UTF-8",
#             "Accept": "*/*",
#         }
#         body = {
#             "imp_key": settings.IAMPORT["IMP_KEY"],
#             "imp_secret": settings.IAMPORT["IMP_SECRET"],
#         }
#         try:
#             response = requests.post(
#                 url,
#                 headers=headers,
#                 data=json.dumps(body, ensure_ascii=False, indent="\t"),
#             )
#             return response
#         except Exception as ex:
#             print(ex)

#     def verify_iamport_payment(self, imp_uid, amount, token):
#         url = f"https://api.iamport.kr/payments/{imp_uid}"
#         headers = {
#             "Content-Type": "application/json",
#             "Authorization": f"Bearer {token}",
#         }
#         response = requests.get(url, headers=headers)

#         if response.status_code != 200:
#             logger.error(f"Failed to call Iamport API: status_code={response.status_code}, response={response.text}")
#             return False

#         try:
#             payment_data = response.json()
#         except ValueError as e:
#             logger.error(f"Error parsing Iamport API response: {e}")
#             return False

#         logger.info(f"Iamport payment data: {payment_data}")

#         if payment_data["code"] == 0:
#             if "response" not in payment_data:
#                 logger.error(f"No response key in Iamport API response: {payment_data}")
#                 return False

#             iamport_amount = int(payment_data["response"]["amount"])
#             iamport_status = payment_data["response"]["status"]
#             logger.info(
#                 f"Verification check: status={iamport_status}, amount={iamport_amount} vs {amount}"
#             )
#             return iamport_status == "paid" and iamport_amount == int(amount)
#         else:
#             logger.error(f"Failed to get payment data from Iamport: {payment_data}")
#             return False

#     def post(self, request):
#         user = request.user
#         imp_uid = request.data.get("imp_uid")
#         merchant_uid = request.data.get("merchant_uid")
#         major_category_id = request.data.get("major_category_id")
#         total_amount = request.data.get("total_amount")
#         # receipt_url = request.data.get("receipt_url")

#         logger.info(f"Payment request received: {request.data}")

#         try:
#             major_category = MajorCategory.objects.get(id=major_category_id)
#         except MajorCategory.DoesNotExist:
#             logger.error(f"MajorCategory not found: id={major_category_id}")
#             return Response(
#                 {"error": "해당 강의를 찾을 수 없습니다."},
#                 status=status.HTTP_404_NOT_FOUND,
#             )

#         iamport_token = self.get_iamport_token()
#         if not iamport_token:
#             return Response(
#                 {"error": "아임포트 인증에 실패했습니다."},
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             )

#         if self.verify_iamport_payment(imp_uid, total_amount, iamport_token):
#             payment = Payment.objects.create(
#                 username=user,
#                 major_category=major_category,
#                 total_amount=total_amount,
#                 merchant_uid=merchant_uid,
#                 payment_status="paid",
#                 receipt_url=f"https://api.iamport.kr/payments/{imp_uid}",
#                 imp_uid=imp_uid,
#             )
#             logger.info(f"Payment created successfully: id={payment.id}")
#             return Response(
#                 {
#                     "message": "결제가 성공적으로 완료되었습니다.",
#                     "payment_id": payment.id,
#                     "status": payment.payment_status,
#                 },
#                 status=status.HTTP_201_CREATED,
#             )
#         else:
#             logger.warning(f"Payment verification failed: imp_uid={imp_uid}")
#             return Response(
#                 {"error": "결제 검증에 실패했습니다."},
#                 status=status.HTTP_400_BAD_REQUEST,
#             )
