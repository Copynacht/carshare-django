import django_filters
from .models import ReservationModel


class ReservationFilter(django_filters.FilterSet):
    user = django_filters.NumberFilter(field_name='user__id', lookup_expr='exact')
    car = django_filters.NumberFilter(field_name='car__id', lookup_expr='exact')
    status = django_filters.NumberFilter(field_name='status', lookup_expr='exact')
    pay = django_filters.BooleanFilter(field_name='pay')

    class Meta:
        model = ReservationModel
        fields = ['user', 'car', 'status', 'pay']
