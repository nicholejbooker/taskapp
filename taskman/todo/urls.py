from django.urls import path

from . import views

app_name = "todo"

urlpatterns = [
    path("", views.task_list, name="task_list"),
    path("calendar/", views.calendar_view, name="calendar"),
    path("tasks/<int:pk>/toggle/", views.task_toggle, name="task_toggle"),
    path("tasks/<int:pk>/edit/", views.task_edit, name="task_edit"),
    path("tasks/<int:pk>/delete/", views.task_delete, name="task_delete"),
    path("subtasks/<int:pk>/toggle/", views.subtask_toggle, name="subtask_toggle"),
    path("subtasks/<int:pk>/delete/", views.subtask_delete, name="subtask_delete"),
]
