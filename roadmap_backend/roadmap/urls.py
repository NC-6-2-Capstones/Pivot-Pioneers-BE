from django.urls import path


from .views import login_view, register_view, logout_view, login_token, register_token, user_profile, view_or_edit_profile


urlpatterns = [
    path('login/', login_view, name='login'),
    path('register/', register_view, name='register'),
    path('logout/', logout_view, name='logout'),
    path('profile/', view_or_edit_profile, name='view_or_edit_profile'),
    path('api/auth/login/', login_token, name='api_login'),
    path('api/auth/register/', register_token, name='api_register'),
    path('api/auth/me/', user_profile, name='user_profile'),
]
