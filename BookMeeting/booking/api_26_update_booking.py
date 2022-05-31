from django.conf import settings
from room_and_group.models import Room, Group
from .models import Booking
from events.models import Event
from users.models import CustomUser
from users.serializers import CustomUserSerializer
from rest_framework import serializers, status
from rest_framework.decorators import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Q
from datetime import datetime
from django.utils import timezone
import jwt


def checkBookings(list_booking,
                  new_room, booking_id):  # [booking1, booking2, ...]   booking1{start_time: "", end_time: ""} room: ""
    data_vali = list()
    for booking_datetime in list_booking:
        if len(data_vali) != 0:
            return data_vali
        data_vali += Booking.objects.filter(
            ~Q(status=-1) &
            ~Q(id=booking_id) &
            Q(room=new_room) &
            # time_from > start_time và < end_time
            (Q(time_from__gte=booking_datetime['start_time'], time_from__lte=booking_datetime['end_time']) |
             # time_to > start_time và end_time
             Q(time_to__gte=booking_datetime['start_time'], time_to__lte=booking_datetime['end_time']) |
             # start_time > time_from và < time_to
             Q(time_from__gte=booking_datetime['start_time'], time_to__lte=booking_datetime['start_time']) |
             # end_time > time_from và < time_to
             Q(time_from__gte=booking_datetime['end_time'], time_to__lte=booking_datetime['end_time']) |
             Q(time_from__lte=booking_datetime['start_time'], time_to__gte=booking_datetime['end_time'])
             ))
    return data_vali


class serializer_update_booking(serializers.Serializer):
    email = serializers.EmailField(max_length=254,required=False)
    time_from = serializers.TimeField(required=False)
    time_to = serializers.TimeField(required=False)
    group = serializers.CharField(required=False)
    room = serializers.CharField(max_length=50, required=False)
    booking_status = serializers.IntegerField(required=False)
    date = serializers.DateField()


class Booking_update(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk, format=None):

        token_decode = jwt.decode(request.META['HTTP_AUTHORIZATION'].split(' ')[1], settings.SECRET_KEY,
                                  algorithms=["HS256"])

        booking = Booking.objects.get(id=pk)
        if booking is None:
            return Response({
                'status': False,
                "error": {
                    "code": status.HTTP_400_BAD_REQUEST,
                    "message": "Booking not found!"
                }
            }, status=status.HTTP_400_BAD_REQUEST)
        else:
            data_input = serializer_update_booking(data=request.data)
            if not data_input.is_valid():
                return Response({
                    'status': False,
                    "error": {
                        "code": status.HTTP_400_BAD_REQUEST,
                        "message": "Missing information!"
                    }
                }, status=status.HTTP_400_BAD_REQUEST)
            start_time = data_input.data.get('time_from')
            end_time = data_input.data.get('time_to')
            if start_time.count(':') == 1:
                start_time += ':00'
            if end_time.count(':') == 1:
                end_time += ':00'
            else:
                if data_input.data.get('time_from') is not None:
                    new_time_from = datetime.combine(datetime.strptime(request.data['date'], '%Y-%m-%d').date(),
                                                     datetime.strptime(start_time, '%H:%M:%S').time())
                else:
                    new_time_from = booking.time_from
                if data_input.data.get('time_to') is not None:
                    new_time_to = datetime.combine(datetime.strptime(request.data['date'], '%Y-%m-%d').date(),
                                                   datetime.strptime(end_time, '%H:%M:%S').time())
                else:
                    new_time_to = booking.time_to
                if data_input.data.get('room') is not None:
                    new_room = Room.objects.get(id=data_input.data.get('room'))
                else:
                    new_room = booking.room
                data_vali = checkBookings([{"start_time": new_time_from,
                                            "end_time": new_time_to}], new_room, booking.id)
                if data_input.data.get('status') is not None:
                    booking.status = data_input.data.get('status')
                email_booker = data_input.data.get('email')
                if email_booker is not None:  # if exist in data
                    if not CustomUser.objects.filter(email=email_booker).exists():
                        return Response({
                            'status': False,
                            "error": {
                                "code": status.HTTP_404_NOT_FOUND,
                                "message": "Booker not found!"
                            }
                        }, status=status.HTTP_404_NOT_FOUND)
                if len(data_vali) == 0:

                    user = str(Booking.objects.get(id=pk).created_by_id)
                    is_admin = (CustomUserSerializer(CustomUser.objects.get(id=token_decode["user_id"]))).data[
                        'is_superuser']
                    if is_admin == True or token_decode["user_id"] == user:
                        event_id = booking.event.id
                        if data_input.data.get('group') is not None:
                            Event.objects.filter(id=event_id).update(group=Group.objects.get(
                                name=data_input.data.get('group')),)
                        booking.time_from = new_time_from
                        booking.time_to = new_time_to
                        booking.room = new_room
                        booking.updated_at = timezone.now()
                        booking.updated_by = CustomUser.objects.get(id=token_decode['user_id'])
                        booking.save()

                        return Response({
                            'status': True,

                        }, status=status.HTTP_200_OK)
                    else:
                        return Response({
                            'status': False,
                            'message': 'You are not the creator or admin'
                        }, status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({
                        'status': False,
                        "error": {
                            "code": status.HTTP_400_BAD_REQUEST,
                            "message": f"conflict with {data_vali[0].event.title} from {data_vali[0].time_from.date()} {data_vali[0].time_from.time()}"
                                       f" to {data_vali[0].time_to.date()} {data_vali[0].time_to.time()}!"
                        }
                    }, status=status.HTTP_400_BAD_REQUEST)
