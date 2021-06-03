from django.db import models

from django.db import models
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser, User, _user_has_perm
)
from django.utils.translation import ugettext_lazy as _
from django.core.validators import MinValueValidator
from django.utils import timezone


class AccountManager(BaseUserManager):
    def create_user(self, request_data, **kwargs):
        now = timezone.now()
        if not request_data['email']:
            raise ValueError('Users must have an email address.')

        profile = ""
        if request_data.get('profile'):
            profile = request_data['profile']

        user = self.model(
            username=request_data['username'],
            email=self.normalize_email(request_data['email']),
            is_active=True,
            last_login=now,
            date_joined=now,
            profile=profile
        )

        user.set_password(request_data['password'])
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password, **extra_fields):
        request_data = {
            'username': username,
            'email': email,
            'password': password
        }
        user = self.create_user(request_data)
        user.is_active = True
        user.is_staff = True
        user.is_admin = True
        user.save(using=self._db)
        return user


class Account(AbstractBaseUser):
    username = models.CharField(_('username'), max_length=30, unique=True)
    first_name = models.CharField(_('first name'), max_length=30, blank=True)
    last_name = models.CharField(_('last name'), max_length=30, blank=True)
    email = models.EmailField(
        verbose_name='email address', max_length=255, unique=True)
    profile = models.CharField(_('profile'), max_length=255, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    objects = AccountManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    def user_has_perm(user, perm, obj):
        return _user_has_perm(user, perm, obj)

    def has_perm(self, perm, obj=None):
        return _user_has_perm(self, perm, obj=obj)

    def has_module_perms(self, app_label):
        return self.is_admin

    def get_short_name(self):
        return self.first_name

    @property
    def is_superuser(self):
        return self.is_admin

    class Meta:
        db_table = 'api_user'
        swappable = 'AUTH_USER_MODEL'


class CarModel(models.Model):
    name = models.CharField(max_length=80)
    odometer = models.IntegerField(validators=[MinValueValidator(0)])
    description = models.CharField(max_length=100)
    per_use = models.IntegerField(validators=[MinValueValidator(0)])
    MISSION_CHOICES = (
        (0, "AT"),
        (1, "MT"),
    )
    mission = models.IntegerField(default=0, choices=MISSION_CHOICES)
    INSURANCE_CHOICES = (
        (0, "任意保険に加入済み"),
        (1, "１日保険に加入が必要"),
    )
    insurance = models.IntegerField(default=0, choices=INSURANCE_CHOICES)
    AVAILABLE_CHOICES = (
        (0, "利用可能"),
        (1, "利用不可能"),
    )
    available = models.IntegerField(default=0, choices=AVAILABLE_CHOICES)

    def __str__(self):
        return self.name


class ReservationModel(models.Model):
    user = models.ForeignKey(Account, db_column='account',
                             on_delete=models.SET_NULL,  blank=True, null=True)
    car = models.ForeignKey(CarModel, db_column='car',
                            on_delete=models.SET_NULL,  blank=True, null=True)
    start_date_time = models.DateTimeField(default=timezone.now)
    end_date_time = models.DateTimeField(default=timezone.now)
    start_odometer = models.IntegerField(validators=[MinValueValidator(0)])
    end_odometer = models.IntegerField(
        validators=[MinValueValidator(0)], default=0)
    STATUS_CHOICES = (
        (0, "予約中"),
        (1, "予約キャンセル"),
        (2, "返却"),
        (3, "事故")
    )
    status = models.IntegerField(default=0, choices=STATUS_CHOICES)
    pay = models.BooleanField(default=False)
