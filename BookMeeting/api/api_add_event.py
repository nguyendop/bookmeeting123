from datetime import datetime, timedelta, timezone
from rest_framework import serializers, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.conf import settings
from users.models import CustomUser
from events.models import Event
from booking.models import Booking
from room_and_group.models import Room, Group
from django.db.models import Q
import jwt
import re


# Receive Data
class serializer_add_event(serializers.Serializer):
    email = serializers.EmailField(max_length=128, required=False)
    title = serializers.CharField(max_length=255)
    group = serializers.CharField(max_length=254, required=False)
    room = serializers.CharField(max_length=254)
    start_time = serializers.TimeField()
    end_time = serializers.TimeField()
    date = serializers.CharField(max_length=50)

    repeat = serializers.BooleanField()
    weekly = serializers.CharField(max_length=7, required=False)
    from_date = serializers.CharField(max_length=50, required=False)
    to_date = serializers.CharField(max_length=50, required=False)


# check booking's datetime, 1 data = 1 component of list
def checkBookings(list_booking,
                  room_input):  # [booking1, booking2, ...]   booking1{start_time: "", end_time: ""} room: ""
    data_vali = list()
    for booking_datetime in list_booking:
        if len(data_vali) != 0:
            return data_vali
        data_vali += Booking.objects.filter(
            Q(room=room_input) &
            # time_from > start_time và < end_time
            (Q(time_from__gte=booking_datetime['start_time'], time_from__lte=booking_datetime['end_time']) |
             # time_to > start_time và end_time
             Q(time_to__gte=booking_datetime['start_time'], time_to__lte=booking_datetime['end_time']) |
             # start_time > time_from và < time_to
             Q(time_from__gte=booking_datetime['start_time'], time_to__lte=booking_datetime['start_time']) |
             # end_time > time_from và < time_to
             Q(time_from__gte=booking_datetime['end_time'], time_to__lte=booking_datetime['end_time'])))
    return data_vali

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def api_add_event(request):
    # receive data
    data_input = serializer_add_event(data=request.data)
    # receive user's token
    token_decode = jwt.decode(request.META['HTTP_AUTHORIZATION'].split(' ')[1], settings.SECRET_KEY,
                              algorithms=["HS256"])

    # check if there is some missing info
    if not data_input.is_valid():
        empty_data_list = list()
        if data_input.data.get('title') is None:
            empty_data_list.append('title')
        if data_input.data.get('room') is None:
            empty_data_list.append('room')
        if data_input.data.get('start_time') is None:
            empty_data_list.append('start_time')
        if data_input.data.get('end_time') is None:
            empty_data_list.append('end_time')
        if data_input.data.get('date') is None:
            empty_data_list.append('date')
        if data_input.data.get('repeat') is None:
            empty_data_list.append('repeat')
        return Response({
            'status': False,
            "error": {
                "code": status.HTTP_400_BAD_REQUEST,
                "message": f"missing {empty_data_list} information!"
            }
        }, status=status.HTTP_400_BAD_REQUEST)
    else:
        # check integrity of input information

        # check email
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

        # check time format
        start_time = data_input.data.get('start_time')
        end_time = data_input.data.get('end_time')

        # FE sends only hour:minute
        if start_time.count(':') == 1:
            start_time += ':00'
        if end_time.count(':') == 1:
            end_time += ':00'

        # check format input time by trying convert to datetime type
        try:
            start_time = datetime.strptime(start_time, '%H:%M:%S')  # exist default date but compare by .time()
            end_time = datetime.strptime(end_time, '%H:%M:%S')
        except Exception:
            return Response({
                'status': False,
                "error": {
                    "code": status.HTTP_406_NOT_ACCEPTABLE,
                    "message": "Time format must be either Hour:Minute or Hour:Minute:Second!"
                }
            }, status=status.HTTP_406_NOT_ACCEPTABLE)

        # check format input date
        try:
            day = datetime.strptime(data_input.data.get('date'), "%Y-%m-%d")
        except Exception:
            return Response({
                'status': False,
                "error": {
                    "code": status.HTTP_406_NOT_ACCEPTABLE,
                    "message": "Date format must be Year-Month-Day!"
                }
            }, status=status.HTTP_406_NOT_ACCEPTABLE)

        # check optional info (repeat, weekly, from_date, to_date)
        repeat = data_input.data.get('repeat')
        if repeat is True:
            from_date = data_input.data.get('from_date')
            to_date = data_input.data.get('to_date')
            if from_date is None or to_date is None:
                return Response({
                    'status': False,
                    "error": {
                        "code": status.HTTP_404_NOT_FOUND,
                        "message": "from_date and to_date must be FILLED with TRUE REPEAT!"
                    }
                }, status=status.HTTP_404_NOT_FOUND)
            try:
                from_date = datetime.strptime(from_date, "%Y-%m-%d")
                to_date = datetime.strptime(to_date, "%Y-%m-%d")
            except Exception:
                return Response({
                    'status': False,
                    "error": {
                        "code": status.HTTP_406_NOT_ACCEPTABLE,
                        "message": "from_date and to_date format must be Year-Month-Day!"
                    }
                }, status=status.HTTP_406_NOT_ACCEPTABLE)

            # check weekly
            weekly = data_input.data.get('weekly')
            if weekly is None:
                return Response({
                    'status': False,
                    "error": {
                        "code": status.HTTP_404_NOT_FOUND,
                        "message": "WEEKLY must be FILLED with TRUE REPEAT!"
                    }
                }, status=status.HTTP_404_NOT_FOUND)
            rex = re.compile('[2-8]{1,7}')
            if rex.match(weekly) is None:
                return Response({
                    'status': False,
                    "error": {
                        "code": status.HTTP_406_NOT_ACCEPTABLE,
                        "message": "weekly must be as planned!"
                    }
                }, status=status.HTTP_406_NOT_ACCEPTABLE)

            boolean_weekly = {
                "2": True if weekly.find('2') != -1 else False,
                "3": True if weekly.find('3') != -1 else False,
                "4": True if weekly.find('4') != -1 else False,
                "5": True if weekly.find('5') != -1 else False,
                "6": True if weekly.find('6') != -1 else False,
                "7": True if weekly.find('7') != -1 else False,
                "8": True if weekly.find('8') != -1 else False,
            }

        # Validate time then add
        # pack all times of bookings into a list
        list_booking = list()
        if repeat is False:
            start_time = datetime.combine(day.date(), start_time.time())
            end_time = datetime.combine(day.date(), end_time.time())
            list_booking.append({'start_time': start_time,
                                 'end_time': end_time})
        else:
            from_date = from_date.date()
            to_date = to_date.date()
            # from_date to_date start_time end_time

            delta = to_date - from_date
            for i in range(delta.days + 1):
                # time not change so no need to set new variable
                if boolean_weekly[str((from_date + timedelta(days=i)).weekday() + 2)]:
                    start_time = datetime.combine(from_date + timedelta(days=i), start_time.time())
                    end_time = datetime.combine(from_date + timedelta(days=i), end_time.time())
                    list_booking.append({'start_time': start_time,
                                         'end_time': end_time})
        if len(list_booking)==0:
            return Response({
                'status': False,
                "error": {
                    "code": status.HTTP_400_BAD_REQUEST,
                    "message": f"from {from_date} to {to_date} no day"
                }
            }, status=status.HTTP_400_BAD_REQUEST)
        room_input = Room.objects.get(name=data_input.data.get('room')).id
        data_vali = list(checkBookings(list_booking, room_input))
        if len(data_vali) == 0:
            # add event
            if data_input.data.get('group') is not None:
                new_event = Event.objects.create(title=data_input.data.get('title'),
                                                 group=Group.objects.get(name=data_input.data.get('group')),
                                                 created_at=datetime.now(timezone.utc),
                                                 created_by=CustomUser.objects.get(id=token_decode['user_id']))
            else:
                new_event = Event.objects.create(title=data_input.data.get('title'),
                                                 created_at=datetime.now(timezone.utc),
                                                 created_by=CustomUser.objects.get(id=token_decode['user_id']))
            # add booking
            for i in list_booking:
                Booking.objects.create(event=Event.objects.get(id=new_event.id),
                                       time_from=i['start_time'],
                                       time_to=i['end_time'],
                                       room=Room.objects.get(id=room_input),
                                       created_at=datetime.now(timezone.utc),
                                       created_by=CustomUser.objects.get(id=token_decode['user_id']))

            return Response({
                'status': True
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'status': False,
                "error": {
                    "code": status.HTTP_400_BAD_REQUEST,
                    "message": f"conflict with {data_vali[0].event.title} from {data_vali[0].time_from.date()} {data_vali[0].time_from.time()}"
                               f" to {data_vali[0].time_to.date()} {data_vali[0].time_to.time()}!"
                }
            }, status=status.HTTP_400_BAD_REQUEST)




