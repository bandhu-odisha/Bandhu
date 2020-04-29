"""genesisportal URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
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
from django.contrib import admin
from django.urls import path,include
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [

    path('login/', views.login, name="login"),
    path('signup/', views.signup,name="signup"),
    path('activate/<slug:uidb64>/<slug:token>/', views.activate, name='activate'),
    path('authenticate/<slug:uidb64>/<slug:token>/', views.authenticate, name='authenticate'),

    path('activated/', views.activated,name="activated"),   # User Activation Complete
    path('authenticated/', views.authenticated,name="authenticated"),   # User Authentication Complete

    path('signup/success/', views.signup_success,name="signup_success_page"),
    path('signup/failure/', views.signup_failure,name="signup_failure_page"),
    
    # Django Auth Urls
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('password_change/', auth_views.PasswordChangeView.as_view(), name='password_change'),
    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(), name='password_change_done'),
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]
