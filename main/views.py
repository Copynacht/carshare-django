import datetime
import tempfile
import csv
from rest_framework.viewsets import generics, ModelViewSet
from rest_framework import viewsets, mixins
from .models import CarModel, ReservationModel, Account
from rest_framework.permissions import IsAdminUser, IsAuthenticated, AllowAny
from .serializers import CarSerializer, ReservationSerializer, AccountSerializer
from .filters import ReservationFilter
from django.db import transaction
from rest_framework.response import Response
from django.db.models import Q
from rest_framework import status
from rest_framework.decorators import action
from datetime import timezone, timedelta
from django.http import Http404, FileResponse
from django_filters.rest_framework import DjangoFilterBackend

JST = timezone(timedelta(hours=+9), 'JST')

# ユーザ作成のView(POST)
class AccountRegister(generics.CreateAPIView):
    permission_classes = (AllowAny,)
    queryset = Account.objects.all()
    serializer_class = AccountSerializer

    @transaction.atomic
    def post(self, request, format=None):
        serializer = AccountSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ユーザ情報取得のView(GET)
class UserMyPage(generics.RetrieveUpdateAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = Account.objects.all()
    serializer_class = AccountSerializer
    lookup_field = 'email'

    def get_object(self):
        try:
            instance = self.queryset.get(id=self.request.user.id)
            return instance
        except Account.DoesNotExist:
            raise Http404

    def retrieve(self, request, format=None):
        return Response(data={
            'id': request.user.id,
            'username': request.user.username,
            'email': request.user.email,
        },
            status=status.HTTP_200_OK)


class AccountListView(mixins.ListModelMixin,
                      viewsets.GenericViewSet):
    permission_classes = (IsAdminUser,)
    queryset = Account.objects.all()
    serializer_class = AccountSerializer


class CarViewSet(ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = CarModel.objects.all()
    serializer_class = CarSerializer


class ReservationViewSet(mixins.ListModelMixin,
                         mixins.RetrieveModelMixin,
                         mixins.CreateModelMixin,
                         mixins.UpdateModelMixin,
                         viewsets.GenericViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = ReservationModel.objects.all()
    serializer_class = ReservationSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = ReservationFilter

    def get_queryset(self):
        q = super(ReservationViewSet, self).get_queryset().order_by('-start_date_time')
        if(self.request.query_params.get('my', None)):
            return q.filter(user=self.request.user.id)
        return q

    def create(self, request, pk=None):
        u = request.user.id
        c = request.data['car_uid']
        sdt = request.data['start_date_time']
        edt = request.data['end_date_time']
        if sdt < datetime.datetime.now(JST).strftime("%Y-%m-%dT%H:%M:%S%z"):
            return Response('利用開始時刻が現在時刻より早いです',
                            status=status.HTTP_400_BAD_REQUEST)
        if sdt > edt:
            return Response('利用開始時刻が返却時刻より早いです',
                            status=status.HTTP_400_BAD_REQUEST)
        if sdt == edt:
            return Response('利用開始時刻と返却時刻が同じです',
                            status=status.HTTP_400_BAD_REQUEST)
        duplicate = ReservationModel.objects.all().filter(car__id=c).filter(status=0).filter(Q(start_date_time__lte=sdt) & Q(
            end_date_time__gte=edt) | Q(start_date_time__gte=sdt) & Q(
            start_date_time__lte=edt) | Q(end_date_time__gte=sdt) & Q(end_date_time__lte=edt)).distinct().count()
        if duplicate == 0:
            serializer = ReservationSerializer(data={'user_uid': u, 'car_uid': c, 'start_date_time': sdt,
                                                     'end_date_time': edt, 'start_odometer': 0, 'end_odometer': 0, 'status': 0})
            if serializer.is_valid():
                serializer.save()
                return Response(status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors,
                                status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response('予約が重複しています',
                            status=status.HTTP_400_BAD_REQUEST)

    @ action(detail=True, methods=["patch"])
    def returncar(self, request, pk=None):
        so = request.data["start_odometer"]
        eo = request.data["end_odometer"]
        if int(eo) < int(so):
            return Response('利用開始前距離が返却後距離より長いです',
                            status=status.HTTP_400_BAD_REQUEST)
        if request.method == 'PATCH':
            reservation = self.get_object()
            if reservation.user == request.user:
                serializer = ReservationSerializer(
                    reservation, data={'status': 2, 'start_odometer': so, 'end_odometer': eo}, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    rewrite = CarModel.objects.get(id=reservation.car.id)
                    if rewrite.odometer > int(so):
                        return Response('利用開始前距離が車に記録されている距離より短いです',
                                        status=status.HTTP_400_BAD_REQUEST)
                    rewrite.per_use = rewrite.per_use + 1
                    rewrite.odometer = eo
                    rewrite.save()
                    return Response(status=status.HTTP_200_OK)
                else:
                    return Response('エラーが発生しました', status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response('異なるユーザーの予約です', status=status.HTTP_400_BAD_REQUEST)

    @ action(detail=True, methods=["patch"])
    def change(self, request, pk=None):
        if request.method == 'PATCH':
            sdt = request.data["start_date_time"]
            edt = request.data["end_date_time"]
            if sdt < datetime.datetime.now(JST).strftime("%Y-%m-%dT%H:%M:%S%z"):
                return Response('利用開始時刻が現在時刻より早いです',
                                status=status.HTTP_400_BAD_REQUEST)
            if sdt > edt:
                return Response('利用開始時刻が返却時刻より早いです',
                                status=status.HTTP_400_BAD_REQUEST)
            if sdt == edt:
                return Response('利用開始時刻と返却時刻が同じです',
                                status=status.HTTP_400_BAD_REQUEST)
            reservation = self.get_object()
            if reservation.user == request.user:
                duplicate = ReservationModel.objects.all().exclude(id=reservation.id).filter(car=reservation.car).filter(status=0).filter(Q(start_date_time__lte=sdt) & Q(
                    end_date_time__gte=edt) | Q(start_date_time__gte=sdt) & Q(
                    start_date_time__lte=edt) | Q(end_date_time__gte=sdt) & Q(end_date_time__lte=edt)).distinct().count()
                if duplicate == 0:
                    serializer = ReservationSerializer(
                        reservation, data={'start_date_time': sdt, 'end_date_time': edt}, partial=True)
                    if serializer.is_valid():
                        serializer.save()
                        return Response(status=status.HTTP_200_OK)
                    else:
                        return Response('エラーが発生しました', status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response('予約が重複しています',
                                    status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response('異なるユーザーの予約です', status=status.HTTP_400_BAD_REQUEST)

    @ action(detail=True, methods=["patch"])
    def cancel(self, request, pk=None):
        reservation = self.get_object()
        if request.method == 'PATCH':
            if reservation.user == request.user:
                if reservation.start_date_time > datetime.datetime.now(JST):
                    serializer = ReservationSerializer(
                        reservation, data={'status': 1}, partial=True)
                    if serializer.is_valid():
                        serializer.save()
                        return Response(status=status.HTTP_200_OK)
                    else:
                        return Response('エラーが発生しました', status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response('利用開始時間を過ぎているのでキャンセルできません。予約を変更するか、返却してください。', status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response('異なるユーザーの予約です', status=status.HTTP_400_BAD_REQUEST)

class ReservationCsvExport(viewsets.ModelViewSet):
    permission_classes = (AllowAny,)
    queryset = ReservationModel.objects.all()
    serializer_class = ReservationSerializer
    filter_class = ReservationFilter
    
    @action(methods=["get"], detail=False)
    def csv_export(self, request):
        queryset = super(ReservationCsvExport, self).get_queryset().order_by('-start_date_time')
        file = self._create_export_customer_csv(queryset)
        filename = (
            "MMT予約データ.csv"
        )
        response = FileResponse(
            open(file.name, "rb"),
            as_attachment=True,
            content_type="application/csv",
            filename=filename,
        )
        return response

    def _create_export_customer_csv(self, reservations):
        file = tempfile.NamedTemporaryFile(delete=False)
        with open(file.name, "w") as csvfile:
            fieldnames = [
                "名前",
                "車種",
                "開始日時",
                "返却日時",
                "走行距離",
                "返却ステータス",
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for r in reservations:
                status = ""
                if r.status == 0:
                    status = "予約中"
                if r.status == 1:
                    status = "予約キャンセル"
                if r.status == 2:
                    status = "返却"
                if r.status == 3:
                    status = "事故"
                if r.user == None:
                    continue
                writer.writerow(
                    {
                        "名前": r.user.username,
                        "車種": r.car.name,
                        "開始日時": r.start_date_time,
                        "返却日時": r.end_date_time,
                        "走行距離": r.end_odometer-r.start_odometer,
                        "返却ステータス": status
                    }
                )

        file.seek(0)
        return file
