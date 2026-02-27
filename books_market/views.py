import os
import mimetypes
import json

from django.shortcuts import render, get_object_or_404
from django.http import FileResponse, Http404, HttpResponse
from django.db.models import Count, Q
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.templatetags.static import static

from .models import Category, Book


def theme_css(request):
    """Serves a small CSS file with theme variables (static image URLs). No inline styles in HTML."""
    header_bg = static("img/header_bg.jpg")
    hero_bg = static("img/landing_bg.jpg")
    css = (
        ":root {\n"
        f"  --header-bg-image: url('{header_bg}');\n"
        f"  --hero-bg-image: url('{hero_bg}');\n"
        "}\n"
    )
    return HttpResponse(css, content_type="text/css")


def home(request):
    return render(request, 'books_market/home.html')


def about(request):
    return render(request, 'books_market/about.html')


def category_list(request):
    categories = Category.objects.annotate(book_count=Count('book')).order_by('title')
    return render(request, 'books_market/category_list.html', {'categories': categories})


def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug)
    books_qs = Book.objects.filter(category=category).select_related('category', 'language').order_by('title')
    paginator = Paginator(books_qs, 24)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    return render(request, 'books_market/category_detail.html', {
        'category': category,
        'page_obj': page_obj,
        'paginator': paginator,
    })


def book_detail(request, slug):
    book = get_object_or_404(Book.objects.select_related('category', 'language'), slug=slug)
    related_books = (
        Book.objects.filter(category=book.category)
        .exclude(pk=book.pk)
        .select_related('category', 'language')[:4]
    )
    image_url = None
    if book.image:
        image_url = request.build_absolute_uri(book.image.url)
    json_ld = json.dumps({
        "@context": "https://schema.org",
        "@type": "Book",
        "name": book.title,
        "author": book.author,
        "description": (book.description or "")[:500],
        "image": image_url,
    }, ensure_ascii=False)
    return render(request, 'books_market/book_detail.html', {
        'book': book,
        'user_can_access_file': request.user.is_authenticated,
        'related_books': related_books,
        'json_ld': json_ld,
    })


def _serve_book_file(book, as_attachment: bool):
    """Serves the book file to authenticated users. Ensures the file handle is closed."""
    if not book.file:
        raise Http404("File not available")
    path = book.file.path
    if not os.path.isfile(path):
        raise Http404("File not found")
    filename = os.path.basename(book.file.name)
    content_type, _ = mimetypes.guess_type(filename)
    if not content_type:
        content_type = "application/octet-stream"
    f = open(path, "rb")
    try:
        response = FileResponse(f, as_attachment=as_attachment, filename=filename)
        response["Content-Type"] = content_type
        return response
    except Exception:
        f.close()
        raise


@login_required
def book_read(request, slug):
    """Serve the book file for viewing in the browser (inline)."""
    book = get_object_or_404(Book, slug=slug)
    return _serve_book_file(book, as_attachment=False)


@login_required
def book_download(request, slug):
    """Serve the book file for download (attachment)."""
    book = get_object_or_404(Book, slug=slug)
    return _serve_book_file(book, as_attachment=True)


def register_page(request):
    return render(request, 'books_market/register.html')


def login_page(request):
    return render(request, 'books_market/login.html')


def forgot_password_page(request):
    return render(request, 'books_market/forgot_password.html')


def reset_password_page(request):
    return render(request, 'books_market/reset_password.html', {
        'uid': request.GET.get('uid', ''),
        'token': request.GET.get('token', ''),
    })


def welcome_page(request):
    return render(request, 'books_market/welcome.html')


def cabinet_page(request):
    return render(request, 'books_market/cabinet.html')


SEARCH_RESULTS_LIMIT = 50


def search_books(request):
    q = (request.GET.get('q') or '').strip()
    books = []
    if q:
        books = (
            Book.objects.filter(
                Q(title__icontains=q) | Q(author__icontains=q)
            )
            .select_related('category', 'language')[:SEARCH_RESULTS_LIMIT]
        )
    return render(request, 'books_market/search.html', {
        'query': q,
        'books': books,
    })


def handler500(request):
    return render(request, '500.html', status=500)