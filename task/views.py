from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, CreateAPIView
from rest_framework.exceptions import PermissionDenied
from rest_framework.parsers import MultiPartParser, FormParser
from .models import Project, Task, TaskAttachment
from task.serializers import ProjectSerializer, TaskSerializer, TaskAttachmentSerializer
from task.permissions import IsAdminOrManager, IsAdminManagerOrTaskOwner
from account.enums import RoleChoices
import logging
from task.tasks import send_mail_task_notification
from task.utils import notify_task_update
from drf_spectacular.utils import extend_schema

logger = logging.getLogger("task")

class ProjectCreateView(ListCreateAPIView):
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]
    queryset = Project.objects.all()

    def get_queryset(self):
        user = self.request.user
        if user.role == RoleChoices.ADMIN:
            return Project.objects.all()
        return Project.objects.filter(owner=user)
    
    @extend_schema(request=ProjectSerializer, responses= ProjectSerializer)
    def perform_create(self, serializer):
        if self.request.user.role == RoleChoices.DEVELOPER:
            raise PermissionDenied("Developer can not create project")
        serializer.save(owner=self.request.user)

class ProjectDetailsView(RetrieveUpdateDestroyAPIView):
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]
    queryset = Project.objects.all()

class TaskCreateView(ListCreateAPIView):
    serializer_class = TaskSerializer
    queryset = Task.objects.all()

    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["project", "due_date", "status", "priority"]
    ordering_fields = ["due_date", "priority", "created_at"]
    search_fields = ['title', "description", "assigned__email"]

    def get_queryset(self):
        user = self.request.user
        queryset = Task.objects.select_related("created", "project").prefetch_related("assigned").order_by("-created_at")

        if user.role == RoleChoices.ADMIN:
            logger.info(f"Admin {user.email} view all task")
            return queryset
        elif user.role == RoleChoices.MANAGER:
            logger.info(f"Manager {user.email} show only owned task created")
            owned= queryset.filter(project__owner=user)
            created = queryset.filter(created=user)
            assigned = queryset.filter(assigned=user)
            return (owned | created | assigned).distinct()
        
        logger.info(f"Developer {user.email} show only owned assigned task")
        return queryset.filter(assigned=user).distinct()

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAuthenticated(), IsAdminOrManager()]
        return [IsAuthenticated()]
    
    @extend_schema(request=TaskSerializer, responses= TaskSerializer)
    def perform_create(self, serializer):
        task = serializer.save(created=self.request.user)
        assigned_users = serializer.validated_data.get('assigned', [])
        task.assigned.set(assigned_users)
        assigned_emails = ", ".join([u.email for u in task.assigned.all()]) if task.assigned.exists() else "Unassigned"
        logger.info(
            f"Task created: {task.title} "
            f"(Project: {task.project.title if task.project else 'No Project'}, "
            f"Assigned: {assigned_emails if assigned_emails else 'Unassigned'}) "
            f"created {self.request.user.email}"
        )
        send_mail_task_notification.delay(task.id)
        notify_task_update(task)        
        return task

class TaskDetailsView(RetrieveUpdateDestroyAPIView):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated,IsAdminManagerOrTaskOwner]
    queryset = Task.objects.all()

class TaskAttachmentUploadView(CreateAPIView):
    queryset = TaskAttachment.objects.all()
    serializer_class = TaskAttachmentSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    @extend_schema(request=TaskAttachmentSerializer, responses=TaskAttachmentSerializer)
    def perform_create(self, serializer):
        task_id = self.kwargs.get("task_id")
        task = Task.objects.get(id=task_id)
        serializer.save(task=task)