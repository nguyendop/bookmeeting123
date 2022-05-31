from datetime import datetime, timedelta
from django.utils.dateparse import parse_datetime
from rest_framework.decorators import APIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from users.serializers import CustomUserSerializer
from django.db.models import Q
from users.models import CustomUser
from .models import Booking
from room_and_group.models import Room
from .serializers import BookingSerializer, BookingemptySerializer
from room_and_group.serializers import RoomSerializer, Roomempty
from rest_framework_simplejwt.authentication import JWTAuthentication
from events.models import Event
from events.serializers import EventSerializer


class BookingListInTime(APIView):
    """
    In this we get all booking in range time
    """

    def post(self, request, format=None):
        for i in (EventSerializer(Event.objects.all().filter(status=0), many=True).data):
            booking = Booking.objects.all().filter(event_id=i['id']).filter(status=0)
            serializer = BookingSerializer(booking, many=True)
            if serializer.data == []:
                Event.objects.filter(id=i['id']).update(status=-1)
        try:
            rq_time_from = request.data['time_from']
            rq_time_to = request.data['time_to']
            booking = Booking.objects.all().filter(
                Q(status__in=["0", "1"]))
            serializer = BookingSerializer(booking, many=True)
            for i in serializer.data:
                if parse_datetime(i['time_from']).strftime('%Y-%m-%d %H:%M:%S') <= str(datetime.now()):
                    booking.filter(time_from=i['time_from']).update(status=1)
        except:
            return Response({
                "success": False,
                "error": {
                    "code": status.HTTP_400_BAD_REQUEST,
                    "message": "Bad request!",
                }
            }, status=status.HTTP_400_BAD_REQUEST)
        try:
            rq_time_from = request.data['time_from']
            rq_time_to = request.data['time_to']

            booking = Booking.objects.all().filter(
                Q(status__in=["0", "1"]) & (Q(time_from__range=[rq_time_from, rq_time_to]) |
                                            Q(time_to__range=[rq_time_from, rq_time_to])))
            serializer = BookingSerializer(booking, many=True)

            return Response({
                "success": True,
                "data": serializer.data,
            }, status=status.HTTP_200_OK)
        except:
            return Response({
                "success": False,
                "error": {
                    "code": status.HTTP_400_BAD_REQUEST,
                    "message": "Bad request!",
                }
            }, status=status.HTTP_400_BAD_REQUEST)


class BookingList(APIView):
    """
    This is booking list
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        try:
            bookings = Booking.objects.all().filter(status__in=["0"])[:5]
            serializer = BookingSerializer(bookings, many=True)
            return Response({
                "success": True,
                "data": serializer.data,
            }, status=status.HTTP_200_OK)
        except:
            return Response({
                "success": False,
                "error": {
                    "code": status.HTTP_400_BAD_REQUEST,
                    "message": "Bad request!",
                }
            }, status=status.HTTP_400_BAD_REQUEST)


class SearchEmptyRoom(APIView):
    """
    In this we get all booking in range time
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        try:
            rq_time_from = request.data['time_from']
            rq_time_to = request.data['time_to']

            booking = Booking.objects.all().filter(
                Q(status__in=['0']) & (Q(time_from__range=[rq_time_from, rq_time_to]) |
                                       Q(time_to__range=[rq_time_from, rq_time_to])))

            serializer = BookingemptySerializer(booking, many=True)
            roomempty = serializer.data
            id_list = []
            for i in range(len(roomempty)):
                a = roomempty[i]
                b = a["room"]
                b = dict(b)
                c = b["id"]
                id_list.append(c)
            room = Room.objects.all()
            roomserializer = Roomempty(room, many=True)

            roomempty2 = roomserializer.data
            id_list2 = []
            for j in range(len(roomempty2)):
                a = roomempty2[j]
                a = dict(a)
                b = a["id"]
                id_list2.append(b)
            cm = list(set(id_list) ^ set(id_list2))
            Search_Empty_Room = Room.objects.all().filter(id__in=cm).filter(status_room__in=['0'])
            serializerSearchemptry = RoomSerializer(Search_Empty_Room, many=True)
            return Response({
                "success": True,
                "data": serializerSearchemptry.data,
            }, status=status.HTTP_200_OK)
        except:
            return Response({
                "success": False,
                "error": {
                    "code": status.HTTP_400_BAD_REQUEST,
                    "message": "Bad request!",
                }
            }, status=status.HTTP_400_BAD_REQUEST)


# xóa nhiều booking
class DeleteManyBooking(APIView):
    def delete(self, request, format=None):
        try:
            weekly = request.data['weekly']
            from_date = datetime.strptime(request.data['from_date'], "%Y-%m-%d")
            to_date = datetime.strptime(request.data['to_date'], "%Y-%m-%d")
            event_id = request.data['event_id']
        except:
            return Response({
                "success": False,
                "message": "Input is invalid!"
            }, status=status.HTTP_400_BAD_REQUEST)




        boolean_weekly = {
        "2": True if weekly.find('2') != -1 else False,
        "3": True if weekly.find('3') != -1 else False,
        "4": True if weekly.find('4') != -1 else False,
        "5": True if weekly.find('5') != -1 else False,
        "6": True if weekly.find('6') != -1 else False,
        "7": True if weekly.find('7') != -1 else False,
        "8": True if weekly.find('8') != -1 else False,
        }
        list_booking = list()
        from_date = from_date.date()
        to_date = to_date.date()
        # from_date to_date start_time end_time
        # set day = from_date todo lưu DB không?
        delta = to_date - from_date
        for i in range(delta.days + 1):
            if boolean_weekly[str((from_date + timedelta(days=i)).weekday() + 2)]:
                start_time = (from_date + timedelta(days=i))
                list_booking.append(start_time)
        jwt_object = JWTAuthentication()
        header = jwt_object.get_header(request)
        raw_token = jwt_object.get_raw_token(header)
        validated_token = jwt_object.get_validated_token(raw_token)
        user = jwt_object.get_user(validated_token).id
        is_admin = (CustomUserSerializer(CustomUser.objects.get(id=user))).data['is_superuser']
        data_event=[]
        try:
            for i in list_booking:
                if is_admin:
                    time_from = Booking.objects.filter(time_from__date=i).filter(status=0).filter(event_id=event_id)
                    serializer = BookingSerializer(time_from, many=True)
                    if serializer.data!=[]:
                        data_event.append(serializer.data)
                    time_from.update(status=-1)
                else:
                    time_from = Booking.objects.filter(time_from__date=i).filter(status=0).filter(event_id=event_id).filter(created_by=user)
                    serializer = BookingSerializer(time_from, many=True)
                    if serializer.data!=[]:
                        data_event.append(serializer.data)
                    time_from.update(status=-1)
        except:
            return Response({
                "success": False,
                "message": "UUID Incorrect"
            }, status=status.HTTP_400_BAD_REQUEST)
        if data_event==[]:
            return Response({
                "success": False,
                "message": "Booking not found!"
            }, status=status.HTTP_404_NOT_FOUND)    
        return Response({
                "success": True,
                "message": "Delete successful!"
            }, status=status.HTTP_200_OK)

# delete 1 booking
class DeleteBooking(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, format=None):
        try:
            booking_id = request.data.get('booking_id')
        except:
            return Response({
                "success": False,
                "message": "Booking_id Incorrect"
            }, status=status.HTTP_400_BAD_REQUEST)
        jwt_object = JWTAuthentication()
        header = jwt_object.get_header(request)
        raw_token = jwt_object.get_raw_token(header)
        validated_token = jwt_object.get_validated_token(raw_token)
        user = jwt_object.get_user(validated_token).id
        is_admin = (CustomUserSerializer(CustomUser.objects.get(id=user))).data['is_superuser']
        try:
            if is_admin:
                time_from = Booking.objects.filter(id=booking_id).filter(status=0)
            else:
                time_from = Booking.objects.filter(id=booking_id).filter(status=0).filter(created_by=user)
        except:
            return Response({
                "success": False,
                "message": "Input is invalid!"
            }, status=status.HTTP_400_BAD_REQUEST)
        serializer = BookingSerializer(time_from, many=True)
        if serializer.data == []:
            return Response({
                "success": False,
                "message": "You are not the creator, you cannot delete booking!"
            }, status=status.HTTP_404_NOT_FOUND)
        else:
            time_from.update(status=-1)
            return Response({
                "success": True,
                "message": "Delete successful!"
            }, status=status.HTTP_200_OK)
