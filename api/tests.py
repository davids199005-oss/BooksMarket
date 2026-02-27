from datetime import date

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status

from books_market.models import Category, Language, Book

User = get_user_model()

VALID_PASSWORD = "TestPass123!"


class CategoryAPITests(APITestCase):
    def test_category_list_returns_200_and_list(self):
        Category.objects.create(title="Cat", slug="cat", description="D")
        response = self.client.get("/api/categories/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data.get("results", response.data)
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["slug"], "cat")
        self.assertIn("book_count", data[0])

    def test_category_detail_by_slug_returns_200(self):
        Category.objects.create(title="Tech", slug="tech", description="Desc")
        response = self.client.get("/api/categories/tech/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["slug"], "tech")
        self.assertEqual(response.data["title"], "Tech")


class BookAPITests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.category = Category.objects.create(
            title="Tech", slug="tech", description="Tech"
        )
        cls.other_category = Category.objects.create(
            title="Other", slug="other", description="Other"
        )

    def test_book_list_returns_200_and_list(self):
        Book.objects.create(
            title="Book One",
            slug="book-one",
            author="Author",
            description="D",
            published_date=date(2020, 1, 1),
            category=self.category,
        )
        response = self.client.get("/api/books/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data.get("results", response.data)
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["slug"], "book-one")

    def test_book_list_filter_by_category(self):
        Book.objects.create(
            title="Tech Book",
            slug="tech-book",
            author="A",
            description="D",
            published_date=date(2020, 1, 1),
            category=self.category,
        )
        Book.objects.create(
            title="Other Book",
            slug="other-book",
            author="B",
            description="D",
            published_date=date(2020, 1, 1),
            category=self.other_category,
        )
        response = self.client.get("/api/books/?category=tech")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data.get("results", response.data)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["slug"], "tech-book")

    def test_book_detail_by_slug_returns_200(self):
        Book.objects.create(
            title="Detail Book",
            slug="detail-book",
            author="Author",
            description="Full description",
            published_date=date(2021, 5, 15),
            category=self.category,
        )
        response = self.client.get("/api/books/detail-book/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["slug"], "detail-book")
        self.assertIn("category", response.data)
        self.assertIn("language", response.data)
        self.assertIn("image_url", response.data)
        self.assertIn("file_url", response.data)


class RegisterAPITests(APITestCase):
    def test_register_success_returns_201(self):
        payload = {
            "username": "newuser",
            "email": "new@example.com",
            "password": VALID_PASSWORD,
            "password_confirm": VALID_PASSWORD,
        }
        response = self.client.post("/api/auth/register/", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("id", response.data)
        self.assertEqual(response.data["username"], "newuser")
        self.assertEqual(response.data["email"], "new@example.com")

    def test_register_validation_errors_returns_400(self):
        User.objects.create_user(
            username="taken", email="taken@example.com", password=VALID_PASSWORD
        )
        payload_duplicate_username = {
            "username": "taken",
            "email": "other@example.com",
            "password": VALID_PASSWORD,
            "password_confirm": VALID_PASSWORD,
        }
        response = self.client.post(
            "/api/auth/register/", payload_duplicate_username, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("username", response.data)
        payload_mismatch_password = {
            "username": "newuser",
            "email": "new@example.com",
            "password": VALID_PASSWORD,
            "password_confirm": "WrongConfirm1",
        }
        response2 = self.client.post(
            "/api/auth/register/", payload_mismatch_password, format="json"
        )
        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password_confirm", response2.data)


class CurrentUserAPITests(APITestCase):
    def test_me_401_without_token_200_with_token(self):
        r_anon = self.client.get("/api/auth/me/")
        self.assertEqual(r_anon.status_code, status.HTTP_401_UNAUTHORIZED)
        user = User.objects.create_user(
            username="testuser", email="test@example.com", password=VALID_PASSWORD
        )
        token_response = self.client.post(
            "/api/auth/token/",
            {"username": "testuser", "password": VALID_PASSWORD},
            format="json",
        )
        self.assertEqual(token_response.status_code, status.HTTP_200_OK)
        access = token_response.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        r_auth = self.client.get("/api/auth/me/")
        self.assertEqual(r_auth.status_code, status.HTTP_200_OK)
        self.assertEqual(r_auth.data["username"], "testuser")
        self.assertEqual(r_auth.data["email"], "test@example.com")


class FavoritesAPITests(APITestCase):
    def test_favorites_add_then_list(self):
        user = User.objects.create_user(
            username="user", email="u@example.com", password=VALID_PASSWORD
        )
        cat = Category.objects.create(title="C", slug="c", description="D")
        book = Book.objects.create(
            title="Fav Book",
            slug="fav-book",
            author="A",
            description="D",
            published_date=date(2020, 1, 1),
            category=cat,
        )
        token_resp = self.client.post(
            "/api/auth/token/",
            {"username": "user", "password": VALID_PASSWORD},
            format="json",
        )
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {token_resp.data['access']}"
        )
        post_resp = self.client.post(
            "/api/me/favorites/", {"book_slug": "fav-book"}, format="json"
        )
        self.assertEqual(post_resp.status_code, status.HTTP_201_CREATED)
        get_resp = self.client.get("/api/me/favorites/")
        self.assertEqual(get_resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(get_resp.data), 1)
        self.assertEqual(get_resp.data[0]["slug"], "fav-book")


class ReadAPITests(APITestCase):
    def test_read_add_delete_then_404_on_second_delete(self):
        user = User.objects.create_user(
            username="reader", email="r@example.com", password=VALID_PASSWORD
        )
        cat = Category.objects.create(title="C", slug="c", description="D")
        book = Book.objects.create(
            title="Read Book",
            slug="read-book",
            author="A",
            description="D",
            published_date=date(2020, 1, 1),
            category=cat,
        )
        token_resp = self.client.post(
            "/api/auth/token/",
            {"username": "reader", "password": VALID_PASSWORD},
            format="json",
        )
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {token_resp.data['access']}"
        )
        post_resp = self.client.post(
            "/api/me/read/", {"book_slug": "read-book"}, format="json"
        )
        self.assertEqual(post_resp.status_code, status.HTTP_201_CREATED)
        del_resp = self.client.delete("/api/me/read/read-book/")
        self.assertEqual(del_resp.status_code, status.HTTP_204_NO_CONTENT)
        del_again = self.client.delete("/api/me/read/read-book/")
        self.assertEqual(del_again.status_code, status.HTTP_404_NOT_FOUND)
