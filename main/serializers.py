from rest_framework import serializers
from .models import Account, CarModel, ReservationModel


class AccountSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = Account
        fields = ('username', 'email', 'password')

    def create(self, validated_data):
        return Account.objects.create_user(request_data=validated_data)


class CarSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarModel
        read_only_fields = ['id', 'name', 'description',
                            'odometer', 'per_use', 'mission', 'insurance']
        fields = ('id', 'name', 'description', 'odometer',
                  'per_use', 'mission', 'insurance', 'available')


class ReservationSerializer(serializers.ModelSerializer):
    user = AccountSerializer(read_only=True)
    car = CarSerializer(read_only=True)
    user_uid = serializers.PrimaryKeyRelatedField(
        queryset=Account.objects.all(), write_only=True)
    car_uid = serializers.PrimaryKeyRelatedField(
        queryset=CarModel.objects.all(), write_only=True)

    class Meta:
        model = ReservationModel
        read_only_fields = ['id', ]
        fields = ('id', 'user', 'user_uid', 'car', 'car_uid', 'start_date_time',
                  'end_date_time', 'start_odometer', 'end_odometer', 'status')

    def create(self, validated_date):
        validated_date['user'] = validated_date.get('user_uid', None)
        validated_date['car'] = validated_date.get('car_uid', None)

        if validated_date['user'] is None:
            raise serializers.ValidationError("user not found.")

        if validated_date['car'] is None:
            raise serializers.ValidationError("car not found.")

        del validated_date['user_uid']
        del validated_date['car_uid']

        return ReservationModel.objects.create(**validated_date)
