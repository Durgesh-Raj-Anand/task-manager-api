# Task Manager REST API

A Django REST Framework API for managing tasks.

## Setup

1. Create a virtual environment and install dependencies:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. Copy `.env.example` to `.env` and fill in your database credentials:

```bash
cp .env.example .env
```

3. Create the PostgreSQL database:

```sql
CREATE DATABASE taskmanager_db;
```

4. Run migrations:

```bash
python manage.py migrate
```

5. Create a superuser:

```bash
python manage.py createsuperuser
```

6. Run the development server:

```bash
python manage.py runserver
```

## API Endpoints

*Coming soon.*

## Tech Stack

- Python
- Django
- Django REST Framework
- PostgreSQL
- django-filter
- django-environ
