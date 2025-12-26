from django.urls import reverse
from account.models import CustomUser
from rest_framework.test import APIClient
from account.enums import RoleChoices
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

@pytest.mark.django_db
def test_user_signup(api_client, create_user):
    admin, _ = create_user(RoleChoices.ADMIN)  

    api_client.force_authenticate(user=admin)

    url = reverse("create_user")
    payload = {
        "email": "newuser@example.com",
        "password": "StrongPass123",
        "role": RoleChoices.DEVELOPER,
    }
    resp = api_client.post(url, payload, format="json")
    assert resp.status_code == 201
    assert CustomUser.objects.filter(email="newuser@example.com").exists()

@pytest.mark.django_db
def test_user_login(api_client, create_user):
    user, pwd = create_user(RoleChoices.DEVELOPER)
    url = reverse("user_login")  
    payload = {
        "email": user.email,
        "password": pwd,
    }
    resp = api_client.post(url, payload, format="json")
    assert resp.status_code == 200
    assert "access" in resp.data 


@pytest.mark.django_db
def test_invalid_login(api_client):
    url = reverse("user_login")
    payload = {"email": "fake@example.com", "password": "wrong"}
    resp = api_client.post(url, payload, format="json")
    assert resp.status_code == 401