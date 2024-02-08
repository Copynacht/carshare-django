from django.urls import re_path
from rest_framework import routers
from .views import AccountRegister, UserMyPage, CarViewSet, ReservationViewSet, AccountListView

router = routers.DefaultRouter()
router.register('car', CarViewSet)
router.register('reservation', ReservationViewSet)
router.register('user', AccountListView)

urlpatterns = [
    re_path('register', AccountRegister.as_view()),
    re_path('mypage', UserMyPage.as_view()),
]
