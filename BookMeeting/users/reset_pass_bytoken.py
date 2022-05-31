from rest_framework import serializers, status
from rest_framework.decorators import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
import datetime as DT

from .models import CustomUser


class reset_pass_bytoken_inform(serializers.Serializer):
    email = serializers.EmailField()
    token = serializers.CharField(max_length=50)
    new_password = serializers.CharField(max_length=255)


class reset_pass_bytoken_api(APIView):
    permission_classes = [AllowAny]

    def post(self, request):  # lấy forgot key từ db
        serial_info = reset_pass_bytoken_inform(data=request.data)
        if serial_info.is_valid():
            try:
                user = CustomUser.objects.get(forgotkey=serial_info['token'].value, email=serial_info['email'].value)
                # tìm user có forgotkey như thế
            except Exception as e:
                return Response({
                    'status': False,
                    "error": {
                        "code": status.HTTP_401_UNAUTHORIZED,
                        "message": "Cannot find user with that forgotkey!"
                    }
                }, status=status.HTTP_401_UNAUTHORIZED)

            # kiểm tra hạn của forgotkey
            if DT.datetime.now(DT.timezone.utc) > user.forgotkey_timeout:
                user.forgotkey = None
                user.forgotkey_timeout = None
                return Response({
                    'status': False,
                    "error": {
                        "code": status.HTTP_408_REQUEST_TIMEOUT,
                        "message": "Forgotkey expired!"
                    }
                }, status=status.HTTP_408_REQUEST_TIMEOUT)

            # nhận thông tin mật khẩu mới
            user.set_password(serial_info.data.get("new_password"))  # băm mật khẩu và lưu vào db
            user.forgotkey = None  # Token dùng rồi sẽ bị xóa
            user.forgotkey_timeout = None
            user.save()
            return Response({
                'status': True,
            }, status=status.HTTP_200_OK)
        else:  # không tìm được thông  tin
            return Response({
                'status': False,
                "error": {
                    "code": status.HTTP_400_BAD_REQUEST,
                    "message": "wrong input format!"
                }
            }, status=status.HTTP_400_BAD_REQUEST)
