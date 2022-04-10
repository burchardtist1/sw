from django.urls import path

from characters import views

urlpatterns = [
    path("", views.CollectionView.as_view(), name="collections"),
    path("count", views.CountView.as_view(), name="count"),
    path("<pk>/", views.CollectionDetailsView.as_view(), name="collection-details"),
    path("download/<pk>/", views.DownloadCSVView.as_view(), name="download"),
    path("list/<pk>/", views.CharactersView.as_view(), name="characters"),
]
