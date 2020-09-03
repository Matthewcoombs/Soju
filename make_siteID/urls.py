
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_page, name="home_page"),
    path('create/<int:userID>/', views.create_global_siteID, name="globalID_interface")
]