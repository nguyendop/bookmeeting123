from datetime import datetime
from tkinter import N
from tkinter.messagebox import NO
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import APIView
from rest_framework import status
from .serializers import GroupSerializer, RoomSerializer, DeleteRoomSerializer
from .models import Group, Room
from rest_framework.permissions import IsAdminUser
import sys
from django.utils import timezone
from django.db.models import Q
sys.path.append("..")
from events.models import Event
from events.serializers import EventSerializer
from booking.models import Booking
from booking.serializers import BookingSerializer, BookingemptySerializer, BookingsearchroomSerializer
from .serializers import AddRoomSerializer
from rest_framework_simplejwt.authentication import JWTAuthentication




class GroupView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        groups = Group.objects.all().filter(status_group__in=['0', '1']).order_by('-created_at')
        serializers = GroupSerializer(groups, many=True)
        return Response({
            "success": True,
            "data": serializers.data,
        }, status=status.HTTP_200_OK)

    def post(self, request, format=None):
        serializer = GroupSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'data': serializer.data, 'code': status.HTTP_201_CREATED})
        return Response(status.HTTP_400_BAD_REQUEST)


class GroupDetailView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, pk, format=None):
        try:
            group = Group.objects.get(pk=pk)
            serializer = GroupSerializer(group)
            return Response(serializer.data)
        except Group.DoesNotExist:
            return Response({'code': status.HTTP_404_NOT_FOUND})

    def put(self, request, pk, format=None):
        try:
            group = Group.objects.get(pk=pk)
            serializer = GroupSerializer(group, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Group.DoesNotExist:
            return Response({'code': status.HTTP_404_NOT_FOUND})

    def delete(self, request, pk, format=None):
        try:
            group = Group.objects.get(pk=pk)
            group.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Group.DoesNotExist:
            return Response({'code': status.HTTP_404_NOT_FOUND})


class EditGroup(APIView):
    permission_classes = [IsAdminUser]

    def put(self, request, pk, format=None):
        jwt_object = JWTAuthentication()
        header = jwt_object.get_header(request)
        raw_token = jwt_object.get_raw_token(header)
        validated_token = jwt_object.get_validated_token(raw_token)
        user = jwt_object.get_user(validated_token)

        group_all = Group.objects.all()
        serializer_all = GroupSerializer(group_all, many=True)
        group = Group.objects.get(pk=pk)
        serializer = GroupSerializer(group)

        listroom = []
        for i in serializer_all.data:
            if i['status_group'] == '0' or i['status_group'] == '1':
                listroom.append(i['name'].upper())

        try:
            if serializer.data['status_group'] == '-1':
                return Response({
                    "success": False,
                    "error": {
                        "code": status.HTTP_400_BAD_REQUEST,
                        "message": "Group not edit!",
                    }
                }, status=status.HTTP_400_BAD_REQUEST)
            listroom.remove(serializer.data['name'])
            if request.data['name'].upper() in listroom:
                return Response({
                    "success": False,
                    "error": {
                        "code": status.HTTP_400_BAD_REQUEST,
                        "message": "Group name is exist!",
                    }
                }, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({
                "success": False,
            }, status=status.HTTP_400_BAD_REQUEST)
        try:
            group_all.filter(status_group=-1).filter(name=request.data['name']).delete()
            serializer_save = GroupSerializer(group, data=request.data)
            if serializer_save.is_valid():
                serializer_save.save()
                Group.objects.filter(id=serializer.data['id']).update(updated_by=user, name=request.data['name'].upper())
                return Response({
                    "success": True,
                    "message": "Edit Successful!"
                }, status=status.HTTP_201_CREATED)
        except Group.DoesNotExist:
            return Response({'code': status.HTTP_404_NOT_FOUND})


class AddGroup(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, format=None):
        jwt_object = JWTAuthentication()
        header = jwt_object.get_header(request)
        raw_token = jwt_object.get_raw_token(header)
        validated_token = jwt_object.get_validated_token(raw_token)
        user = jwt_object.get_user(validated_token)

        serializer = GroupSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                "success": False,
                "error": {
                    "code": status.HTTP_400_BAD_REQUEST,
                    "message": "Input is invalid!",
                }
            }, status=status.HTTP_400_BAD_REQUEST)
        elif serializer.is_valid():
            data_1 = Group.objects.all().filter(name=request.data['name']).filter(status_group__in='1')
            serializer_1 = GroupSerializer(data_1, many=True)
            if serializer_1.data:
                return Response({
                    "success": False,
                    "error": {
                        "code": status.HTTP_400_BAD_REQUEST,
                        "message": "Group has been lock!",
                    }
                }, status=status.HTTP_400_BAD_REQUEST)

            data_0 = Group.objects.all().filter(name=request.data['name']).filter(status_group__in='0')
            serializer_0 = GroupSerializer(data_0, many=True)
            if serializer_0.data:
                return Response({
                    "success": False,
                    "error": {
                        "code": status.HTTP_400_BAD_REQUEST,
                        "message": "Group is exist!",
                    }
                }, status=status.HTTP_400_BAD_REQUEST)
            try:
                data_2 = Group.objects.get(name=request.data['name'])
                serializer_2 = GroupSerializer(data_2)
                if serializer_2.data['status_group'] == '-1':
                    data_check = Group.objects.all().filter(name=request.data['name']).update(status_group=0,
                                                                                              created_by=user,
                                                                                              name=request.data['name'].upper(),
                                                                                              created_at=timezone.now())
                    serializer_save = GroupSerializer(data_2, data=data_check)
                    if serializer_save.is_valid():
                        serializer_save.save()
                    return Response({
                        "success": True,
                    }, status=status.HTTP_201_CREATED)
            except:
                serializer = GroupSerializer(data=request.data)
                if serializer.is_valid():
                    serializer.save()
                Group.objects.all().filter(name=request.data['name']).update(created_by=user, name=request.data['name'].upper())

                return Response({
                    "success": True,
                }, status=status.HTTP_201_CREATED)


class RoomView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        rooms = Room.objects.all().filter(status_room__in=['0', '1']).order_by('-updated_at')
        serializers = RoomSerializer(rooms, many=True)
        return Response({
            "success": True,
            "data": serializers.data
        })



class RoomDetailView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, pk, format=None):
        try:
            room = Room.objects.get(pk=pk)
            serializer = RoomSerializer(room)
            return Response(serializer.data)
        except Room.DoesNotExist:
            return Response({'code': status.HTTP_404_NOT_FOUND})

    def put(self, request, pk, format=None):
        try:
            room = Room.objects.get(pk=pk)
            serializer = RoomSerializer(room, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Room.DoesNotExist:
            return Response({'code': status.HTTP_404_NOT_FOUND})

    def delete(self, request, pk, format=None):
        try:
            room = Room.objects.get(pk=pk)
            room.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Room.DoesNotExist:
            return Response({'code': status.HTTP_404_NOT_FOUND})


class SearchEventRoom(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        room_name = request.data['room_name']
        try:
            if room_name == 'ALL':
                booking = Booking.objects.all().filter(status__in=["0"])
                serializer_2 = BookingSerializer(booking, many=True)
                return Response({
                    "success": True,
                    "data": serializer_2.data,
                }, status=status.HTTP_200_OK)
            else:
                room_s = Room.objects.all().filter(name=room_name).filter(status_room__in=['0'])
                serializer = RoomSerializer(room_s, many=True)
                a = serializer.data
                a = a[0]
                a = dict(a)

                booking = Booking.objects.all().filter(status__in='0').filter(room=a['id'])
                serializer_2 = BookingsearchroomSerializer(booking, many=True)

                return Response({
                    "success": True,
                    "data": serializer_2.data,
                }, status=status.HTTP_200_OK)
        except:

            return Response({
                "success": False,
                "error": {
                    "code": status.HTTP_404_NOT_FOUND,
                    "message": "Room not found!"
                }
            }, status=status.HTTP_404_NOT_FOUND)


class AddRoom(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, format=None):
        jwt_object = JWTAuthentication()
        header = jwt_object.get_header(request)
        raw_token = jwt_object.get_raw_token(header)
        validated_token = jwt_object.get_validated_token(raw_token)
        user = jwt_object.get_user(validated_token)

        serializer = AddRoomSerializer(data=request.data)

        if not serializer.is_valid():
            return Response({
                "success": False,
                "error": {
                    "code": status.HTTP_400_BAD_REQUEST,
                    "message": "Input is invalid!",
                }
            }, status=status.HTTP_400_BAD_REQUEST)
        elif serializer.is_valid():
            data_1 = Room.objects.all().filter(name=request.data['name']).filter(status_room__in='1')
            serializer_1 = AddRoomSerializer(data_1, many=True)
            if serializer_1.data:
                return Response({
                    "success": False,
                    "error": {
                        "code": status.HTTP_400_BAD_REQUEST,
                        "message": "Room has been lock!",
                    }
                }, status=status.HTTP_400_BAD_REQUEST)

            data_0 = Room.objects.all().filter(name=request.data['name']).filter(status_room__in='0')
            serializer_0 = AddRoomSerializer(data_0, many=True)
            if serializer_0.data:
                return Response({
                    "success": False,
                    "error": {
                        "code": status.HTTP_400_BAD_REQUEST,
                        "message": "Room is exist!",
                    }
                }, status=status.HTTP_400_BAD_REQUEST)
            data_3 = Room.objects.all().filter(status_room__in='0').filter(color=request.data['color'])
            serializer_3 = AddRoomSerializer(data_3, many=True)
            if serializer_3.data:
                return Response({
                    "success": False,
                    "error": {
                        "code": status.HTTP_400_BAD_REQUEST,
                        "message": "color is exist!",
                    }
                }, status=status.HTTP_400_BAD_REQUEST)

            try:
                data_2 = Room.objects.filter(status_room__in='0').get(name=request.data['name'])
                serializer_2 = RoomSerializer(data_2)

                if serializer_2.data['status_room'] == '-1':
                    data_check = Room.objects.all().filter(name=request.data['name']).update(status_room=0,
                                                                                             created_by=user,
                                                                                             size=request.data['size'],
                                                                                             color=request.data[
                                                                                                 'color'],
                                                                                             name=request.data[
                                                                                                 'name'].upper()
                                                                                             ,
                                                                                             created_at=timezone.now())
                    serializer_save = RoomSerializer(data_2, data=data_check)
                    if serializer_save.is_valid():
                        serializer_save.save()
                    return Response({
                        "success": True,
                    }, status=status.HTTP_201_CREATED)
            except:

                serializer = RoomSerializer(data=request.data)

                if serializer.is_valid():
                    serializer.save()
                Room.objects.all().filter(name=request.data['name']).update(created_by=user,
                                                                            name=request.data['name'].upper())
                return Response({
                    "success": True,
                }, status=status.HTTP_201_CREATED)



class DeleteRoom(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, format=None):
        serializer = DeleteRoomSerializer(data=request.data)
        if serializer.is_valid():
            if serializer.data['name'] != serializer.data[request]:
                return Response({
                    "success": False,
                    "error": {
                        "code": status.HTTP_400_BAD_REQUEST,
                        "message": " RoomName Not Found!",
                    }
                }, status=status.HTTP_400_BAD_REQUEST)
        try:
            data = Room.objects.get(name=serializer.data['name'])
            serializer = DeleteRoomSerializer(data)
        except:
            return Response({
                "success": False,
                "error": {
                    "code": status.HTTP_400_BAD_REQUEST,
                    "message": "Input is invalid!",
                }
            }, status=status.HTTP_400_BAD_REQUEST)
        if BookingSerializer(Booking.objects.filter(room_id=serializer.data['id']).filter(status=0), many=True).data:
            return Response({
                "success": False,
                "error": {
                    "code": status.HTTP_400_BAD_REQUEST,
                    "message": "There's an event going on in the room",
                    }
            }, status=status.HTTP_400_BAD_REQUEST)
        if serializer.data['status_room'] == '0':
            Room.objects.filter(name=serializer.data['name']).update(status_room='-1')
            return Response({
                "success": True,
            }, status=status.HTTP_201_CREATED)

        return Response({
            "success": False,
            "error": {"code": status.HTTP_400_BAD_REQUEST,
                      "message": "Room is in the deleted state from before !",
                      }
        }, status=status.HTTP_400_BAD_REQUEST)


class DeleteGroup(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, format=None):
        serializer = GroupSerializer(data=request.data)

        try:
            data = Group.objects.get(name=request.data['name'])
            serializer = GroupSerializer(data)
        except:
            return Response({
                "success": False,
                "error": {
                    "code": status.HTTP_400_BAD_REQUEST,
                    "message": "Input is invalid!",
                }
            }, status=status.HTTP_400_BAD_REQUEST)
        if serializer.data['status_group'] == '0':
            status_group = Group.objects.filter(name=serializer.data['name']).update(status_group='-1')
            serializer = GroupSerializer(data, data=status_group)
            if serializer.is_valid():
                serializer.save()
            return Response({
                "success": True,
            }, status=status.HTTP_201_CREATED)

        return Response({
            "success": False,
            "error": {"code": status.HTTP_400_BAD_REQUEST,
                      "message": "Group is in the deleted state from before !",
                      }
        }, status=status.HTTP_400_BAD_REQUEST)


class EditRoom(APIView):
    permission_classes = [IsAdminUser]

    def put(self, request, pk, format=None):

        jwt_object = JWTAuthentication()
        header = jwt_object.get_header(request)
        raw_token = jwt_object.get_raw_token(header)
        validated_token = jwt_object.get_validated_token(raw_token)
        user = jwt_object.get_user(validated_token)

        room_all = Room.objects.all()
        serializer_all = RoomSerializer(room_all, many=True)
        room = Room.objects.get(pk=pk)
        serializer = RoomSerializer(room)

        data_3 = Room.objects.filter(~Q(pk =pk)).filter(status_room__in='0').filter(color=request.data['color'])
        serializer_3 = AddRoomSerializer(data_3, many=True)
        if serializer_3.data:
            return Response({
                "success": False,
                "error": {
                    "code": status.HTTP_400_BAD_REQUEST,
                    "message": "color is exist!",
                }
            }, status=status.HTTP_400_BAD_REQUEST)

        if serializer.data['status_room'] == '-1':
            return Response({
                "success": False,
                "error": {"code": status.HTTP_400_BAD_REQUEST,
                          "message": "Room is in the deleted state from before !",
                          }
            }, status=status.HTTP_400_BAD_REQUEST)
        list_room = []
        for i in serializer_all.data:
            if i['status_room'] == '0' or i['status_room'] == '1':
                list_room.append(i['name'].upper())
        try:
            list_room.remove(serializer.data['name'].upper())
            if request.data['name'].upper() in list_room:
                return Response({
                    "success": False,
                    "error": {
                        "code": status.HTTP_400_BAD_REQUEST,
                        "message": "Room name is exist!",
                    }
                }, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({
                "success": False,
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            room = Room.objects.get(pk=pk)
            serializer = RoomSerializer(room, data=request.data)
            room_all.filter(status_room=-1).filter(name=request.data['name']).delete()
            if serializer.is_valid():
                serializer.save()
                room_all.filter(id=pk).update(name=request.data['name'].upper())
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Room.DoesNotExist:
            return Response({'code': status.HTTP_404_NOT_FOUND})
