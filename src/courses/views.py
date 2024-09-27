from rest_framework import generics
from .models import MajorCategory
from .serializers import MajorCategorySerializer


class MajorCategoryListView(generics.ListAPIView):
    queryset = MajorCategory.objects.all()
    serializer_class = MajorCategorySerializer
