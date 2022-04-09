from django.urls import path

from characters import views

urlpatterns = [
    path("", views.CollectionView.as_view(), name="collections"),
    path("count", views.CountView.as_view(), name="count"),
]
