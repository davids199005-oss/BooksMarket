# Generated for populating slug on existing Book rows

from django.db import migrations
from django.utils.text import slugify


def populate_slugs(apps, schema_editor):
    Book = apps.get_model('books_market', 'Book')
    used = set()
    for book in Book.objects.all():
        if not book.slug:
            base = slugify(book.title) or 'book'
            slug = base
            c = 1
            while slug in used:
                slug = f'{base}-{c}'
                c += 1
            used.add(slug)
            book.slug = slug
            book.save(update_fields=['slug'])


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('books_market', '0004_add_book_slug'),
    ]

    operations = [
        migrations.RunPython(populate_slugs, noop),
    ]
