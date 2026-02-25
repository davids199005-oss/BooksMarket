from django.urls import path

from .auth_views import (
    CurrentUserView,
    LoginView,
    LogoutView,
    PasswordResetConfirmView,
    PasswordResetRequestView,
    RegisterView,
    TokenRefreshThrottleView,
)
from .me_views import (
    FavoritesDestroyView,
    FavoritesListCreateView,
    ReadDestroyView,
    ReadListCreateView,
)
from .views import router

urlpatterns = [
    path('auth/register/', RegisterView.as_view(), name='api-register'),
    path('auth/me/', CurrentUserView.as_view(), name='api-current-user'),
    path('auth/token/', LoginView.as_view(), name='api-token-obtain'),
    path('auth/token/refresh/', TokenRefreshThrottleView.as_view(), name='api-token-refresh'),
    path('auth/logout/', LogoutView.as_view(), name='api-logout'),
    path('auth/password/reset/', PasswordResetRequestView.as_view(), name='api-password-reset'),
    path('auth/password/reset/confirm/', PasswordResetConfirmView.as_view(), name='api-password-reset-confirm'),
    path('me/favorites/', FavoritesListCreateView.as_view(), name='api-favorites-list'),
    path('me/favorites/<slug:book_slug>/', FavoritesDestroyView.as_view(), name='api-favorites-destroy'),
    path('me/read/', ReadListCreateView.as_view(), name='api-read-list'),
    path('me/read/<slug:book_slug>/', ReadDestroyView.as_view(), name='api-read-destroy'),
] + router.urls
