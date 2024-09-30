from django.urls import path
from .views import PaymentInfoAPIView, PaymentCompleteAPIView

app_name = "payment"

urlpatterns = [
    path(
        "info/<int:major_category_id>/",
        PaymentInfoAPIView.as_view(),
        name="payment-info",
    ),
    path("complete/", PaymentCompleteAPIView.as_view(), name="payment-complete"),
]
