from django.urls import path, include
from .views import *
from .sendmail import sendmail
from .linkchangepass import *
from .reset_pass_bytoken import *
from .sendmail_resetpass_token import *

urlpatterns = [
    path('sendmail_bytoken/', sendmail_bytoken_api, name='sendmail'),
    path('sendmail/', sendmail, name='sendmail'),
    path('reset-password-bytoken/', reset_pass_bytoken_api.as_view(), name='reset-password-bytoken'),
    path('loginnew/', UserLoginNewView.as_view(), name='UserLoginNewView'),
    path('change-password/', ChangePasswordView.as_view(), name='change_password_status=0'),

    path('change-password/<str:pk>', mail_newpassword.as_view(), name='reset-password'),
    path('user_id/', UserNameView.as_view(), name="User Name View"),
    path('user_list/', ListUser.as_view(), name="user list"),
    path('', UserList.as_view(), name="all-user"),
    path('login/', UserLoginView.as_view(), name='login'),
    path('register/', UserRegisterView.as_view(), name="register"),
]
