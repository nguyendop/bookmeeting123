import uuid
import datetime as DT
from django.core.mail import send_mail
from django.conf import settings
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

from .models import CustomUser


class sendmail_bytoken_api_info(serializers.Serializer):
    email = serializers.EmailField()


@api_view(["POST"])
@permission_classes([AllowAny])
def sendmail_bytoken_api(request):
    serializer = sendmail_bytoken_api_info(data=request.data)  # convert json request to kinda python dictionary
    if serializer.is_valid():  # check valid of serializer
        email = serializer['email'].value  # take value "email" from dictionary above (input email)
        try:
            user = CustomUser.objects.get(email=email)  # try to find an user that match with input email
        except Exception as e:  # Not found user
            return Response({
                'status': False,
                "error": {
                    "code": status.HTTP_401_UNAUTHORIZED,
                    "message": "Email doesnot exist!"
                }
            }, status=status.HTTP_401_UNAUTHORIZED)

        user.forgotkey = uuid.uuid4()  # create uuid as a token
        user.forgotkey_timeout = DT.datetime.now(DT.timezone.utc) + DT.timedelta(days=2)  # create expire time for token
        user.save()
        msg = f'''This is your token given to reset your password, do not share with anyone else!
            Just in case, this is the link reset: http://10.99.63.125:81/confirm
            You would need this below token to reset your password, just copy and paste it into correct blank!
            Your token: {str(user.forgotkey)}
            Expire Time: {str(user.forgotkey_timeout)[:19]}'''

        send_mail(subject='Authenticate forgot password', message=msg, from_email=settings.EMAIL_HOST_USER,
                  recipient_list=[email])  # send mail function
        return Response({
            'status': True,
        }, status=status.HTTP_200_OK)

    else:
        return Response({
            'status': False,
            "error": {
                "code": status.HTTP_400_BAD_REQUEST,
                "message": "Wrong body json!"
            }
        }, status=status.HTTP_400_BAD_REQUEST)
