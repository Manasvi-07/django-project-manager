from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

def notify_task_update(task):
    created = task.created
    assigned_users = task.assigned.all()
    channel_layer = get_channel_layer()

    payload = {
        "type": "task_update",
        "data": {
            "id": task.id,
            "title": task.title,
            "status": task.status,
            "assigned": ", ".join([u.email for u in assigned_users]) if assigned_users else None,
            "created": created.email if created else None,
        },
    }
    print("Preparing to notify via WebSocket")

    if created:
        group_name = f"user_{created.id}"
        print(f"[Websocket Notify] Sending update to group: {group_name}")
        async_to_sync(channel_layer.group_send)(group_name, payload)

    for user in assigned_users:
        group_name = f"user_{user.id}"
        print(f"[Websocket Notify] Sending update to group: {group_name}")
        async_to_sync(channel_layer.group_send)(group_name, payload)
            