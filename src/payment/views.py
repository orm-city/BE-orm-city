from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import MajorCategory
from django.conf import settings


class PaymentCreateView(generics.CreateAPIView):
    # permission_classes = [IsAuthenticated]
    serializer_class = PaymentCreateSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        payment = serializer.save()
        return Response(PaymentSerializer(payment).data, status=status.HTTP_201_CREATED)
      
class PaymentInfoAPIView(APIView):
    """
    결제할 강의의 정보를 전달
    """

    def get(self, request, major_category_id):
        try:
            major_category = MajorCategory.objects.get(id=major_category_id)
            data = {
                "major_category_name": major_category.name,
                "major_category_price": major_category.price,
                "imp_key": settings.IMP_KEY,  # settings.py에서 IMP_CODE 가져오기
            }
            return Response(data, status=status.HTTP_200_OK)
        except MajorCategory.DoesNotExist:
            return Response(
                {"error": "해당 강의를 찾을 수 없습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )


# # 결제 완료 후 정보를 처리하는 API
# class PaymentCompleteAPIView(APIView):
#     def post(self, request):
#         imp_uid = request.data.get('imp_uid')
#         merchant_uid = request.data.get('merchant_uid')
#         major_category_id = request.data.get('major_category_id')
#         total_amount = request.data.get('total_amount')

#         # 아임포트 결제 정보를 검증
#         access_token = get_iamport_token()
#         payment_data = get_payment_data(imp_uid, access_token)

#         if payment_data and payment_data['status'] == 'paid' and payment_data['amount'] == total_amount:
#             # 결제가 성공적으로 완료되었으면 DB에 저장
#             try:
#                 major_category = MajorCategory.objects.get(id=major_category_id)
#                 payment = Payment.objects.create(
#                     user=request.user,
#                     major_category=major_category,
#                     total_amount=total_amount,
#                     payment_status='COMPLETED',
#                     receipt_url=payment_data.get('receipt_url', ''),
#                 )
#                 return Response({'status': 'success', 'message': '결제 정보가 저장되었습니다.'}, status=status.HTTP_201_CREATED)
#             except MajorCategory.DoesNotExist:
#                 return Response({'status': 'failed', 'message': '강의를 찾을 수 없습니다.'}, status=status.HTTP_404_NOT_FOUND)
#         else:
#             return Response({'status': 'failed', 'message': '결제 검증 실패'}, status=status.HTTP_400_BAD_REQUEST)





