from django.urls import path
from .views import MajorCategoryListView

urlpatterns = [
    path(
        "major-categories/", MajorCategoryListView.as_view(), name="major-category-list"
    ),
]
