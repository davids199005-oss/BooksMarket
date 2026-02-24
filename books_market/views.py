from django.shortcuts import render, get_object_or_404
from django.db.models import Count

from .models import Category, Book


def home(request):
    return render(request, 'books_market/home.html')


def about(request):
    return render(request, 'books_market/about.html')


def category_list(request):
    categories = Category.objects.annotate(book_count=Count('book')).order_by('title')
    return render(request, 'books_market/category_list.html', {'categories': categories})


def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug)
    books = Book.objects.filter(category=category).select_related('category', 'language')
    return render(request, 'books_market/category_detail.html', {'category': category, 'books': books})


def book_detail(request, slug):
    book = get_object_or_404(Book.objects.select_related('category', 'language'), slug=slug)
    return render(request, 'books_market/book_detail.html', {'book': book})