# Generated by Django 3.0.6 on 2021-06-03 23:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_auto_20210602_0331'),
    ]

    operations = [
        migrations.AddField(
            model_name='reservationmodel',
            name='pay',
            field=models.BooleanField(default=False),
        ),
    ]
