# Code Nest — BooksMarket

A Django web app for browsing a curated catalog of programming books. Browse by category, view details, and read or download books when available.

## Features

- **Web UI**: Home, categories list, category detail with books, book detail with cover, description, and download/read links
- **REST API**: Read-only API for categories and books (JSON), with pagination and optional filtering by category
- **Admin**: Django admin for managing categories, languages, and books (covers, PDFs, metadata)

## Tech Stack

- Python 3.11+
- Django 5.x
- Django REST Framework
- SQLite (default), Pillow for image fields

## Prerequisites

- Python 3.11 or higher
- pip

## Installation

1. Clone the repository and go to the project directory:

   ```bash
   git clone https://github.com/your-username/BooksMarket.git
   cd BooksMarket
   ```

2. Create a virtual environment and activate it:

   ```bash
   python -m venv .venv
   .venv\Scripts\activate   # Windows
   # source .venv/bin/activate   # Linux / macOS
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```


   For production set `DJANGO_DEBUG=False` and a strong `DJANGO_SECRET_KEY` in `.env`.

4. Run migrations and start the server:

   ```bash
   python manage.py migrate
   python manage.py runserver
   ```

5. Open in browser: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

## Environment Variables

| Variable            | Description                                      |
|---------------------|--------------------------------------------------|
| `DJANGO_SECRET_KEY` | Secret key (required when `DEBUG=False`)         |
| `DJANGO_DEBUG`      | `True` or `False` (default: `True`)              |
| `ALLOWED_HOSTS`     | Comma-separated hosts (e.g. `localhost,127.0.0.1`) |



## API

- **Categories**: `GET /api/categories/` — list all categories with book count  
- **Category detail**: `GET /api/categories/<slug>/`  
- **Books**: `GET /api/books/` — list books (optional query: `?category=<slug>`)  
- **Book detail**: `GET /api/books/<slug>/`  

Responses are JSON. Pagination: 20 items per page. Throttling: 100 requests/hour for anonymous users.

## Project Structure

```
BooksMarket/
├── config/           # Django settings, urls, wsgi
├── books_market/     # Main app: models, views, templates, static
├── api/              # REST API (DRF)
├── templates/        # Global templates (base, 404)
├── static/           # Global static (CSS, images)
├── media/            # User uploads (covers, files) — not in git
├── manage.py
├── requirements.txt

```

## License

MIT 
