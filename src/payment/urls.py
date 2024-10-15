from django.urls import path

from .views import (
    PaymentInfoAPIView,
    PaymentCompleteAPIView,
    UserPaymentsView,
    RefundAPIView,
    PaymentDetailView,
)


urlpatterns = [
    path(
        "info/<int:major_category_id>/",
        PaymentInfoAPIView.as_view(),
        name="payment-info",
    ),
    path("complete/", PaymentCompleteAPIView.as_view(), name="payment-complete"),
    path("user-payments/", UserPaymentsView.as_view(), name="user-payments"),
    path(
        "detail/<int:payment_id>/", PaymentDetailView.as_view(), name="payment-detail"
    ),
    path("refund/<int:payment_id>/", RefundAPIView.as_view(), name="payment-refund"),
]
