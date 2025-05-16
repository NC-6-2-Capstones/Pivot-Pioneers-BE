from django.urls import path
from .views import home_view, login_view, register_view, logout_view, login_token, register_token, user_profile, view_or_edit_profile, submit_assessment, get_personality_profile, get_assessment_questions, goal_list_create, goal_detail, goal_roadmap, get_user_achievements, get_user_points, add_points_for_goal, check_new_achievements




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
    path('api/goals/', goal_list_create, name='goal-list-create'),
    path('api/goals/<int:pk>/', goal_detail, name='goal-detail'),
    path('api/goals/<int:pk>/roadmap/', goal_roadmap, name='goal-roadmap'),
    path('api/gamification/points/', get_user_points, name='user-points'),
    path('api/gamification/add-points/', add_points_for_goal, name='add-points'),
    path('api/gamification/achievements/', get_user_achievements, name='user-achievements'),
    path('api/gamification/check-achievements/', check_new_achievements, name='check-achievements'),


]
