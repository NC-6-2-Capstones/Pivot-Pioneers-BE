import requests
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import get_user_model, authenticate
from .models import PersonalityProfile
from .forms import PersonalityProfileForm
from .serializers import PersonalityProfileSerializer
from .models import (
    Goal, PersonalityProfile, RoadmapStep, Resource, AssessmentQuestion
)
from .serializers import (
    GoalSerializer, PersonalityProfileSerializer, RoadmapStepSerializer,
    ResourceSerializer, AssessmentQuestionSerializer, UserSerializer
)

from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

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


class GoalViewSet(viewsets.ModelViewSet):
    queryset = Goal.objects.all()
    serializer_class = GoalSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Goal.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['get'], url_path='roadmap')
    def roadmap(self, request, pk=None):
        try:
            goal = self.get_queryset().get(pk=pk)
        except Goal.DoesNotExist:
            return Response({'detail': 'Goal not found.'}, status=status.HTTP_404_NOT_FOUND)

        steps = goal.steps.all().order_by('order')
        serializer = RoadmapStepSerializer(steps, many=True)
        return Response(serializer.data)


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
    

class RoadmapStepViewSet(viewsets.ModelViewSet):
    serializer_class = RoadmapStepSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return RoadmapStep.objects.filter(goal__user=self.request.user)


class ResourceViewSet(viewsets.ModelViewSet):
    serializer_class = ResourceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Resource.objects.all()
        queryset = queryset.filter(goal__user=self.request.user)

        goal_id = self.request.query_params.get('goal_id')
        if goal_id is not None:
            queryset = queryset.filter(goal_id=goal_id)

        return queryset

class AssessmentQuestionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AssessmentQuestion.objects.all()
    serializer_class = AssessmentQuestionSerializer
    permission_classes = [permissions.AllowAny]


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]

@api_view(['POST'])
@permission_classes([AllowAny])
def login_token(request):
    username = request.data.get('username')
    password = request.data.get('password')
    
    user = authenticate(username=username, password=password)
    
    if user:
        token, created = Token.objects.get_or_create(user=user)
        serializer = UserSerializer(user)
        return Response({'token': token.key, 'user': serializer.data})
    
    return Response({'detail': 'Invalid credentials'}, status=400)

@api_view(['POST'])
@permission_classes([AllowAny])
def register_token(request):
    serializer = UserSerializer(data=request.data)
    
    if serializer.is_valid():
        user = get_user_model().objects.create_user(
            username=request.data['username'],
            email=request.data.get('email', ''),
            password=request.data['password']
        )
        token, created = Token.objects.get_or_create(user=user)
        return Response({'token': token.key, 'user': UserSerializer(user).data})
    
    return Response(serializer.errors, status=400)

@api_view(['GET'])
def user_profile(request):
    serializer = UserSerializer(request.user)
    return Response(serializer.data)