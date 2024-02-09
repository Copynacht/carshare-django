from django.urls import include, re_path
from django.contrib import admin
from main.urls import router
from . import settings
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = [
    re_path('admin/', admin.site.urls),
    re_path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    re_path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    re_path('user/', include('main.urls')),
    re_path('api/', include(router.urls)),
]

urlpatterns += staticfiles_urlpatterns()

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += (
        re_path(r'^debug_toolbar/', include(debug_toolbar.urls)),
    )
