from django.urls import reverse
from rest_framework.test import APIClient
from account.enums import RoleChoices
from account.models import CustomUser
from django.utils import timezone
import datetime
from task.models import Project, Task
import pytest

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def create_user(db):
    def make_user(role=RoleChoices.DEVELOPER, email=None, password="StrongPass123"):
        email = email or f"{role.lower()}@example.com"
        user = CustomUser.objects.create_user(
            email=email,
            password=password,
            role=role
        )
        return user, password
    return make_user

# ---------------- Project API Tests ----------------

@pytest.mark.django_db
def test_list_projects(api_client, create_user):
    admin, _pwd = create_user(RoleChoices.ADMIN)
    Project.objects.create(title="P1", description="Test1", deadline=timezone.make_aware(datetime.datetime(2025, 12, 31)), owner=admin)
    Project.objects.create(title="P2", description="Test2", deadline=timezone.make_aware(datetime.datetime(2025, 12, 31)), owner=admin)

    api_client.force_authenticate(user=admin)
    url = reverse("project_create_list")
    resp = api_client.get(url)
    assert resp.status_code == 200
    assert len(resp.data) >= 2


@pytest.mark.django_db
def test_update_project(api_client, create_user):
    admin, _pwd = create_user(RoleChoices.ADMIN)
    project = Project.objects.create(title="Old", description="Test", deadline=timezone.make_aware(datetime.datetime(2025, 12, 31)), owner=admin)

    api_client.force_authenticate(user=admin)
    url = reverse("project_details_update_delete", args=[project.id])
    payload = {"title": "Updated", "description": "Updated", "deadline": "2026-01-01"}
    resp = api_client.put(url, payload, format="json")
    assert resp.status_code == 200
    project.refresh_from_db()
    assert project.title == "Updated"


@pytest.mark.django_db
def test_delete_project(api_client, create_user):
    admin, _pwd = create_user(RoleChoices.ADMIN)
    project = Project.objects.create(title="DeleteMe", description="Test", deadline=timezone.make_aware(datetime.datetime(2025, 12, 31)), owner=admin)

    api_client.force_authenticate(user=admin)
    url = reverse("project_details_update_delete", args=[project.id])
    resp = api_client.delete(url)
    assert resp.status_code == 204
    assert not Project.objects.filter(id=project.id).exists()


# ---------------- Task API Tests ----------------

@pytest.mark.django_db
def test_list_tasks(api_client, create_user):
    manager, _pwd = create_user(RoleChoices.MANAGER)
    dev, _ = create_user(RoleChoices.DEVELOPER)
    aware_due = timezone.make_aware(datetime.datetime(2025, 12, 31))

    project = Project.objects.create(title="P1", description="Test", deadline=timezone.make_aware(datetime.datetime(2025, 12, 31)), owner=manager)

    Task.objects.create(project=project, title="T1", description="D1", status="todo", priority="low", assigned=dev, due_date=aware_due)
    Task.objects.create(project=project, title="T2", description="D2", status="in_progress", priority="high", assigned=dev, due_date=aware_due)

    api_client.force_authenticate(user=manager)
    url = reverse("task_create_list")
    resp = api_client.get(url)
    assert resp.status_code == 200
    assert len(resp.data) >= 2


@pytest.mark.django_db
def test_update_task(api_client, create_user):
    manager, _pwd = create_user(RoleChoices.MANAGER)
    dev, _ = create_user(RoleChoices.DEVELOPER)
    aware_due = timezone.make_aware(datetime.datetime(2025, 12, 31))

    project = Project.objects.create(title="P1", description="Test", deadline=timezone.make_aware(datetime.datetime(2025, 12, 31)), owner=manager)

    task = Task.objects.create(
        project=project,
        title="OldTask",
        description="Test",
        status="todo",
        priority="medium",
        assigned=dev,
        due_date=aware_due
    )

    api_client.force_authenticate(user=manager)
    url = reverse("task_details_update_delete", args=[task.id])
    payload = {
        "project": project.id, 
        "title": "Updated Task",
        "description": "Updated desc",
        "status": "done",
        "priority": "high",
        "assigned": dev.id,
        "due_date": aware_due.isoformat()
    }
    resp = api_client.patch(url, payload, format="json")
    assert resp.status_code == 200
    task.refresh_from_db()
    assert task.title == "Updated Task"


@pytest.mark.django_db
def test_delete_task(api_client, create_user):
    manager, _pwd = create_user(RoleChoices.MANAGER)
    dev, _ = create_user(RoleChoices.DEVELOPER)
    aware_due = timezone.make_aware(datetime.datetime(2025, 12, 31))

    project = Project.objects.create(title="P1", description="Test", deadline=timezone.make_aware(datetime.datetime(2025, 12, 31)), owner=manager)

    task = Task.objects.create(project=project, title="DeleteMe", description="Test", status="todo", priority="low", assigned=dev, due_date=aware_due)

    api_client.force_authenticate(user=manager)
    url = reverse("task_details_update_delete", args=[task.id])
    resp = api_client.delete(url)
    assert resp.status_code == 204
    assert not Task.objects.filter(id=task.id).exists()