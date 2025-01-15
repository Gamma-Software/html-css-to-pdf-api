from django.urls import path
from . import views

urlpatterns = [
    path("html-to-pdf/", views.ConvertToPDFView.as_view(), name="html-to-pdf"),
    path("svg-to-png/", views.convert_svg_to_png, name="svg-to-png"),
]
