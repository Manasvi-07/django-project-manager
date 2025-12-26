from django.urls import path
from .views import ProjectCreateView, ProjectDetailsView 
from .views import TaskCreateView, TaskDetailsView, TaskAttachmentUploadView

urlpatterns = [
    # Project URLs
    path('projects/create/', ProjectCreateView.as_view(), name="project_create_list"),
    path('projects/details/<int:pk>/', ProjectDetailsView.as_view(), name="project_details_update_delete"),
    # Task URLs
    path('tasks/create/', TaskCreateView.as_view(), name="task_create_list"),
    path('tasks/details/<int:pk>/', TaskDetailsView.as_view(), name="task_details_update_delete"),
    path('tasks/attachments/<int:task_id>/', TaskAttachmentUploadView.as_view(), name="task_file_attachments")
]