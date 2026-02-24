from django.contrib import admin
from .models import Category, Language, Book


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug', 'description']
    prepopulated_fields = {'slug': ('title',)}


@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ['code', 'name']


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug', 'author', 'category', 'language', 'get_published_year']
    list_filter = ['category', 'language']
    search_fields = ['title', 'author']
    prepopulated_fields = {'slug': ('title',)}
    fields = ['title', 'slug', 'author', 'category', 'language', 'published_date', 'image', 'file', 'description']

    @admin.display(description='Published Year')
    def get_published_year(self, obj):
        return obj.published_date.year if obj.published_date else ''
