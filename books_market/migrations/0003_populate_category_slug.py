# Generated for populating slug on existing Category rows

from django.db import migrations
from django.utils.text import slugify


def populate_slugs(apps, schema_editor):
    Category = apps.get_model('books_market', 'Category')
    used = set()
    for cat in Category.objects.all():
        if not cat.slug:
            base = slugify(cat.title) or 'category'
            slug = base
            c = 1
            while slug in used:
                slug = f'{base}-{c}'
                c += 1
            used.add(slug)
            cat.slug = slug
            cat.save(update_fields=['slug'])


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('books_market', '0002_add_category_slug'),
    ]

    operations = [
        migrations.RunPython(populate_slugs, noop),
    ]
