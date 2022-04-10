"""sw URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import include, path

from sw.html import collection_count, collection_details, collection_list, index

urlpatterns = [
    path("api/characters/", include("characters.urls")),
]

html_patterns = [
    path("", index),
    path("html/", collection_list, name="html-collections"),
    path("html/collection/<int:pk>/", collection_details),
    path("html/count/<int:pk>/", collection_count),
]

urlpatterns += html_patterns
