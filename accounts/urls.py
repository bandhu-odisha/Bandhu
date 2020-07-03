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

    path('login/', views.login_view, name="login"),
    path('signup/', views.signup_view,name="signup"),
    path('activate/<slug:uidb64>/<slug:token>/', views.account_activation, name='account_activation'),
    path('authenticate/<slug:uidb64>/<slug:token>/', views.account_authentication, name='account_authentication'),
    path('delete/<slug:uidb64>/<slug:token>/', views.account_deletion, name='account_deletion'),
    path('delete/<slug:uidb64>/confirmed/', views.account_deletion_confirmed, name='account_deletion_confirmed'),

    path('signup/success/', views.signup_success,name="signup_success_page"),   # User Signup Complete
    path('activated/', views.account_activated,name="account_activated"),   # User Activation Complete
    path('authenticated/', views.account_authenticated,name="account_authenticated"),   # User Authentication Complete
    path('deleted/', views.account_deleted,name="account_deleted"),   # User Authentication Complete

    
    # Django Auth Urls
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('password_change/', auth_views.PasswordChangeView.as_view(), name='password_change'),
    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(), name='password_change_done'),
    path('password_reset/', auth_views.PasswordResetView.as_view(html_email_template_name='registration/password_reset_email.html'), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]
