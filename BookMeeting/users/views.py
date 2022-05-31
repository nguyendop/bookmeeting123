from django.conf import settings
from django.contrib.auth import authenticate
from django.core.mail import send_mail
from rest_framework import status, generics, filters
from rest_framework.decorators import APIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.template.loader import render_to_string
from .models import CustomUser, status_user
from .permissions import IsOwnerOrReadOnly
from .serializers import CustomUserSerializer, UserListAll, UserLoginSerializer, ChangePasswordSerializer, RegisterSerializer, \
    UserViewSerializer


class UserList(generics.ListAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [filters.SearchFilter]
    search_fields = ['fullname']


class UserRegisterView(APIView):
    """
    This is Register view
    """
    permission_classes = [IsAdminUser]

    def post(self, request, format=None):
        jwt_object = JWTAuthentication()
        header = jwt_object.get_header(request)
        raw_token = jwt_object.get_raw_token(header)
        validated_token = jwt_object.get_validated_token(raw_token)
        user_id = jwt_object.get_user(validated_token).id

        serializer = RegisterSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                "success": False,
                "error": {
                    "code": status.HTTP_400_BAD_REQUEST,
                    "message": "Email is invalid!",
                }
            }, status=status.HTTP_400_BAD_REQUEST)
        elif serializer.is_valid():
            try:
                user_data = CustomUser.objects.get(email=serializer.data['email'])
                serializer_user = CustomUserSerializer(user_data)
                if serializer_user.data['status_user'] == '-1':
                    status_user = CustomUser.objects.filter(email=serializer.data['email']).update(status_user=1)
                    created_by = CustomUser.objects.filter(email=serializer.data['email']).update(created_by=user_id)
                    updated_by = CustomUser.objects.filter(email=serializer.data['email']).update(updated_by=user_id)
                    serializer_save_user = CustomUserSerializer(user_data, data=[status_user, created_by, updated_by])
                    if serializer_save_user.is_valid():
                        serializer_save_user.save()

                    email = serializer.data['email']
                    password = '123456'
                    html_template = 'reset_mail.html'
                    html_content = render_to_string(html_template, {'email': email, 'password': password})
                    send_mail(subject='User Password Bookmeeting', message='msg', from_email=settings.EMAIL_HOST_USER,
                              recipient_list=[email], fail_silently=False, html_message=html_content)
                    return Response({
                        "success": True,
                    }, status=status.HTTP_201_CREATED)
                return Response({
                    "success": False,
                    "error": {
                        "code": status.HTTP_400_BAD_REQUEST,
                        "message": "This email is exist!",
                    }
                }, status=status.HTTP_400_BAD_REQUEST)
            except:
                serializer = RegisterSerializer(data=request.data)
                serializer.is_valid()
                serializer.save()
                CustomUser.objects.filter(email=request.data['email']).update(created_by=user_id)
                CustomUser.objects.filter(email=request.data['email']).update(updated_by=user_id)

                email = serializer.data['email']
                password = '123456'
                # msg = f'''Bạn đã tạo account thành công hãy truy cập theo đường link để kích hoạt tài khoản: http://10.99.63.125:81/active
                # http://10.99.63.125:68/LoginPage/NewUserLogin
                # Với username: {email}
                # Password: {password}
                # Hãy truy cập và đổi mật khẩu để duy trì đăng nhập.
                # Truy cập trang: https://www.ominext.com/ để liên hệ với chúng tôi, hoặc contact tới số điện thoại:0123456789'''
                html_template = 'reset_mail.html'
                html_content = render_to_string(html_template, {'email': email, 'password': password})
                send_mail(subject='User Password Bookmeeting', message='msg', from_email=settings.EMAIL_HOST_USER,
                          recipient_list=[email], fail_silently=False, html_message=html_content)
                return Response({
                    "success": True,
                }, status=status.HTTP_201_CREATED)


class UserLoginView(APIView):
    """
    This is login view
    """

    def post(self, request, format=None):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = authenticate(
                request,
                email=serializer.validated_data['email'],
                password=serializer.validated_data['password']
            )
            try:
                user_data = CustomUser.objects.get(email=serializer.data['email'])
            except:
                return Response({
                    "success": False,
                    "error": {
                        "code": status.HTTP_400_BAD_REQUEST,
                        "message": "Email or password is incorrect!"
                    }
                }, status=status.HTTP_400_BAD_REQUEST)
            serializer_user = CustomUserSerializer(user_data)
            if user and (serializer_user.data['status_user'] == '1' or serializer_user.data['is_superuser']):
                refresh = TokenObtainPairSerializer.get_token(user)
                is_admin = CustomUser.objects.get(email=request.data['email']).is_superuser
                status_user = CustomUser.objects.get(email=request.data['email']).status_user
                data = {
                    'status_user': status_user,
                    'is_admin': is_admin,
                    'refresh_token': str(refresh),
                    'access_token': str(refresh.access_token),
                    'access_expires': int(settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'].total_seconds()),
                    'refresh_expires': int(settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'].total_seconds())
                }
                return Response({
                    "success": True,
                    "data": data,
                }, status=status.HTTP_200_OK)
            elif user and (serializer_user.data['status_user'] == '0'):
                return Response({
                    "success": False,
                    "error": {
                        "code": status.HTTP_400_BAD_REQUEST,
                        "message": "Account not active!"
                    }
                }, status=status.HTTP_400_BAD_REQUEST)
            elif user and (serializer_user.data['status_user'] == '2'):
                return Response({
                    "success": False,
                    "error": {
                        "code": status.HTTP_400_BAD_REQUEST,
                        "message": "Account has been locked!"
                    }
                }, status=status.HTTP_400_BAD_REQUEST)

            return Response({
                "success": False,
                "error": {
                    "code": status.HTTP_400_BAD_REQUEST,
                    "message": "Email or password is incorrect!"
                }
            }, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            "success": False,
            "error": {
                "code": status.HTTP_400_BAD_REQUEST,
                "message": "Email or password is invalid!"
            }
        }, status=status.HTTP_400_BAD_REQUEST)


class UserLoginNewView(APIView):
    """
    This is login view
    """

    def post(self, request, format=None):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = authenticate(
                request,
                email=serializer.validated_data['email'],
                password=serializer.validated_data['password']
            )
            try:
                user_data = CustomUser.objects.get(email=serializer.data['email'])
            except:
                return Response({
                    "success": False,
                    "error": {
                        "code": status.HTTP_400_BAD_REQUEST,
                        "message": "Email or password is incorrect!"
                    }
                }, status=status.HTTP_400_BAD_REQUEST)
            serializer_user = CustomUserSerializer(user_data)
            if user and (serializer_user.data['status_user'] == '0' or serializer_user.data['is_superuser']):
                refresh = TokenObtainPairSerializer.get_token(user)
                is_admin = CustomUser.objects.get(email=request.data['email']).is_superuser
                data = {
                    'is_admin': is_admin,
                    'refresh_token': str(refresh),
                    'access_token': str(refresh.access_token),
                    'access_expires': int(settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'].total_seconds()),
                    'refresh_expires': int(settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'].total_seconds())
                }
                return Response({
                    "success": True,
                    "data": data,
                }, status=status.HTTP_200_OK)
            return Response({
                "success": False,
                "error": {
                    "code": status.HTTP_400_BAD_REQUEST
                }
            }, status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordView(APIView):
    """
    An endpoint for changing password.
    """
    serializer_class = ChangePasswordSerializer
    model = CustomUser
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def get_object(self, queryset=None):
        obj = self.request.user
        return obj

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = ChangePasswordSerializer(data=request.data)

        if serializer.is_valid():
            # Check old password
            if not self.object.check_password(serializer.data.get("old_password")):
                return Response({
                    "success": False,
                    "error": {
                        "code": status.HTTP_409_CONFLICT,
                        "message": "old password is not correct!"
                    }
                }, status=status.HTTP_404_NOT_FOUND)

            # set_password also hashes the password that the user will get
            self.object.set_password(serializer.data.get("new_password"))
            self.object.save()
            try:
                jwt_object = JWTAuthentication()
                header = jwt_object.get_header(request)
                raw_token = jwt_object.get_raw_token(header)
                validated_token = jwt_object.get_validated_token(raw_token)
                user = jwt_object.get_user(validated_token)
                user_data = CustomUser.objects.get(email=user)
                serializer_user = CustomUserSerializer(user_data)

                if serializer_user.data['status_user'] == '0':
                    status_user = CustomUser.objects.filter(email=user).update(status_user=1)
                    serializer_save_user = CustomUserSerializer(user_data, data=status_user)

                    if serializer_save_user.is_valid():
                        serializer_save_user.save()

            except:
                return Response({
                    "success": False,
                    "error": {
                        "code": status.HTTP_400_BAD_REQUEST
                    }
                }, status=status.HTTP_400_BAD_REQUEST)

            return Response({
                "success": True,
            }, status=status.HTTP_202_ACCEPTED)

        return Response({
            "success": False,
            "error": {
                "code": status.HTTP_400_BAD_REQUEST,
                "message": "Password is invalid!",
            }
        })


class UserDetail(APIView):
    """
    Retrieve, update or delete a user instance.
    """
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def get(self, request, pk, format=None):

        try:
            user = CustomUser.objects.get(pk=pk)
            serializer = CustomUserSerializer(user)
            return Response(serializer.data)

        except CustomUser.DoesNotExist:
            return Response({'code': status.HTTP_404_NOT_FOUND})

    def put(self, request, pk, format=None):
        try:
            user = CustomUser.objects.get(pk=pk)
            serializer = CustomUserSerializer(user, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except CustomUser.DoesNotExist:
            return Response({'code': status.HTTP_404_NOT_FOUND})

    def delete(self, request, pk, format=None):
        try:
            user = CustomUser.objects.get(pk=pk)
            user.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except CustomUser.DoesNotExist:
            return Response({'code': status.HTTP_404_NOT_FOUND})


class UserNameView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):

        jwt_object = JWTAuthentication()
        header = jwt_object.get_header(request)
        raw_token = jwt_object.get_raw_token(header)
        validated_token = jwt_object.get_validated_token(raw_token)
        user = jwt_object.get_user(validated_token)
        try:
            user_data = CustomUser.objects.get(email=user)
        except:
            return Response({
                "success": False,
                "error": {
                    "code": status.HTTP_400_BAD_REQUEST,
                    "message": "Bad request!"
                }
            }, status=status.HTTP_400_BAD_REQUEST)
        return Response({
            "success": True,
            "data": UserViewSerializer(user_data).data,
        }, status=status.HTTP_200_OK)

class ListUser(APIView):
    permissions_classes = [IsAuthenticated]
    def get(self, request, format=None):
        User = CustomUser.objects.all()
        serializer = UserListAll(User, many=True)
        return Response({
            "success": True,
            "data": serializer.data
        })
