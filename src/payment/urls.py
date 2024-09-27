from django.urls import path
from .views import PaymentInfoAPIView

urlpatterns = [
    path(
        "info/<int:major_category_id>/",
        PaymentInfoAPIView.as_view(),
        name="payment-info",
    ),
    # path("complete/", PaymentCompleteAPIView.as_view(), name="payment-complete"),  # 결제 완료 처리
]
