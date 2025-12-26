from django.urls import path
from account.views import UserSignupView, AdminSignupView, UserRoleUpdateView, UserProfileUpdateView, UserListView

urlpatterns = [
    path('signup/admin/', AdminSignupView.as_view(), name="admin_signup"),
    path('signup/user/', UserSignupView.as_view(), name="create_user"),
    path('user/', UserListView.as_view(), name="user_list"),
    path('user/profile/', UserProfileUpdateView.as_view(), name="user_update_profile"),
    path('user/role/<int:pk>/', UserRoleUpdateView.as_view(), name="user_role_update"),
]
