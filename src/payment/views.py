from rest_framework import generics, status
from rest_framework.response import Response
from .serializers import PaymentCreateSerializer, PaymentSerializer


class PaymentCreateView(generics.CreateAPIView):
    # permission_classes = [IsAuthenticated]
    serializer_class = PaymentCreateSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        payment = serializer.save()
        return Response(PaymentSerializer(payment).data, status=status.HTTP_201_CREATED)
