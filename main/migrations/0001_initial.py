# Generated by Django 3.0.6 on 2021-06-01 08:27

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Account',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('username', models.CharField(max_length=30, unique=True, verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=30, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=30, verbose_name='last name')),
                ('email', models.EmailField(max_length=255, unique=True, verbose_name='email address')),
                ('profile', models.CharField(blank=True, max_length=255, verbose_name='profile')),
                ('is_active', models.BooleanField(default=True)),
                ('is_staff', models.BooleanField(default=False)),
                ('is_admin', models.BooleanField(default=False)),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
            ],
            options={
                'db_table': 'api_user',
                'swappable': 'AUTH_USER_MODEL',
            },
        ),
        migrations.CreateModel(
            name='CarModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=80)),
                ('odometer', models.IntegerField(validators=[django.core.validators.MinValueValidator(0)])),
                ('description', models.CharField(max_length=100)),
                ('per_use', models.IntegerField(validators=[django.core.validators.MinValueValidator(0)])),
                ('mission', models.IntegerField(choices=[(0, 'AT'), (1, 'MT')], default=0)),
                ('insurance', models.IntegerField(choices=[(0, '任意保険に加入済み'), (1, '１日保険に加入が必要')], default=0)),
            ],
        ),
        migrations.CreateModel(
            name='ReservationModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_date_time', models.DateTimeField(default=django.utils.timezone.now)),
                ('end_date_time', models.DateTimeField(default=django.utils.timezone.now)),
                ('start_odometer', models.IntegerField(validators=[django.core.validators.MinValueValidator(0)])),
                ('end_odometer', models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0)])),
                ('status', models.IntegerField(choices=[(0, '予約中'), (1, '予約キャンセル'), (2, '利用中'), (3, '返却'), (4, '事故')], default=0)),
                ('car', models.ForeignKey(blank=True, db_column='car', null=True, on_delete=django.db.models.deletion.SET_NULL, to='main.CarModel')),
                ('user', models.ForeignKey(blank=True, db_column='account', null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
