from rest_framework.serializers import ModelSerializer, ValidationError, ReadOnlyField
from .models import Project, Task, TaskAttachment
from account.enums import RoleChoices

class ProjectSerializer(ModelSerializer):
    owner = ReadOnlyField(source="owner.id")

    class Meta:
        model = Project
        fields = ['id', 'title', 'description', 'deadline', 'owner', 'created_at', 'updated_at']


class TaskAttachmentSerializer(ModelSerializer):
    class Meta:
        model = TaskAttachment
        fields = ['id', 'task', 'file', 'image','uploaded_at']
        read_only_fields = ['id','uploaded_at', 'task']

class TaskSerializer(ModelSerializer):
    attachments = TaskAttachmentSerializer(many=True, read_only=True)
    created = ReadOnlyField(source="created.id")

    class Meta:
        model = Task
        fields = ['id', 'project','title', 'description', 'status', 'priority', 'assigned', 'created','due_date', 'created_at', 'updated_at', 'attachments']

    def validate_assigned(self, value):
        request = self.context['request']
        user = request.user

        for assigned_user in value:
            if assigned_user.role == RoleChoices.ADMIN:
                raise ValidationError("Tasks cannot assigned to admin user")

            if user.role == RoleChoices.MANAGER:
                if assigned_user == user:
                    raise ValidationError("Tasks cannot be assigned to manager users.")
                if assigned_user.role != RoleChoices.DEVELOPER:
                    raise ValidationError("Managers can only assign tasks to developer.")
            
            if user.role == RoleChoices.DEVELOPER:
                raise ValidationError("developer are not allowed to assign tasks.")
        return value