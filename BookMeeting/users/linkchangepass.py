import base64
import json
import os.path
import sys

from rest_framework import serializers, status
from rest_framework.decorators import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
import datetime as DT

from .models import CustomUser


class newpassword(serializers.Serializer):
    new_password = serializers.CharField(max_length=255)


class mail_newpassword(APIView):
    permission_classes = [AllowAny]

    def post(self, request, pk):  # lấy forgot key từ db
        if not pk.endswith("'"):
            pk += "'"
        encrypted_data = pk[2:-1].encode()
        data_encoded = base64.b64decode(encrypted_data)
        data_string = data_encoded.decode()
        data = json.loads(data_string)

        user = CustomUser.objects.get(id=data["user_id"])
        key = data["user_forgotkey"]
        timeExp = data["time_out"]

        format = "%Y-%m-%d %H:%M:%S"
        dt_object = DT.datetime.strptime(timeExp, format)

        timeNow = DT.datetime.strptime(DT.datetime.now(DT.timezone.utc).strftime("%Y-%m-%d %H:%M:%S"), format)

        # kiểm tra hạn của forgot key
        if timeNow > dt_object:
            return Response({
                'status': False,
                "error": {
                    "code": status.HTTP_408_REQUEST_TIMEOUT,
                    "message": "No longer forgot key!"
                }
            }, status=status.HTTP_408_REQUEST_TIMEOUT)

        # kiểm tra key đã sử dụng rồi hay chưa
        fhandle = open(
            os.path.join(sys.path[0], r'C:\inetpub\wwwroot\03.source-backend\BookMeeting\users\used_token.txt'))
        for line in fhandle:
            if line == key:
                return Response({
                    'status': False,
                    "error": {
                        "code": status.HTTP_406_NOT_ACCEPTABLE,
                        "message": "Key used!"
                    }
                }, status=status.HTTP_406_NOT_ACCEPTABLE)
        fhandle.close()

        # nhận thông tin mật khẩu mới
        serializer = newpassword(data=request.data)
        if serializer.is_valid():  # tìm được thông tin
            user.set_password(serializer.data.get("new_password"))
            user.save()

            fhandle = open(
                os.path.join(sys.path[0], r'C:\inetpub\wwwroot\03.source-backend\BookMeeting\users\used_token.txt'),
                'a')
            fhandle.write(key)
            fhandle.close()

            return Response({
                'status': True,
            }, status=status.HTTP_200_OK)

        else:
            return Response({
                'status': False,
                "error": {
                    "code": status.HTTP_400_BAD_REQUEST,
                    "message": "wrong inform format!"
                }
            }, status=status.HTTP_400_BAD_REQUEST)
