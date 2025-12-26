from django.db import models
from account.models import CustomUser
from task.enums import StatusChoice, PriorityChoice

class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class Project(BaseModel):
    title = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    deadline = models.DateTimeField()
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="project_owned")

    def __str__(self):
        return self.title

class Task(BaseModel):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="tasks")
    title = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=50, choices=StatusChoice, default=StatusChoice.TODO)
    priority = models.CharField(max_length=50, choices=PriorityChoice, default=PriorityChoice.MEDIUM)
    assigned = models.ManyToManyField(CustomUser,related_name='assigned_tasks')
    created = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='created_tasks')
    completed = models.BooleanField(default=False)
    due_date = models.DateTimeField()

    def __str__(self):
        return f"{self.title}({self.project.title})"
    
class TaskAttachment(models.Model):
    task = models.ForeignKey(Task, related_name='attachments', on_delete=models.CASCADE)
    file = models.FileField(upload_to='task_attachments/', null=True, blank=True)
    image = models.ImageField(upload_to='task_images/', null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Attachment for {self.task.title}"