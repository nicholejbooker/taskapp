from django.contrib import admin

from .models import SubTask, Task


class SubTaskInline(admin.TabularInline):
    model = SubTask
    extra = 1
    fields = ("label", "is_done", "order")


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("title", "priority", "due_date", "is_done", "created_at")
    list_filter = ("is_done", "priority")
    search_fields = ("title", "notes")
    ordering = ("is_done", "due_date", "-created_at")
    inlines = [SubTaskInline]
