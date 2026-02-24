# Как залить проект на GitHub

## 1. Инициализация репозитория (если ещё не сделано)

```bash
cd d:\BooksMarket
git init
```

## 2. Добавить файлы и первый коммит

```bash
git add .
git status
git commit -m "Initial commit: Code Nest — BooksMarket Django project"
```

Перед `git add .` убедись, что в корне есть `.gitignore` — он исключает `.venv/`, `db.sqlite3`, `media/`, `staticfiles/`, `.env` и др., чтобы они не попали в репозиторий.

## 3. Создать репозиторий на GitHub

1. Зайди на [github.com](https://github.com) и войди в аккаунт.
2. Нажми **New repository** (или **+** → **New repository**).
3. Укажи имя (например, `BooksMarket` или `code-nest`).
4. Оставь репозиторий **пустым** (не ставь README, .gitignore, license — они уже есть или будут из проекта).
5. Нажми **Create repository**.

## 4. Подключить удалённый репозиторий и отправить код

Скопируй URL репозитория (HTTPS или SSH). Пример для HTTPS:

```bash
git remote add origin https://github.com/ТВОЙ_ЛОГИН/BooksMarket.git
git branch -M main
git push -u origin main
```

Если используешь SSH:

```bash
git remote add origin git@github.com:ТВОЙ_ЛОГИН/BooksMarket.git
git branch -M main
git push -u origin main
```

Подставь вместо `ТВОЙ_ЛОГИН` свой логин GitHub и вместо `BooksMarket` — имя репозитория, если назвал иначе.

## 5. Дальнейшая работа

После первого пуша:

```bash
git add .
git commit -m "Описание изменений"
git push
```

## Важно

- **Секреты:** В коде не должно быть паролей и `SECRET_KEY` от production. В проекте ключ берётся из переменной окружения `DJANGO_SECRET_KEY`; в репозитории можно оставить только пример в `.env.example` (без реальных значений).
- **База:** `db.sqlite3` в `.gitignore` — в репозиторий не попадёт. Для production используй отдельную БД (PostgreSQL и т.п.).
- **Медиа:** Папка `media/` в `.gitignore` — загруженные файлы не коммитятся. На сервере их нужно хранить отдельно или собирать после деплоя.
