from django.contrib import admin
from .models import Task, TaskAttachment

class TaskAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'get_assigned',
        'created',
        'priority',
        'status',
        'due_date',
        'completed',
    )
    list_filter = ('priority', 'status', 'completed')
    search_fields = ('title', 'assigned__email', 'created__email')
    ordering = ('-due_date',)

    def get_assigned(self, obj):
        return ",".join([user.email for user in obj.assigned.all()])
    get_assigned.short_description = "Assigned_to"
    
class TaskAttachmentAdmin(admin.ModelAdmin):
    list_display = ('task', 'uploaded_at', 'file','image')

admin.site.register(Task, TaskAdmin)
admin.site.register(TaskAttachment, TaskAttachmentAdmin)