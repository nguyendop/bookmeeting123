import uuid
import json
import base64
import datetime as DT
from django.core.mail import send_mail
from django.conf import settings
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from .models import CustomUser
from django.template.loader import render_to_string


class sendserializer(serializers.Serializer):
    email = serializers.EmailField()


@api_view(["POST"])
@permission_classes([AllowAny])
def sendmail(request):
    serializer = sendserializer(data=request.data)  # convert json request to kinda python dictionary
    if serializer.is_valid():  # check valid of serializer
        email = serializer['email'].value  # take value "email" from dictionary above (input email)

        try:
            user = CustomUser.objects.get(email=email)  # try to find a user that match with input email
        except Exception as e:
            return Response({
                'status': False,
                "error": {
                    "code": status.HTTP_401_UNAUTHORIZED,
                    "message": "Email doesn't exist!"
                }
            }, status=status.HTTP_401_UNAUTHORIZED)

        if user.status_user == '0':
            return Response({
                'status': False,
                "error": {
                    "code": status.HTTP_406_NOT_ACCEPTABLE,
                    "message": "User's account has not yet been activated!"
                }
            }, status=status.HTTP_406_NOT_ACCEPTABLE)
        elif user.status_user == '-1':
            return Response({
                'status': False,
                "error": {
                    "code": status.HTTP_406_NOT_ACCEPTABLE,
                    "message": "User's account has been deleted!"
                }
            }, status=status.HTTP_406_NOT_ACCEPTABLE)
        elif user.status_user == '2':
            return Response({
                'status': False,
                "error": {
                    "code": status.HTTP_406_NOT_ACCEPTABLE,
                    "message": "User's account has been locked!"
                }
            }, status=status.HTTP_406_NOT_ACCEPTABLE)
        else:
            data = {
                "user_id": str(user.id),
                "user_forgotkey": str(uuid.uuid4()),
                "time_out": str(DT.datetime.now(DT.timezone.utc) + DT.timedelta(days=2))[:-13]
            }
            data_string = json.dumps(data)
            data_byte = bytes(data_string, 'utf-8')
            data_encoded = base64.b64encode(data_byte)
            html_template = 'reset_mail_sendmail.html'
            data_encoded_1 = str(data_encoded)[2:-1]
            data_encoded_2 = str(data_encoded)
            html_content = render_to_string(html_template,
                                            {'data_encoded_1': data_encoded_1, 'data_encoded_2': data_encoded_2})

            send_mail(subject='Authenticate forgot password', message='msg', from_email=settings.EMAIL_HOST_USER,
                      recipient_list=[email], fail_silently=False, html_message=html_content)  # send mail function
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
