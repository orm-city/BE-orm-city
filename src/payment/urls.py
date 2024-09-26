from django.urls import path
from .views import PaymentCreateView

app_name = "payment"

urlpatterns = [
    path("create/", PaymentCreateView.as_view(), name="payment-create"),
]
