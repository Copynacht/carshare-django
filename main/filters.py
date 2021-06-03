from django_filters import rest_framework as filters
from .models import ReservationModel


class ReservationFilter(filters.FilterSet):
    user = filters.NumberFilter(field_name='user', lookup_expr='exact')
    car = filters.NumberFilter(field_name='car', lookup_expr='exact')
    status = filters.NumberFilter(field_name='status', lookup_expr='exact')
    pay = filters.BooleanFilter(field_name='pay')

    class Meta:
        model = ReservationModel
        fields = ['user', 'car', 'status', 'pay']
