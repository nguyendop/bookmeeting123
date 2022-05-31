from datetime import datetime, timedelta
from itertools import count
from re import S
import numpy as np
import re
from django.utils.dateparse import parse_datetime
from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.views import APIView
from .serializers import *
from rest_framework import status, generics, filters
from rest_framework.response import Response
from booking.models import Booking
from booking.serializers import *
from rest_framework_simplejwt.authentication import JWTAuthentication
from unidecode import unidecode


class SearchEvent_ListApi(generics.ListAPIView):
    queryset = Booking.objects.all()
    serializer_class = Booking_Search_event_Serializer
    permission_classes = [IsAdminUser]
    filter_backends = [filters.SearchFilter]
    search_fields = ['event']


class SearchEvent(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):

        try:
            title = request.data['title'].lower()
            title = unidecode(title)
            events = Event.objects.all().filter(title__icontains=title).filter(status__in=["0"])
            serializer_event = EventSearchSerializer(events, many=True)
            list_id_events = []
            for i in range(len(serializer_event.data)):
                a = serializer_event.data[i]['id']
                list_id_events.append(a)

            booking = Booking.objects.all().filter(status__in=["0"])
            serializer_booking = BookingSerializer(booking, many=True)
            list_id_booking = []
            for i in range(len(serializer_booking.data)):
                b = serializer_booking.data[i]['id']
                list_id_booking.append(b)

            list_id_b = []
            for i in list_id_booking:
                booking = Booking.objects.all().filter(id=i)
                serializer_booking = BookingSerializer(booking, many=True)
                for j in list_id_events:

                    if j == serializer_booking.data[0]['event']['id']:
                        list_id_b.append(i)

            booking = Booking.objects.all().filter(id__in=list_id_b)
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


class EventList(APIView):
    """
    This is booking list
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        try:
            eventlist = Event.objects.all().filter(status__in=["0"]).order_by('-created_at', '-updated_at')[:5]
            serializer = EventlistchSerializer(eventlist, many=True)
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


class EditEvent(APIView):
    permission_classes = [IsAdminUser]

    def put(self, request, pk, format=None):
        jwt_object = JWTAuthentication()
        header = jwt_object.get_header(request)
        raw_token = jwt_object.get_raw_token(header)
        validated_token = jwt_object.get_validated_token(raw_token)
        user = jwt_object.get_user(validated_token)

        event = Event.objects.get(pk=pk)
        serializer = EventSerializer(event)
        if serializer.data['status'] == '-1':
            return Response({
                "success": False,
                "error": {"code": status.HTTP_400_BAD_REQUEST,
                          "message": "Event is in the deleted state from before !",
                          }
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            event = Event.objects.get(pk=pk)
            serializer = EventSerializer(event, data=request.data)
            if serializer.is_valid():
                serializer.save()
                Event.objects.filter(id=serializer.data['id']).update(updated_by=user)
                return Response({
                    "success": True,
                }, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Event.DoesNotExist:
            return Response({'code': status.HTTP_404_NOT_FOUND})


class DeleteEvent(generics.ListAPIView):
    """
    In this API, we will use this to delete event that has booking is active. If booking is completed, we will not
    delete that
    """
    permission_classes = [IsAuthenticated]

    def list(self, request, pk):
        event = Event.objects.get(pk=pk)
        serializer = EventSerializer(event)

        if serializer.data['status'] == '-1':
            return Response({
                "success": False,
                "error": {"code": status.HTTP_400_BAD_REQUEST,
                          "message": "Event is in the deleted state from before !",
                          }
            }, status=status.HTTP_404_NOT_FOUND)

        try:
            Booking.objects.filter(event=pk).filter(status="0").update(status="-1")
            Event.objects.filter(id=pk).update(status="-1")
            return Response({
                "success": True,
            })
        except Event.DoesNotExist:
            return Response({
                "success": False,
                "error": {"code": status.HTTP_404_NOT_FOUND,
                          "message": "Event is not exist!",
                          }
            }, status=status.HTTP_404_NOT_FOUND)
    
