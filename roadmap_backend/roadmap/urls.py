from django.urls import path
from .views import home_view, login_view, register_view, logout_view, login_token, register_token, user_profile, view_or_edit_profile, submit_assessment, get_personality_profile, get_assessment_questions




urlpatterns = [
    path('', home_view, name='home'),
    path('login/', login_view, name='login'),
    path('register/', register_view, name='register'),
    path('logout/', logout_view, name='logout'),
    path('profile/', view_or_edit_profile, name='view_or_edit_profile'),
    path('api/auth/login/', login_token, name='api_login'),
    path('api/auth/register/', register_token, name='api_register'),
    path('api/auth/me/', user_profile, name='user_profile'),
    path('api/assessments/questions/', get_assessment_questions, name='assessment_questions'),
    path('api/assessments/submit/', submit_assessment, name='submit_assessment'),
    path('api/assessments/profile/', get_personality_profile, name='personality_profile'),
]
