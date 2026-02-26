import os
import mimetypes

from django.shortcuts import render, get_object_or_404
from django.http import FileResponse, Http404
from django.db.models import Count
from django.contrib.auth.decorators import login_required

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
    return render(request, 'books_market/book_detail.html', {
        'book': book,
        'user_can_access_file': request.user.is_authenticated,
    })


def _serve_book_file(book, as_attachment: bool):
    """Отдаёт файл книги; вызывается только для авторизованных."""
    if not book.file:
        raise Http404("File not available")
    path = book.file.path
    if not os.path.isfile(path):
        raise Http404("File not found")
    filename = os.path.basename(book.file.name)
    content_type, _ = mimetypes.guess_type(filename)
    if not content_type:
        content_type = "application/octet-stream"
    response = FileResponse(open(path, "rb"), as_attachment=as_attachment, filename=filename)
    response["Content-Type"] = content_type
    return response


@login_required
def book_read(request, slug):
    """Отдача файла книги для просмотра в браузере (inline)."""
    book = get_object_or_404(Book, slug=slug)
    return _serve_book_file(book, as_attachment=False)


@login_required
def book_download(request, slug):
    """Отдача файла книги для скачивания (attachment)."""
    book = get_object_or_404(Book, slug=slug)
    return _serve_book_file(book, as_attachment=True)


def register_page(request):
    return render(request, 'books_market/register.html')


def login_page(request):
    return render(request, 'books_market/login.html')


def welcome_page(request):
    return render(request, 'books_market/welcome.html')


def cabinet_page(request):
    return render(request, 'books_market/cabinet.html')