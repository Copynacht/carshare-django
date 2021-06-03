from django.contrib import admin
from .models import Account, CarModel, ReservationModel

admin.site.title = '管理画面'
admin.site.site_header = 'シェアカー管理'
admin.site.index_title = 'メニュー'


class AccountAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'password', 'is_staff',
                    'is_active', 'is_admin', 'date_joined')


class CarAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'odometer',
                    'per_use', 'mission', 'insurance', 'available')


class ReservationAdmin(admin.ModelAdmin):
    list_display = ('user', 'car', 'start_date_time', 'pay',
                    'end_date_time', 'start_odometer', 'end_odometer', 'status')


admin.site.register(Account, AccountAdmin)
admin.site.register(CarModel, CarAdmin)
admin.site.register(ReservationModel, ReservationAdmin)
