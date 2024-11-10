from django.contrib import admin
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("signup/", views.sign_up, name="signup"),
    path("add_app/", views.add_app, name="add_app"),
    path("delete_app/<int:appliance_id>/", views.delete_app, name="delete_app"),
    path("update_app/<int:appliance_id>/", views.update_app, name="update_app"),
    path("toggle_status/<int:appliance_id>/", views.toggle_status, name="toggle_status"),

    path("powercalculation/", views.power_calculation, name="power_calculation"),
    path("dashboard/", views.dashboard, name="dashboard"),
]


