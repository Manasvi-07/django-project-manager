from django.db import models

class StatusChoice(models.TextChoices):
    TODO = 'todo', 'Todo'
    IN_PROGRESS = 'in_progress', 'In_progress'
    DONE = 'done', 'Done'

class PriorityChoice(models.TextChoices):
    HIGH = 'high', 'High'
    LOW = 'low', 'Low'
    MEDIUM = 'medium', 'Medium'
