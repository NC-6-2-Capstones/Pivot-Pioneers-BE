import requests
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import get_user_model
from .models import PersonalityProfile
from .forms import PersonalityProfileForm
from .serializers import PersonalityProfileSerializer

from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.decorators import action

# Create your views here.
User = get_user_model()

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('post_list')
    else:
        form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    return redirect('login')

def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('post_list')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})


@login_required
def view_or_edit_profile(request):
    try:
        profile = request.user.personality_profile
    except PersonalityProfile.DoesNotExist:
        profile = None

    if request.method == 'POST':
        form = PersonalityProfileForm(request.POST, instance=profile)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()
            return redirect('view_or_edit_profile')  
    else:
        form = PersonalityProfileForm(instance=profile)

    return render(request, 'profile/edit_profile.html', {'form': form, 'profile': profile})


class PersonalityProfileViewSet(viewsets.ModelViewSet):
    serializer_class = PersonalityProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return PersonalityProfile.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'], url_path='my-profile')
    def my_profile(self, request):
        profile = PersonalityProfile.objects.filter(user=request.user).first()
        if not profile:
            return Response({'detail': 'No profile found.'}, status=404)
        serializer = self.get_serializer(profile)
        return Response(serializer.data)