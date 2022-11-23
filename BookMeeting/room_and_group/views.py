from datetime import datetime
from tkinter import N
from tkinter.messagebox import NO
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import generics, mixins
from rest_framework.decorators import APIView, action
from rest_framework import status
from .serializers import GroupSerializer, RoomSerializer, DeleteRoomSerializer
from .models import Group, Room
from rest_framework.permissions import IsAdminUser
import sys
from django.utils import timezone
from django.db import transaction
from django.db.models import Q

sys.path.append("..")
from events.models import Event
from events.serializers import EventSerializer
from booking.models import Booking
from booking.serializers import BookingSerializer, BookingemptySerializer, BookingsearchroomSerializer
from .serializers import AddRoomSerializer, GroupManagerSerializer
from .permissions import IsADGroupPermission
from rest_framework_simplejwt.authentication import JWTAuthentication
from users.models import Group_user, CustomUser


class GroupView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = GroupSerializer
    queryset = Group.objects.all()

    def get(self, request, format=None):
        groups = Group.objects.all().filter(status_group__in=['0', '1']).order_by('-created_at')
        serializers = GroupSerializer(groups, many=True)
        return Response({
            "success": True,
            "data": serializers.data,
        }, status=status.HTTP_200_OK)


class GroupDetailView(generics.GenericAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = GroupSerializer
    queryset = Group.objects.all()

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


class EditGroup(generics.GenericAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = GroupSerializer
    queryset = Group.objects.all()

    def put(self, request, pk, format=None):
        jwt_object = JWTAuthentication()
        header = jwt_object.get_header(request)
        raw_token = jwt_object.get_raw_token(header)
        validated_token = jwt_object.get_validated_token(raw_token)
        user = jwt_object.get_user(validated_token)

        group_all = Group.objects.all()
        serializer_all = GroupSerializer(group_all, many=True)
        try:
            group = Group.objects.get(pk=pk)
        except Group.DoesNotExist:
            return Response({
                "success": False,
                "message": "Group does not exist!"
            }, status=status.HTTP_400_BAD_REQUEST)
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
                "message": "Field name is required"
            }, status=status.HTTP_400_BAD_REQUEST)
        try:
            group_all.filter(status_group=-1).filter(name=request.data['name']).delete()
            serializer_save = GroupSerializer(group, data=request.data)
            if serializer_save.is_valid():
                serializer_save.save()
                Group.objects.filter(id=serializer.data['id']).update(updated_by=user,
                                                                      name=request.data['name'].upper())
                return Response({
                    "success": True,
                    "message": "Edit Successful!"
                }, status=status.HTTP_201_CREATED)
        except Group.DoesNotExist:
            return Response({'code': status.HTTP_404_NOT_FOUND})


class AddGroup(generics.GenericAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = GroupSerializer

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
                    "message": serializer.errors,
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
                                                                                              name=request.data[
                                                                                                  'name'].upper(),
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
                    data_group_manager = {
                        "user_id": request.user,
                        "group_id": Group.objects.get(name=request.data['name']),
                        "email": request.user.email,
                        "isADGroup": True
                    }
                    GroupManagerSerializer().create(validated_data=data_group_manager)
                Group.objects.all().filter(name=request.data['name']).update(created_by=user,
                                                                             name=request.data['name'].upper())
                return Response({
                    "success": True,
                }, status=status.HTTP_201_CREATED)


class RoomView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = RoomSerializer
    queryset = Room.objects.all()

    def get(self, request, format=None):
        rooms = Room.objects.all().filter(status_room__in=['0', '1']).order_by('-updated_at')
        serializers = RoomSerializer(rooms, many=True)
        return Response({
            "success": True,
            "data": serializers.data
        })


class RoomDetailView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = RoomSerializer
    queryset = Room.objects.all()

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


class SearchEventRoom(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = BookingsearchroomSerializer

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


class AddRoom(generics.GenericAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = AddRoomSerializer

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
                    "message": serializer.errors,
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


class DeleteRoom(generics.GenericAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = DeleteRoomSerializer

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


class DeleteGroup(generics.GenericAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = GroupSerializer

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


class EditRoom(generics.GenericAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = AddRoomSerializer
    queryset = Room.objects.all()

    def put(self, request, pk, format=None):

        jwt_object = JWTAuthentication()
        header = jwt_object.get_header(request)
        raw_token = jwt_object.get_raw_token(header)
        validated_token = jwt_object.get_validated_token(raw_token)
        user = jwt_object.get_user(validated_token)

        room_all = Room.objects.all()
        serializer_all = RoomSerializer(room_all, many=True)
        try:
            room = Room.objects.get(pk=pk)
        except Room.DoesNotExist:
            return Response({
                "success": False,
                "message": "Room does not exist!"
            }, status=status.HTTP_400_BAD_REQUEST)
        serializer = RoomSerializer(room)
        try:
            data_3 = Room.objects.filter(~Q(pk=pk)).filter(status_room__in='0').filter(color=request.data['color'])
        except:
            return Response({
                "success": False,
                "message": "Field color is required"
            }, status=status.HTTP_400_BAD_REQUEST)
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
                "message": "Field name is required"
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            room = Room.objects.get(pk=pk)
            serializer = RoomSerializer(room, data=request.data)
            room_all.filter(status_room=-1).filter(name=request.data['name']).delete()
            if serializer.is_valid():
                serializer.save()
                room_all.filter(id=pk).update(name=request.data['name'].upper())
                return Response(serializer.data)
            return Response({
                "success": False,
                "message": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        except Room.DoesNotExist:
            return Response({'code': status.HTTP_404_NOT_FOUND})


class GroupManagerViewset(generics.GenericAPIView, mixins.ListModelMixin):
    permission_classes = (IsAuthenticated,)
    serializer_class = GroupManagerSerializer
    queryset = Group_user.objects.all()

    def get_queryset(self):
        group_id = self.kwargs.get("group_id")
        return self.queryset.filter(group_id=group_id)

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *arg, **kwargs):
        with transaction.atomic():
            try:
                check_permission = Group_user.objects.get(
                    Q(email=request.user) & Q(group_id=self.kwargs.get("group_id")))
            except Group_user.DoesNotExist:
                return Response({
                    "success": False,
                    "detail": "You do not exist in this group!"
                }, status.HTTP_400_BAD_REQUEST)
            if not check_permission.isADGroup and not request.user.is_superuser:
                return Response({
                    "success": False,
                    "detail": "Permission denied!"
                }, status.HTTP_403_FORBIDDEN)
            for _email in request.data.get("email"):
                try:
                    user_id = CustomUser.objects.get(email=_email)
                except CustomUser.DoesNotExist:
                    transaction.set_rollback(True)
                    return Response({
                        "success": False,
                        "detail": f"{_email} Not Found!"
                    }, status.HTTP_400_BAD_REQUEST)
                if Group_user.objects.filter(
                        Q(email=_email) & Q(group_id=self.kwargs.get("group_id"))).count():
                    return Response({
                        "success": False,
                        "detail": f"{_email} exist in Group!"
                    })
                infor_user = {
                    "user_id": user_id,
                    "group_id": Group.objects.get(pk=self.kwargs.get("group_id")),
                    "email": _email,
                }
                if (request.user.is_superuser and request.user.email != _email) or check_permission.isADGroup:
                    GroupManagerSerializer().create(validated_data=infor_user)

            return Response({
                "success": True,
                "detail": "Invite User successfully!!!"
            }, status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        _email = request.data.get("email")
        group_id = self.kwargs.get("group_id")
        try:
            CustomUser.objects.get(email=_email)
        except CustomUser.DoesNotExist:
            return Response({
                "success": False,
                "detail": f"{_email} Not Found!"
            }, status.HTTP_400_BAD_REQUEST)
        try:
            check_permission = Group_user.objects.get(Q(email=request.user) & Q(group_id=group_id))
        except Group_user.DoesNotExist:
            return Response({
                "success": False,
                "detail": f"{_email} do not exist in this group!"
            }, status.HTTP_400_BAD_REQUEST)
        try:
            user_need_kick = Group_user.objects.get(
                Q(email=_email) & Q(group_id=group_id))
        except Group_user.DoesNotExist:
            return Response({
                "success": False,
                "detail": f"{_email} has not joined the group!"
            }, status.HTTP_400_BAD_REQUEST)
        if request.user.is_superuser and request.user.email != _email:
            user_need_kick.delete()
            return Response({
                "success": True,
                "detail": f"Kick the {_email} successful!"
            }, status.HTTP_200_OK)
        if not check_permission.isADGroup:
            return Response({
                "success": False,
                "detail": "Permission denied!"
            }, status.HTTP_403_FORBIDDEN)
        if check_permission.isADGroup and not user_need_kick.isADGroup:
            user_need_kick.delete()
            return Response({
                "success": True,
                "detail": f"Kick the {_email} successful!"
            }, status.HTTP_200_OK)
        return Response({
            "success": False,
            "detail": "Permission denied!"
        }, status.HTTP_403_FORBIDDEN)


class GroupManageActionView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = GroupManagerSerializer
    queryset = Group_user.objects.all()

    def post(self, request, *args, **kwargs):
        check_group = self.queryset.filter(group_id=self.kwargs.get("group_id"))
        if not check_group:
            return Response({
                "success": False,
                "detail": "Group not found!"
            }, status.HTTP_404_NOT_FOUND)
        try:
            isADGroup = GroupManagerSerializer(check_group.get(user_id=request.user)).data.get("isADGroup")
        except:
            return Response({
                "success": False,
                "detail": "The user has not joined any groups!!"
            }, status.HTTP_400_BAD_REQUEST)
        if isADGroup:
            return Response({
                "success": False,
                "detail": "You need to give someone else admin rights!!!"
            }, status.HTTP_400_BAD_REQUEST)
        check_group.get(user_id=request.user).delete()
        return Response({
            "success": True,
            "detail": "Leave group successful!"
        })


class GroupManagerPermission(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = GroupManagerSerializer
    queryset = Group_user.objects.all()

    def post(self, request, *args, **kwargs):
        try:
            check_user = CustomUser.objects.get(email=request.data.get("email"))
        except CustomUser.DoesNotExist:
            return Response({
                "success": False,
                "detail": "Email Not Found!"
            }, status.HTTP_400_BAD_REQUEST)
        try:
            isADGroup = Group_user.objects.get(Q(email=request.user) & Q(group_id=self.kwargs.get("group_id")))
        except Group_user.DoesNotExist:
            return Response({
                "success": False,
                "detail": "Group Not Found!!"
            }, status.HTTP_404_NOT_FOUND)
        if not isADGroup.isADGroup:
            return Response({
                "success": False,
                "detail": "Permission denied!!"
            }, status.HTTP_403_FORBIDDEN)
        try:
            check_inf = Group_user.objects.get(
                Q(email=request.data.get("email")) & Q(group_id=self.kwargs.get("group_id")))
        except Group_user.DoesNotExist:
            return Response({
                "success": False,
                "detail": "The user has not joined any groups!!"
            }, status.HTTP_400_BAD_REQUEST)
        count_ad = Group_user.objects.filter(Q(group_id=self.kwargs.get("group_id")) & Q(isADGroup=True)).count()
        if count_ad > 5:
            return Response({
                "success": False,
                "detail": "Group can't have more than 5 admins!!"
            })
        if isADGroup.isADGroup or request.user.is_superuser:
            if check_inf.isADGroup:
                return Response({
                    "success": False,
                    "detail": "User is already admin!!"
                })
            check_inf.inherit()
            return Response({
                "success": True,
                "detail": "Successfully!!"
            }, status.HTTP_200_OK)
        return Response({
            "success": False,
            "detail": "Permission denied!!"
        }, status.HTTP_403_FORBIDDEN)


class GroupManagerDemote(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = GroupManagerSerializer
    queryset = Group_user.objects.all()

    def post(self, request, *args, **kwargs):
        count_ad = Group_user.objects.filter(Q(group_id=self.kwargs.get("group_id")) & Q(isADGroup=True))
        is_ad = Group_user.objects.get(Q(email=request.user) & Q(group_id=self.kwargs.get("group_id")))
        if not is_ad.isADGroup:
            return Response({
                "success": False,
                "detail": "Permission denied!!"
            }, status.HTTP_403_FORBIDDEN)
        if count_ad.count() < 2:
            return Response({
                "success": False,
                "detail": "Group need at least 1 admin!!"
            }, status.HTTP_400_BAD_REQUEST)
        try:
            demote = count_ad.get(user_id=request.user)
        except:
            return Response({
                "success": False,
                "detail": "The user has not joined any groups!!"
            }, status.HTTP_400_BAD_REQUEST)
        demote.demote()
        return Response({
            "success": True,
            "detail": "Successfully!!"
        }, status.HTTP_200_OK)
