import requests
from django.http import JsonResponse
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import get_user_model, authenticate
from django.contrib import messages
from django.utils.timezone import now, timedelta
from .models import PersonalityProfile
from .forms import PersonalityProfileForm
from .serializers import PersonalityProfileSerializer
from .models import (
    Goal, PersonalityProfile, RoadmapStep, Resource, AssessmentQuestion, AssessmentAnswer,UserPoints, Achievement, UserAchievement
)
from .serializers import (
    GoalSerializer, PersonalityProfileSerializer, RoadmapStepSerializer,
    ResourceSerializer, AssessmentQuestionSerializer, UserSerializer, AchievementSerializer, UserAchievementSerializer, UserPointsSerializer
)

from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView

# Create your views here.
User = get_user_model()

def home_view(request):
    return render(request, 'home.html')

def ask_gemini(request):
    prompt = request.GET.get("prompt", "")

    headers = {
        "Authorization": f"Bearer {settings.GEMINI_API_KEY}",
    }

    response = requests.post("https://api.gemini.com/...", headers=headers, json={"prompt": prompt})
    return JsonResponse(response.json())

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('view_or_edit_profile')
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
            return redirect('view_or_edit_profile')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})


@login_required
def view_or_edit_profile(request):
    try:
        profile = request.user.personality_profile
    except PersonalityProfile.DoesNotExist:
        profile = None

    retry_key = 'profile_retry_count'
    last_attempt_key = 'profile_last_attempt'
    retry_count = request.session.get(retry_key, 0)
    last_attempt_time = request.session.get(last_attempt_key)

    if last_attempt_time:
        elapsed = now() - now().fromisoformat(last_attempt_time)
        if elapsed > timedelta(minutes=10):
            retry_count = 0
            request.session[retry_key] = 0

    if request.method == 'POST':
        if retry_count >= 5:
            messages.error(request, '⚠️ Max retry limit reached. Please try again later.')
        else:
            form = PersonalityProfileForm(request.POST, instance=profile)
            if form.is_valid():
                profile = form.save(commit=False)
                profile.user = request.user
                profile.save()
                messages.success(request, '✅ Profile updated successfully.')
                request.session[retry_key] = 0  
                request.session[last_attempt_key] = now().isoformat()
            else:
                retry_count += 1
                request.session[retry_key] = retry_count
                request.session[last_attempt_key] = now().isoformat()
                messages.error(request, f'❌ Failed to update profile. Attempt {retry_count} of 5.')
    else:
        form = PersonalityProfileForm(instance=profile)

    return render(request, 'profile/view_or_edit_profile.html', {'form': form, 'profile': profile})


# class GoalViewSet(viewsets.ModelViewSet):
#     queryset = Goal.objects.all()
#     serializer_class = GoalSerializer
#     permission_classes = [permissions.IsAuthenticated]

#     def get_queryset(self):
#         return Goal.objects.filter(user=self.request.user)

#     def create(self, request, *args, **kwargs):
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save(user=request.user)
#         return Response(serializer.data, status=status.HTTP_201_CREATED)
    
#     @action(detail=True, methods=['get'], url_path='roadmap')
#     def roadmap(self, request, pk=None):
#         try:
#             goal = self.get_queryset().get(pk=pk)
#         except Goal.DoesNotExist:
#             return Response({'detail': 'Goal not found.'}, status=status.HTTP_404_NOT_FOUND)

#         steps = goal.steps.all().order_by('order')
#         serializer = RoadmapStepSerializer(steps, many=True)
#         return Response(serializer.data)


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


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_assessment_questions(request):
    """Get all assessment questions"""
    questions = AssessmentQuestion.objects.all().order_by('question_id')
    serializer = AssessmentQuestionSerializer(questions, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_assessment(request):
    """Submit assessment answers and create/update personality profile"""
    answers_data = request.data.get('answers', [])
    
    if not answers_data:
        return Response({'detail': 'No answers provided'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Map to store dimension values
    dimension_values = {
        'problem_solving': '',
        'goal_energy': '',
        'strengths': '',
        'change_response': '',
        'goal_motivation': '',
        'daily_motivation': '',
        'core_belief': '',
        'time_structure': '',
        'environment_preference': '',
        'progress_block': '',
        'obstacle_type': '',
        'future_focus': '',
        'success_definition': '',
        'project_style': '',
        'support_type': ''
    }
    
    # Delete previous answers for this user
    AssessmentAnswer.objects.filter(user=request.user).delete()
    
    # Process each answer
    for answer_data in answers_data:
        question_id = answer_data.get('question_id')
        answer = answer_data.get('answer')
        
        try:
            question = AssessmentQuestion.objects.get(question_id=question_id)
            
            # Save the answer
            AssessmentAnswer.objects.create(
                user=request.user,
                question=question,
                answer=answer
            )
            
            # Map the answer to its value based on the dimension
            if answer == 'a':
                dimension_value = question.value_a
            elif answer == 'b':
                dimension_value = question.value_b
            elif answer == 'c':
                dimension_value = question.value_c
            elif answer == 'd':
                dimension_value = question.value_d
            else:
                dimension_value = ''
            
            # Only update if the dimension exists in our mapping
            if question.dimension in dimension_values:
                dimension_values[question.dimension] = dimension_value
            
        except AssessmentQuestion.DoesNotExist:
            return Response(
                {'detail': f'Question with ID {question_id} does not exist'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    # Create or update the personality profile
    try:
        profile = PersonalityProfile.objects.get(user=request.user)
        # Update existing profile
        for key, value in dimension_values.items():
            if value:  # Only update if we have a value
                setattr(profile, key, value)
        profile.save()
    except PersonalityProfile.DoesNotExist:
        # Create new profile
        profile = PersonalityProfile.objects.create(
            user=request.user,
            **{k: v for k, v in dimension_values.items() if v}  # Only include non-empty values
        )
    
    serializer = PersonalityProfileSerializer(profile)
    return Response({
        'detail': 'Assessment completed successfully',
        'profile': serializer.data
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_personality_profile(request):
    """Get personality profile for the current user"""
    try:
        profile = PersonalityProfile.objects.get(user=request.user)
        serializer = PersonalityProfileSerializer(profile)
        return Response(serializer.data)
    except PersonalityProfile.DoesNotExist:
        return Response(
            {'detail': 'No personality profile found. Please complete the assessment.'},
            status=status.HTTP_404_NOT_FOUND
        )
    

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def goal_list_create(request):
    """List all goals or create a new goal"""
    if request.method == 'GET':
        goals = Goal.objects.filter(user=request.user)
        serializer = GoalSerializer(goals, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = GoalSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def goal_detail(request, pk):
    """Retrieve, update or delete a goal"""
    try:
        goal = Goal.objects.get(pk=pk, user=request.user)
    except Goal.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        serializer = GoalSerializer(goal)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        serializer = GoalSerializer(goal, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        goal.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def goal_roadmap(request, pk):
    """Get roadmap steps for a specific goal"""
    try:
        goal = Goal.objects.get(pk=pk, user=request.user)
    except Goal.DoesNotExist:
        return Response({'detail': 'Goal not found.'}, status=status.HTTP_404_NOT_FOUND)
    
    steps = goal.steps.all().order_by('order')
    serializer = RoadmapStepSerializer(steps, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_points(request):
    """Get the current user's points and level"""
    try:
        points = UserPoints.objects.get(user=request.user)
        serializer = UserPointsSerializer(points)
        return Response(serializer.data)
    except UserPoints.DoesNotExist:
        # Create new points object if it doesn't exist
        points = UserPoints.objects.create(user=request.user)
        serializer = UserPointsSerializer(points)
        return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_points_for_goal(request):
    """Add points for completing a goal"""
    goal_id = request.data.get('goal_id')
    category = request.data.get('category', 'other')
    
    # Define points by category
    category_points = {
        'career': 100,
        'education': 100,
        'personal': 75,
        'financial': 125,
        'health': 100,
        'other': 50
    }
    
    points_to_add = category_points.get(category.lower(), 50)
    
    try:
        # Get or create user points
        user_points, created = UserPoints.objects.get_or_create(user=request.user)
        
        # Add points
        level_up = user_points.add_points(points_to_add)
        
        # Check for achievements
        check_achievements(request.user, user_points)
        
        return Response({
            'total_points': user_points.total_points,
            'level': user_points.level,
            'points_earned': points_to_add,
            'level_up': level_up,
            'goals_completed': user_points.goals_completed
        })
    except Exception as e:
        return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_achievements(request):
    """Get all achievements for the current user"""
    user_achievements = UserAchievement.objects.filter(user=request.user)
    serializer = UserAchievementSerializer(user_achievements, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_new_achievements(request):
    """Check for new achievements and return them"""
    user_points = UserPoints.objects.get_or_create(user=request.user)[0]
    new_achievements = check_achievements(request.user, user_points)
    
    serializer = AchievementSerializer(new_achievements, many=True)
    return Response({
        'new_achievements': serializer.data
    })

# Helper function to check and award achievements
def check_achievements(user, user_points):
    """Check if user qualifies for any new achievements and award them"""
    new_achievements = []
    
    # Get all existing achievements for this user
    existing_achievements = UserAchievement.objects.filter(user=user).values_list('achievement_id', flat=True)
    
    # Check for goal completion achievements
    if user_points.goals_completed >= 1:
        achievement, created = Achievement.objects.get_or_create(
            name="First Goal Completed",
            defaults={
                'description': "You've completed your first goal!",
                'points': 50,
                'achievement_type': 'completion',
                'icon': 'stars'
            }
        )
        
        if achievement.id not in existing_achievements:
            UserAchievement.objects.create(user=user, achievement=achievement)
            new_achievements.append(achievement)
            # Add achievement bonus points
            user_points.total_points += achievement.points
            user_points.save()
    
    if user_points.goals_completed >= 5:
        achievement, created = Achievement.objects.get_or_create(
            name="Goal Master",
            defaults={
                'description': "You've completed 5 goals!",
                'points': 100,
                'achievement_type': 'completion',
                'icon': 'emoji_events'
            }
        )
        
        if achievement.id not in existing_achievements:
            UserAchievement.objects.create(user=user, achievement=achievement)
            new_achievements.append(achievement)
            # Add achievement bonus points
            user_points.total_points += achievement.points
            user_points.save()
    
    # Check for level achievements
    if user_points.level >= 3:
        achievement, created = Achievement.objects.get_or_create(
            name="Level 3 Achiever",
            defaults={
                'description': "You've reached level 3!",
                'points': 75,
                'achievement_type': 'special',
                'icon': 'military_tech'
            }
        )
        
        if achievement.id not in existing_achievements:
            UserAchievement.objects.create(user=user, achievement=achievement)
            new_achievements.append(achievement)
            # Add achievement bonus points
            user_points.total_points += achievement.points
            user_points.save()
    
    # Return any new achievements
    return new_achievements