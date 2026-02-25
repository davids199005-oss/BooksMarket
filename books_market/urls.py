from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('categories/', views.category_list, name='category_list'),
    path('categories/<slug:slug>/', views.category_detail, name='category_detail'),
    path('books/<slug:slug>/', views.book_detail, name='book_detail'),
    path('register/', views.register_page, name='register'),
    path('login/', views.login_page, name='login'),
    path('welcome/', views.welcome_page, name='welcome'),
    path('cabinet/', views.cabinet_page, name='cabinet'),
]