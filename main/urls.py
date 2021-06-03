from django.conf.urls import url
from rest_framework import routers
from .views import AccountRegister, UserMyPage, CarViewSet, ReservationViewSet

router = routers.DefaultRouter()
router.register(r'car', CarViewSet)
router.register(r'reservation', ReservationViewSet)

urlpatterns = [
    url(r'^register/$', AccountRegister.as_view()),
    url(r'^mypage/$', UserMyPage.as_view()),
]
