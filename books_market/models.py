from django.conf import settings
from django.db import models
from django.core.validators import FileExtensionValidator
from django.utils.text import slugify


def _generate_unique_slug(manager, slug_field_name: str, base_slug: str, exclude_pk=None):
    """Generate a unique slug for the given manager, appending a number if needed."""
    slug = base_slug
    counter = 1
    filter_kwargs = {slug_field_name: slug}
    while True:
        qs = manager.filter(**filter_kwargs)
        if exclude_pk is not None:
            qs = qs.exclude(pk=exclude_pk)
        if not qs.exists():
            return slug
        slug = f"{base_slug}-{counter}"
        filter_kwargs[slug_field_name] = slug
        counter += 1


class Category(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, null=True, blank=True)
    description = models.TextField()

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug and self.title:
            base_slug = slugify(self.title)
            self.slug = _generate_unique_slug(
                Category.objects, "slug", base_slug, exclude_pk=self.pk
            )
        super().save(*args, **kwargs)


class Language(models.Model):
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Book(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, null=True, blank=True)
    published_date = models.DateField()
    author = models.CharField(max_length=255)
    description = models.TextField()
    image = models.ImageField(upload_to="books/covers/", blank=True, null=True)
    file = models.FileField(
        upload_to="books/files/",
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=["pdf", "epub", "mobi"])],
    )
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    language = models.ForeignKey(
        Language,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug and self.title:
            base_slug = slugify(self.title)
            self.slug = _generate_unique_slug(
                Book.objects, "slug", base_slug, exclude_pk=self.pk
            )
        super().save(*args, **kwargs)


class BookFavorite(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="book_favorites",
    )
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name="favorited_by",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [["user", "book"]]
        ordering = ["-created_at"]


class BookRead(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="books_read",
    )
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name="read_by",
    )
    read_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [["user", "book"]]
        ordering = ["-read_at"]
