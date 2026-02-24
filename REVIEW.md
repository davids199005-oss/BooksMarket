# Обзор проекта BooksMarket (Code Nest)

## 1. Архитектура

### Общая структура
- **Django-проект** с разделением на приложения: `config` (настройки, корневые URL), `books_market` (каталог книг, HTML-страницы), `api` (REST API).
- **Маршрутизация**: корневые URL в `config/urls.py`, приложения подключаются через `include()` — чёткое разделение зон ответственности.
- **Шаблоны**: общий `templates/base.html`, шаблоны приложения в `books_market/templates/books_market/` — соответствует рекомендациям Django (APP_DIRS + DIRS).
- **Статика**: глобальная в `static/`, статика приложения в `books_market/static/books_market/` — корректно для `collectstatic`.

### Плюсы
- Разделение веб-интерфейса и API по приложениям.
- Использование `slug` для человекочитаемых URL.
- `select_related` в представлениях для уменьшения числа запросов к БД.
- ReadOnly API (ViewSet) для публичного каталога — логично.

### Рекомендации
- При росте API можно вынести сериализаторы в отдельный модуль `api/serializers/` с разбиением по ресурсам.
- Для отображения активной ссылки в навигации можно использовать тег шаблона или context processor с `request.resolver_match.url_name`.

---

## 2. Безопасность

### Реализовано
- **SECRET_KEY**: задаётся через `DJANGO_SECRET_KEY`; при `DEBUG=False` без ключа — `ImproperlyConfigured`.
- **ALLOWED_HOSTS**: из переменной окружения или значения по умолчанию при DEBUG.
- **DEBUG**: из `DJANGO_DEBUG` (env).
- В **production** включены: `SECURE_SSL_REDIRECT`, secure cookies, HSTS, XSS filter, X-Frame-Options, NOSNIFF.
- **Пароли**: используются стандартные валидаторы Django.
- **CSRF**: включён `CsrfViewMiddleware`.
- **Файлы**: `FileExtensionValidator` для полей файлов книг (только `pdf`, `epub`, `mobi`); пути загрузки заданы в коде (`books/covers/`, `books/files/`), без пользовательского ввода.
- **API**: throttling для анонимов (100/hour).

### Рекомендации
- **MEDIA**: в production раздавать медиа через веб-сервер (nginx/apache), а не через Django. В DEBUG раздача через `static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)` — нормально.
- **ImageField**: сейчас ограничений по типам изображений нет. При риске загрузки вредоносных файлов можно добавить валидацию (например, через Pillow) или ограничить расширения.
- Убедиться, что в production заданы `ALLOWED_HOSTS` и `DJANGO_SECRET_KEY` (например, через `.env` и не коммитить `.env` в репозиторий).

---

## 3. Расположение и хранение файлов

### Текущая схема
```
BooksMarket/
├── config/           # Настройки проекта, urls, wsgi
├── books_market/     # Приложение каталога (models, views, urls, admin, templates, static)
├── api/              # REST API (views, urls, serializers)
├── templates/        # Глобальные шаблоны (base.html, 404.html)
├── static/           # Глобальная статика (css/base.css, img/)
├── media/            # Загрузки пользователей (books/covers/, books/files/) — в .gitignore
├── staticfiles/      # Результат collectstatic для production — в .gitignore
```

### Оценка
- Разделение статики по приложениям и глобальной статике — правильное.
- `MEDIA_ROOT` и `MEDIA_URL` заданы; для production добавлен `STATIC_ROOT` для `collectstatic`.
- В `.gitignore` добавлены `media/` и `staticfiles/`, чтобы не коммитить загрузки и собранную статику.

### Замечания
- Файл БД `db.sqlite3` обычно в корне проекта — для production рекомендуется отдельная БД (PostgreSQL и т.п.) и не хранить файл БД в репозитории (уже в `.gitignore`).

---

## 4. Чистота и читаемость кода

### Сделано по результатам проверки
1. **404.html**: бренд исправлен с «BookShelf» на «Code Nest»; добавлены классы для стилей (`.error-page`, `.error-page-title`, `.error-page-link` и т.д.) без инлайн-стилей.
2. **base.css**: добавлены стили для страницы ошибки (`.error-page-*`).
3. **settings.py**: добавлен `STATIC_ROOT = BASE_DIR / 'staticfiles'` для production.
4. **models.py**:
   - Вынесена общая логика генерации уникального slug в функцию `_generate_unique_slug()` — убрано дублирование между `Category` и `Book`.
   - Для модели `Book` добавлен `__str__` для удобства в админке и shell.
   - Имена и форматирование приведены к единому стилю (в т.ч. кавычки для строк в полях).

### Общая оценка
- **views**: короткие функции, явные имена, разделение логики и шаблонов.
- **urls**: именованные маршруты, понятная структура.
- **serializers**: переиспользуемая `_absolute_uri()`, разделение list/detail сериализаторов.
- **admin**: адекватные `list_display`, `list_filter`, `search_fields`, без лишней логики.
- **Шаблоны**: наследование от `base.html`, блоки `extra_css`/`content`, без инлайн-стилей, единый бренд «Code Nest».

### Рекомендации на будущее
- Добавить type hints в views и serializers где это улучшит читаемость.
- При появлении форм — вынести валидацию в `forms.py` или сериализаторы, не дублировать в view.
- Рассмотреть вынос констант (например, лимитов throttling, списка расширений файлов) в `settings` или константы модуля.

---

## Краткий чек-лист

| Аспект | Статус |
|--------|--------|
| Разделение приложений | OK |
| URL по slug | OK |
| Секреты из env | OK |
| Production security settings | OK |
| Валидация загружаемых файлов | OK (расширения) |
| STATIC_ROOT для production | Добавлен |
| Дублирование кода (slug) | Устранено |
| 404 бренд и стили | Исправлено |
| .gitignore | Добавлен |

Проект приведён в порядок с точки зрения архитектуры, безопасности, структуры файлов и читаемости кода; внесённые правки зафиксированы в этом обзоре.
