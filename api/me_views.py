from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from books_market.models import Book, BookFavorite, BookRead
from .serializers import BookListSerializer


class FavoritesListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = Book.objects.filter(
            favorited_by__user=request.user
        ).select_related('category', 'language').distinct().order_by('-favorited_by__created_at')
        serializer = BookListSerializer(qs, many=True, context={'request': request})
        return Response(serializer.data)

    def post(self, request):
        book_slug = request.data.get('book_slug')
        if not book_slug:
            return Response(
                {'detail': 'book_slug is required.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        book = Book.objects.filter(slug=book_slug).first()
        if not book:
            return Response(
                {'detail': 'Book not found.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        _, created = BookFavorite.objects.get_or_create(user=request.user, book=book)
        return Response(
            {'detail': 'Added to favorites.' if created else 'Already in favorites.'},
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )


class FavoritesDestroyView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, book_slug):
        deleted, _ = BookFavorite.objects.filter(
            user=request.user, book__slug=book_slug
        ).delete()
        if not deleted:
            return Response(
                {'detail': 'Not in favorites.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(status=status.HTTP_204_NO_CONTENT)


class ReadListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = Book.objects.filter(
            read_by__user=request.user
        ).select_related('category', 'language').distinct().order_by('-read_by__read_at')
        serializer = BookListSerializer(qs, many=True, context={'request': request})
        return Response(serializer.data)

    def post(self, request):
        book_slug = request.data.get('book_slug')
        if not book_slug:
            return Response(
                {'detail': 'book_slug is required.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        book = Book.objects.filter(slug=book_slug).first()
        if not book:
            return Response(
                {'detail': 'Book not found.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        _, created = BookRead.objects.get_or_create(user=request.user, book=book)
        return Response(
            {'detail': 'Marked as read.' if created else 'Already marked as read.'},
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )


class ReadDestroyView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, book_slug):
        deleted, _ = BookRead.objects.filter(
            user=request.user, book__slug=book_slug
        ).delete()
        if not deleted:
            return Response(
                {'detail': 'Not in read list.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(status=status.HTTP_204_NO_CONTENT)
