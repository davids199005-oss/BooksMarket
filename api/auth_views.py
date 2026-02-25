from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from rest_framework.views import APIView

from rest_framework_simplejwt.views import (
    TokenBlacklistView,
    TokenObtainPairView,
    TokenRefreshView,
)

from .auth_serializers import RegisterSerializer

User = get_user_model()


class AuthThrottle(AnonRateThrottle):
    rate = '20/hour'
    scope = 'auth'


class LoginView(TokenObtainPairView):
    throttle_classes = [AuthThrottle]


class TokenRefreshThrottleView(TokenRefreshView):
    throttle_classes = [AuthThrottle]


class LogoutView(TokenBlacklistView):
    throttle_classes = [AuthThrottle]


class RegisterView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [AuthThrottle]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data, context={'request': request})
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        user = serializer.save()
        return Response(
            {'id': user.id, 'username': user.username, 'email': user.email},
            status=status.HTTP_201_CREATED,
        )


class CurrentUserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({
            'id': user.id,
            'username': user.username,
            'email': getattr(user, 'email', '') or '',
        })


class PasswordResetRequestView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [AuthThrottle]

    def post(self, request):
        email = request.data.get('email', '').strip()
        if not email:
            return Response(
                {'detail': 'Укажите email.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user = User.objects.filter(email__iexact=email, is_active=True).first()
        if user:
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            reset_url = f"{settings.FRONTEND_RESET_URL}?uid={uid}&token={token}"
            subject = render_to_string('email/password_reset_subject.txt').strip()
            body = render_to_string('email/password_reset_body.txt', {'reset_url': reset_url})
            send_mail(
                subject=subject,
                message=body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )
        return Response(
            {'detail': 'Если аккаунт с таким email существует, вы получите письмо с инструкциями.'},
            status=status.HTTP_200_OK,
        )


class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [AuthThrottle]

    def post(self, request):
        uid = request.data.get('uid')
        token = request.data.get('token')
        new_password = request.data.get('new_password')
        new_password_confirm = request.data.get('new_password_confirm')

        errors = {}
        if not uid:
            errors['uid'] = ['Обязательное поле.']
        if not token:
            errors['token'] = ['Обязательное поле.']
        if not new_password:
            errors['new_password'] = ['Обязательное поле.']
        if new_password_confirm is None or new_password_confirm == '':
            errors['new_password_confirm'] = ['Обязательное поле.']
        if errors:
            return Response(errors, status=status.HTTP_400_BAD_REQUEST)

        if new_password != new_password_confirm:
            return Response(
                {'new_password_confirm': ['Пароли не совпадают.']},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user_id = urlsafe_base64_decode(uid).decode()
            user_id = int(user_id)
        except (TypeError, ValueError, UnicodeDecodeError):
            return Response(
                {'detail': 'Некорректная ссылка сброса.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = User.objects.filter(pk=user_id, is_active=True).first()
        if not user or not default_token_generator.check_token(user, token):
            return Response(
                {'detail': 'Ссылка сброса недействительна или устарела.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        from django.contrib.auth.password_validation import validate_password
        from django.core.exceptions import ValidationError
        try:
            validate_password(new_password, user)
        except ValidationError as e:
            return Response(
                {'new_password': list(e.messages)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.set_password(new_password)
        user.save()
        return Response({'detail': 'Пароль успешно изменён.'}, status=status.HTTP_200_OK)
