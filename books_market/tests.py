from datetime import date

from django.test import TestCase, Client
from django.urls import reverse

from .models import Category, Language, Book


class CategoryModelTests(TestCase):
    def test_save_generates_slug_from_title(self):
        cat = Category(title="Programming Books", description="Desc")
        cat.save()
        self.assertEqual(cat.slug, "programming-books")

    def test_duplicate_title_gets_unique_slug(self):
        Category.objects.create(title="Python", description="D1")
        cat2 = Category(title="Python", description="D2")
        cat2.save()
        self.assertEqual(cat2.slug, "python-1")


class BookModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.category = Category.objects.create(
            title="Tech", slug="tech", description="Tech category"
        )
        cls.language = Language.objects.create(code="en", name="English")

    def test_save_generates_slug_from_title(self):
        book = Book(
            title="Clean Code",
            author="R. Martin",
            description="A book",
            published_date=date(2008, 1, 1),
            category=self.category,
        )
        book.save()
        self.assertEqual(book.slug, "clean-code")

    def test_duplicate_title_gets_unique_slug(self):
        Book.objects.create(
            title="Django Book",
            slug="django-book",
            author="Author",
            description="Desc",
            published_date=date(2020, 1, 1),
            category=self.category,
        )
        book2 = Book(
            title="Django Book",
            author="Other",
            description="Desc2",
            published_date=date(2021, 1, 1),
            category=self.category,
        )
        book2.save()
        self.assertEqual(book2.slug, "django-book-1")


class LanguageModelTests(TestCase):
    def test_str_returns_name(self):
        lang = Language(code="ru", name="Russian")
        self.assertEqual(str(lang), "Russian")


class HomeViewTests(TestCase):
    def test_home_returns_200(self):
        client = Client()
        response = client.get("/")
        self.assertEqual(response.status_code, 200)


class CategoryListViewTests(TestCase):
    def test_category_list_returns_categories_in_context(self):
        Category.objects.create(title="Cat1", slug="cat1", description="D1")
        client = Client()
        response = client.get("/categories/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("categories", response.context)
        self.assertEqual(response.context["categories"].count(), 1)


class CategoryDetailViewTests(TestCase):
    def test_category_detail_200_valid_slug_404_invalid(self):
        Category.objects.create(title="Valid", slug="valid", description="D")
        client = Client()
        r1 = client.get("/categories/valid/")
        self.assertEqual(r1.status_code, 200)
        self.assertEqual(r1.context["category"].slug, "valid")
        r2 = client.get("/categories/nonexistent-slug/")
        self.assertEqual(r2.status_code, 404)


class BookDetailViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.category = Category.objects.create(
            title="Tech", slug="tech", description="Tech"
        )

    def test_book_detail_200_valid_slug_404_invalid(self):
        Book.objects.create(
            title="Some Book",
            slug="some-book",
            author="Author",
            description="Desc",
            published_date=date(2020, 1, 1),
            category=self.category,
        )
        client = Client()
        r1 = client.get("/books/some-book/")
        self.assertEqual(r1.status_code, 200)
        self.assertEqual(r1.context["book"].slug, "some-book")
        r2 = client.get("/books/nonexistent-book/")
        self.assertEqual(r2.status_code, 404)


class SearchBooksViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.category = Category.objects.create(
            title="Tech", slug="tech", description="Tech"
        )

    def test_search_empty_query_and_with_query(self):
        Book.objects.create(
            title="Python Guide",
            slug="python-guide",
            author="Smith",
            description="Desc",
            published_date=date(2020, 1, 1),
            category=self.category,
        )
        client = Client()
        r_empty = client.get("/search/")
        self.assertEqual(r_empty.status_code, 200)
        self.assertEqual(r_empty.context["query"], "")
        self.assertEqual(list(r_empty.context["books"]), [])
        r_q = client.get("/search/", {"q": "Python"})
        self.assertEqual(r_q.status_code, 200)
        self.assertEqual(r_q.context["query"], "Python")
        self.assertEqual(len(list(r_q.context["books"])), 1)
        self.assertEqual(r_q.context["books"][0].slug, "python-guide")
