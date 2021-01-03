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
from django.conf.urls import url
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
from core.views import admin_poll_view, jwt_view
from core.admin import admin_view

admin.site.admin_view = admin_view

api_info = openapi.Info(
    title="Votechain Core API",
    default_version='v0.0.2',
    license=openapi.License(name="MIT License"),
)

schema_view = get_schema_view(
   api_info,
   public=True,
   permission_classes=(permissions.AllowAny,),
)

# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('admin/doc', include('django.contrib.admindocs.urls')),
    path('admin/login', page_not_found, kwargs={'exception': Exception('Page not Found')}),
    path('admin', admin.site.urls),
    path('auth', include('rest_framework.urls', namespace='rest_framework')),
    path('poll/<int:id>/start', admin_poll_view.AdminStartPoll.as_view(), name='admin_start_poll'),
    path('poll/<int:id>', admin_poll_view.AdminPoll.as_view(), name='admin_poll'),
    path('poll', admin_poll_view.AdminListOrCreatePoll.as_view(), name='admin_list_poll'),
    path(
        'poll/<int:poll_id>/candidate',
        admin_poll_view.AdminListOrAddCandidate.as_view(),
        name='admin_list_candidates'
    ),
    path(
        'poll/<int:poll_id>/candidate/<int:id>',
        admin_poll_view.AdminGetDeleteCandidate.as_view(),
        name='admin_get_delete_candidate'
    ),
    url(r'^swagger(?P<format>\.json|\.yaml)$',
        schema_view.without_ui(cache_timeout=0), name='schema-json'),
    url(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('auth/token', jwt_view.JwtAuthenticationView.as_view(), name='token_obtain'),
    path('auth/token/refresh', jwt_view.JwtRefreshView.as_view(), name='token_refresh'),
]
