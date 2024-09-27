from django.urls import path
from .views import PaymentInfoAPIView,PaymentCreateView

app_name = "payment"

urlpatterns = [
    path("create/", PaymentCreateView.as_view(), name="payment-create"),
    path(
        "info/<int:major_category_id>/",
        PaymentInfoAPIView.as_view(),
        name="payment-info",
    ),
]
