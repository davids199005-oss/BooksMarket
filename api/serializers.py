from rest_framework import serializers

from books_market.models import Category, Language, Book


def _absolute_uri(request, url):
    if not url or not request:
        return url
    return request.build_absolute_uri(url)


class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Language
        fields = ['code', 'name']


class CategorySerializer(serializers.ModelSerializer):
    book_count = serializers.IntegerField(read_only=True, required=False)

    class Meta:
        model = Category
        fields = ['slug', 'title', 'description', 'book_count']


class BookListSerializer(serializers.ModelSerializer):
    category_slug = serializers.SlugRelatedField(source='category', slug_field='slug', read_only=True)
    category_title = serializers.CharField(source='category.title', read_only=True)
    image_url = serializers.SerializerMethodField()
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = Book
        fields = [
            'slug', 'title', 'author', 'published_date',
            'category_slug', 'category_title',
            'image_url', 'file_url',
        ]

    def get_image_url(self, obj):
        if not obj.image:
            return None
        request = self.context.get('request')
        return _absolute_uri(request, obj.image.url)

    def get_file_url(self, obj):
        if not obj.file:
            return None
        request = self.context.get('request')
        return _absolute_uri(request, obj.file.url)


class BookDetailSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    language = LanguageSerializer(read_only=True)
    image_url = serializers.SerializerMethodField()
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = Book
        fields = [
            'slug', 'title', 'author', 'published_date', 'description',
            'category', 'language',
            'image_url', 'file_url',
        ]

    def get_image_url(self, obj):
        if not obj.image:
            return None
        request = self.context.get('request')
        return _absolute_uri(request, obj.image.url)

    def get_file_url(self, obj):
        if not obj.file:
            return None
        request = self.context.get('request')
        return _absolute_uri(request, obj.file.url)
