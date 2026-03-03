from datetime import date, timedelta
import calendar

from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods, require_POST

from .forms import TaskForm
from .models import SubTask, Task


PREDEFINED_TEMPLATES = [
    {
        "key": "shopping",
        "name": "Shopping",
        "items": ["Carrots", "Toilet paper", "Bananas"],
    },
    {
        "key": "errands",
        "name": "Errands",
        "items": ["Post office", "Bank", "Pharmacy"],
    },
    {
        "key": "weekly_review",
        "name": "Weekly review",
        "items": ["Scan calendar", "Clear inbox", "Plan next week"],
    },
]


@require_http_methods(["GET", "POST"])
def task_list(request):
    # Handle creation from a predefined template
    if request.method == "POST" and request.POST.get("template_key"):
        key = request.POST.get("template_key")
        template = next((t for t in PREDEFINED_TEMPLATES if t["key"] == key), None)
        if template is not None:
            items = [
                value.strip()
                for value in request.POST.getlist("template_items")
                if value.strip()
            ]
            if not items:
                items = template["items"]

            task = Task.objects.create(title=template["name"])
            SubTask.objects.bulk_create(
                [
                    SubTask(task=task, label=label, order=idx)
                    for idx, label in enumerate(items)
                ]
            )
            return redirect("todo:task_list")

    # Default: normal user-entered task creation
    if request.method == "POST":
        form = TaskForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("todo:task_list")
    else:
        form = TaskForm()

    tasks = Task.objects.prefetch_related("subtasks").all()
    return render(
        request,
        "todo/task_list.html",
        {
            "form": form,
            "templates": PREDEFINED_TEMPLATES,
            "tasks_todo": [t for t in tasks if not t.is_done],
            "tasks_done": [t for t in tasks if t.is_done],
        },
    )


@require_POST
def task_toggle(request, pk: int):
    task = get_object_or_404(Task, pk=pk)
    # For recurring tasks, advance to the next due date instead of just marking done
    next_date = task.next_due_date()
    if next_date:
        task.due_date = next_date
        task.is_done = False
        task.save(update_fields=["due_date", "is_done", "updated_at"])
    else:
        task.is_done = not task.is_done
        task.save(update_fields=["is_done", "updated_at"])
    return redirect("todo:task_list")


@require_http_methods(["GET", "POST"])
def task_edit(request, pk: int):
    task = get_object_or_404(Task, pk=pk)
    if request.method == "POST":
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            return redirect("todo:task_list")
    else:
        form = TaskForm(instance=task)
    return render(request, "todo/task_edit.html", {"form": form, "task": task})


@require_POST
def task_delete(request, pk: int):
    task = get_object_or_404(Task, pk=pk)
    task.delete()
    return redirect("todo:task_list")


@require_POST
def subtask_toggle(request, pk: int):
    subtask = get_object_or_404(SubTask, pk=pk)
    subtask.is_done = not subtask.is_done
    subtask.save(update_fields=["is_done"])

    # Optionally keep parent task in sync with subtasks
    task = subtask.task
    has_open_subtasks = task.subtasks.filter(is_done=False).exists()
    if task.is_done and has_open_subtasks:
        task.is_done = False
        task.save(update_fields=["is_done", "updated_at"])
    elif not task.is_done and not has_open_subtasks:
        task.is_done = True
        task.save(update_fields=["is_done", "updated_at"])

    return redirect("todo:task_list")


@require_POST
def subtask_delete(request, pk: int):
    subtask = get_object_or_404(SubTask, pk=pk)
    task = subtask.task
    subtask.delete()

    has_open_subtasks = task.subtasks.filter(is_done=False).exists()
    has_subtasks = task.subtasks.exists()

    if has_subtasks and not has_open_subtasks and not task.is_done:
        task.is_done = True
        task.save(update_fields=["is_done", "updated_at"])
    elif has_open_subtasks and task.is_done:
        task.is_done = False
        task.save(update_fields=["is_done", "updated_at"])

    return redirect("todo:task_list")


@require_http_methods(["GET"])
def calendar_view(request):
    today = date.today()
    try:
        year = int(request.GET.get("year", today.year))
        month = int(request.GET.get("month", today.month))
        first_of_month = date(year, month, 1)
    except Exception:
        first_of_month = date(today.year, today.month, 1)
        year = first_of_month.year
        month = first_of_month.month

    cal = calendar.Calendar(firstweekday=6)  # Sunday as first day
    weeks = cal.monthdatescalendar(year, month)

    range_start = weeks[0][0]
    range_end = weeks[-1][-1]

    tasks = (
        Task.objects.filter(
            is_done=False,
            due_date__isnull=False,
            due_date__gte=range_start,
            due_date__lte=range_end,
        )
        .only("id", "title", "due_date")
        .order_by("due_date", "title")
    )

    tasks_by_date = {}
    for t in tasks:
        tasks_by_date.setdefault(t.due_date, []).append(t)

    weeks_with_tasks = []
    for week in weeks:
        row = []
        for day in week:
            row.append(
                {
                    "date": day,
                    "is_other_month": day.month != month,
                    "tasks": tasks_by_date.get(day, []),
                }
            )
        weeks_with_tasks.append(row)

    prev_month_date = (first_of_month - timedelta(days=1)).replace(day=1)
    next_month_date = (first_of_month + timedelta(days=31)).replace(day=1)

    return render(
        request,
        "todo/calendar.html",
        {
            "weeks": weeks_with_tasks,
            "year": year,
            "month": month,
            "month_name": calendar.month_name[month],
            "prev_year": prev_month_date.year,
            "prev_month": prev_month_date.month,
            "next_year": next_month_date.year,
            "next_month": next_month_date.month,
            "today": today,
        },
    )
