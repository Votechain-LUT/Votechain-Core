"""Votechain URL Configuration

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
from django.views.defaults import page_not_found
from django.urls import path, include
from core.views import admin_poll_view
from core.admin import admin_view

admin.site.admin_view = admin_view

# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('admin/doc/', include('django.contrib.admindocs.urls')),
    path('admin/login/', page_not_found, kwargs={'exception': Exception('Page not Found')}),
    path('admin/', admin.site.urls),
    path('auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('poll/create/', admin_poll_view.AdminCreatePoll.as_view(), name='admin_create_poll'),
    path('poll/start/', admin_poll_view.AdminStartPoll.as_view(), name='admin_start_poll'),
    path('poll/<int:pk>/', admin_poll_view.AdminPoll.as_view(), name='admin_poll'),
    path('poll/list/', admin_poll_view.AdminListPoll.as_view(), name='admin_list_poll'),
]
