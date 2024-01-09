from django.urls import path

from . import views

app_name = "analyzer"

urlpatterns = [
    path("", views.upload_file, name="index"),
    path("uploaded", views.uploaded, name="uploaded"),
    path("report", views.report, name="report"),
]