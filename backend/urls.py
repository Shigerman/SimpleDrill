"""backend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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
from django.urls import path
from backend.app import views

app_name = 'app'

urlpatterns = [
    path('', views.homepage),
    path('register_visitor/', views.register_visitor, name='register-visitor'),
    path('view_invites/', views.view_invites, name='view-invites'),
    path('add_invite/', views.add_invite, name='add-invite'),
    path('login_visitor/', views.login_visitor, name='login-visitor'),
    path('logout_visitor/', views.logout_visitor, name='logout-visitor'),
    path('about/', views.about, name='about'),
    path('select_topic/', views.select_topic, name='select-topic'),
    path('drill_topic/', views.drill_topic, name='drill-topic'),
    path('explain_test/', views.explain_test, name='explain-test'),
    path('test/', views.test, name='test'),
    path('admin/', admin.site.urls),
]
