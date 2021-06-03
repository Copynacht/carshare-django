from django.conf.urls import include, url
from django.contrib import admin
from main.urls import router
from . import settings
from rest_framework_jwt.views import obtain_jwt_token
from django.contrib.staticfiles.urls import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^login/', obtain_jwt_token),
    url(r'^user/', include('main.urls')),
    url(r'^api/', include(router.urls)),
]

urlpatterns += staticfiles_urlpatterns()

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += (
        url(r'^debug_toolbar/', include(debug_toolbar.urls)),
    )
