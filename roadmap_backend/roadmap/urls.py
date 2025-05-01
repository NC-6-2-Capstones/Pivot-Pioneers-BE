from django.urls import path
from .views import login_view, register_view, logout_view, view_or_edit_profile 


urlpatterns = [
    path('login/', login_view, name='login'),
    path('register/', register_view, name='register'),
    path('logout/', logout_view, name='logout'),
    path('profile/', view_or_edit_profile, name='view_or_edit_profile'),
]
