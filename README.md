# Task Manager

A Django-based task management app with to-do lists, templates, subtasks, recurring tasks, and a calendar view.

## Features

- **Custom tasks** – Add tasks with title, notes, priority, due date, and time
- **Template-based tasks** – Quick add from predefined templates (Shopping, Errands, Weekly review) with customizable item lists
- **Subtasks** – Create sublists and mark items off individually (e.g., shopping: carrots, toilet paper, bananas)
- **Recurring tasks** – Set tasks to repeat daily, weekly, or monthly on a specific weekday (e.g., groomer's appointment the first Thursday of each month)
- **Calendar view** – See tasks by due date in a monthly calendar

## Requirements

- [Docker](https://docs.docker.com/get-docker/) and Docker Compose

## Setup with Docker

1. Clone the repository:
   ```bash
   git clone https://github.com/nicholejbooker/taskapp.git
   cd taskapp
   ```

2. Build and run:
   ```bash
   docker compose up --build
   ```

3. Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/) in your browser.

Migrations run automatically on container start. The SQLite database is stored in `taskman/db.sqlite3` and persists between runs.

## Setup with Python (alternative)

- Python 3.10+
- Django 6.0+

1. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   # Windows: venv\Scripts\activate
   # macOS/Linux: source venv/bin/activate
   ```
2. `pip install -r requirements.txt`
3. `cd taskman && python manage.py migrate && python manage.py runserver`

## Project structure

```
taskapp/
├── taskman/           # Django project
│   ├── taskman/       # Project settings
│   └── todo/          # Todo app (models, views, templates)
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## Admin

Access the Django admin at [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/). Create a superuser first:

```bash
# With Docker:
docker compose exec web python manage.py createsuperuser

# With Python/venv:
cd taskman && python manage.py createsuperuser
```
