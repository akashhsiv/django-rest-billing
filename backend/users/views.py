from rest_framework import  status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import viewsets, generics
from django.contrib.auth import update_session_auth_hash
from rest_framework_simplejwt.views import TokenObtainPairView
from django.utils.crypto import get_random_string
from django.conf import settings
from django.core.mail import send_mail
from .utils import send_temporary_password_email
from .models import Users
from .serializers import ChangePasswordSerializer, PasswordResetRequestSerializer, UserSerializer, MyTokenObtainPairSerializer, ResetPasswordSerializer, UserRegisterSerializer
from .models import Users
from .permissions import IsAdminUser, NotFirstLogin
from django.db import transaction

template = """
                <!DOCTYPE html>
                <html lang="en">
                <head>
                    <meta charset="UTF-8" />
                    <meta http-equiv="X-UA-Compatible" content="IE=edge" />
                    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
                    <title>Password Reset OTP</title>
                </head>
                <body
                    style="
                    font-family: Arial, sans-serif;
                    background-color: #f4f4f4;
                    padding: 20px;
                    "
                >
                    <div
                    style="
                        max-width: 600px;
                        margin: 0 auto;
                        background-color: #ffffff;
                        padding: 20px;
                        border-radius: 8px;
                    "
                    >
                    <br>
                    <p>Hi {username},</p>
                    <br>
                    <p style="color: #333333">
                        Use the following OTP to reset your password:
                    </p>
                    <h1
                        style="
                        text-align: center;
                        color: #333333;
                        font-size: 48px;
                        margin-top: 20px;
                        "
                    >
                        {otp} 
                    </h1>
                    <p style="color: #333333">
                        This OTP is valid for a single use only. Please do not share it with
                        anyone.
                    </p>
                    <p style="color: #333333">
                        If you did not request this OTP, please ignore this email.
                    </p>
                    <br>
                    <br>
                    <p style="color: #333333">
                        Regards,
                        <br>
                        Booking Engine
                    </p>
                    </div>
                </body>
                </html>
            """

subject = 'Password Reset OTP'


class UserViewSet(viewsets.ModelViewSet):
    queryset = Users.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser, NotFirstLogin]
    http_method_names = ['get', 'put', 'patch', 'delete']

    def create(self, request, *args, **kwargs):
        return Response(
            {"detail": "Use /register/ to create users."},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )

class PasswordResetRequest(APIView):
    permission_classes = [AllowAny]
    serializer_class = PasswordResetRequestSerializer

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data.get('email')
            user = Users.objects.filter(email=email).first()
            
            if user:
                otp = get_random_string(length=4, allowed_chars='1234567890')
                print("-------------",otp)
                user.reset_password_otp = otp

                user.save()
               

                body = template.format(username=user.username, otp=otp)
                from_email = settings.EMAIL_HOST_USER
                recipient_list = [email]

                # try:
                send_mail(subject, "", from_email,
                        recipient_list, html_message=body)
                return Response({"message": "OTP sent to your email address.", "otp": otp, "email": email}, status=status.HTTP_200_OK)
                # except Exception as e:
                    # print(e)
                    # return Response({"detail": "Failed to send OTP. Please try again later."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                return Response({"message": "OTP sent to your registered email address."}, status=status.HTTP_404_NOT_FOUND)

class PasswordResetConfirm(APIView):
    permission_classes = [AllowAny]
    serializer_class = ResetPasswordSerializer


    def post(self, request):
        email = request.data.get('email')
        otp = request.data.get('otp')
        new_password = request.data.get('new_password')

        if not all([email, otp, new_password]):
            return Response({"message": "All fields are required."}, status=status.HTTP_400_BAD_REQUEST)

        user = Users.objects.filter(email=email, reset_password_otp=otp).first()

        if user:
            user.set_password(new_password)
            user.reset_password_otp = None  
            user.is_first_login = False
            user.save()

            return Response({
                "message": "Password reset successfully. You can now log in.",
                "first_login_completed": True
            }, status=status.HTTP_200_OK)
        else:
            return Response({"message": "Invalid OTP or email."}, status=status.HTTP_400_BAD_REQUEST)

class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)

        if serializer.is_valid():
            old_password = serializer.data.get("old_password")
            new_password = serializer.data.get("new_password")
            confirm_password = serializer.data.get("confirm_password")

            user = request.user

            if not user.check_password(old_password):
                return Response({"message": "Old password is incorrect."}, status=status.HTTP_400_BAD_REQUEST)

            if new_password != confirm_password:
                return Response({"message": "New passwords do not match."}, status=status.HTTP_400_BAD_REQUEST)

            user.set_password(new_password)
            user.save()

            update_session_auth_hash(request, user)

            return Response({"message": "Password updated successfully."}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserRegisterView(generics.CreateAPIView):
    serializer_class = UserRegisterSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        with transaction.atomic():
            user = serializer.save()  

        temp_password = getattr(serializer, '_temp_password', None)
        email = request.data.get('email')

        if temp_password and email:
            send_temporary_password_email(email, temp_password)

        headers = self.get_success_headers(serializer.data)
        response_data = serializer.data
        response_data['email'] = email
        response_data['status'] = True
        response_data['message'] = "User registered successfully."

        return Response(response_data, status=status.HTTP_201_CREATED, headers=headers)

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response({"detail": "Successfully logged out."}, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({"detail": "Invalid refresh token."}, status=status.HTTP_400_BAD_REQUEST)     
        
class SuperAdminLoginView(TokenObtainPairView):
    serializer_class = type(
        "SuperAdminLoginSerializer",
        (MyTokenObtainPairSerializer,),
        {"expected_user_type": "super_admin"},
    )

class ManagerLoginView(TokenObtainPairView):
    serializer_class = type(
        "ManagerLoginSerializer",
        (MyTokenObtainPairSerializer,),
        {"expected_user_type": "manager"},
    )

class CashierLoginView(TokenObtainPairView):
    serializer_class = type(
        "CashierLoginSerializer",
        (MyTokenObtainPairSerializer,),
        {"expected_user_type": "cashier"},
    )