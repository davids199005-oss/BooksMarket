from django.db.models import Count
from rest_framework import viewsets
from rest_framework.routers import DefaultRouter

from books_market.models import Category, Book
from .serializers import CategorySerializer, BookListSerializer, BookDetailSerializer


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CategorySerializer
    lookup_field = 'slug'
    lookup_url_kwarg = 'slug'

    def get_queryset(self):
        return Category.objects.annotate(book_count=Count('book')).order_by('title')


class BookViewSet(viewsets.ReadOnlyModelViewSet):
    lookup_field = 'slug'
    lookup_url_kwarg = 'slug'

    def get_queryset(self):
        qs = Book.objects.select_related('category', 'language')
        category_slug = self.request.query_params.get('category')
        if category_slug:
            qs = qs.filter(category__slug=category_slug)
        return qs

    def get_serializer_class(self):
        if self.action == 'list':
            return BookListSerializer
        return BookDetailSerializer


router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='api-category')
router.register(r'books', BookViewSet, basename='api-book')
