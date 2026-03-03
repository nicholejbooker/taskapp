from datetime import date, timedelta
import calendar

from django.db import models


class Task(models.Model):
    class Priority(models.IntegerChoices):
        LOW = 1, "Low"
        MEDIUM = 2, "Medium"
        HIGH = 3, "High"

    class Recurrence(models.TextChoices):
        NONE = "none", "Does not repeat"
        DAILY = "daily", "Daily"
        WEEKLY = "weekly", "Weekly on this day"
        MONTHLY_WEEKDAY = "monthly_weekday", "Monthly on this weekday"

    title = models.CharField(max_length=200)
    notes = models.TextField(blank=True)
    priority = models.IntegerField(choices=Priority.choices, default=Priority.MEDIUM)
    due_date = models.DateField(null=True, blank=True)
    due_time = models.TimeField(null=True, blank=True)
    recurrence = models.CharField(
        max_length=32, choices=Recurrence.choices, default=Recurrence.NONE
    )
    is_done = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["is_done", "due_date", "-created_at"]

    def __str__(self) -> str:
        return self.title

    def next_due_date(self) -> date | None:
        if not self.due_date or self.recurrence == self.Recurrence.NONE:
            return None

        if self.recurrence == self.Recurrence.DAILY:
            return self.due_date + timedelta(days=1)

        if self.recurrence == self.Recurrence.WEEKLY:
            return self.due_date + timedelta(weeks=1)

        if self.recurrence == self.Recurrence.MONTHLY_WEEKDAY:
            current = self.due_date
            weekday = current.weekday()
            nth = (current.day - 1) // 7  # 0-based occurrence of weekday in month

            # Move to first of next month
            year = current.year + 1 if current.month == 12 else current.year
            month = 1 if current.month == 12 else current.month + 1
            first_next = date(year, month, 1)

            # First occurrence of that weekday in next month
            offset = (weekday - first_next.weekday()) % 7
            day = 1 + offset + nth * 7

            last_day = calendar.monthrange(year, month)[1]
            if day > last_day:
                # Clamp to last occurrence of that weekday in the month
                day = last_day
                while date(year, month, day).weekday() != weekday and day > 1:
                    day -= 1

            return date(year, month, day)

        return None


class SubTask(models.Model):
    task = models.ForeignKey(Task, related_name="subtasks", on_delete=models.CASCADE)
    label = models.CharField(max_length=200)
    is_done = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self) -> str:
        return self.label
