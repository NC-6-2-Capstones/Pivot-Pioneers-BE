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
    Goal, PersonalityProfile, RoadmapStep, Resource, AssessmentQuestion, AssessmentAnswer
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
from rest_framework.permissions import AllowAny, IsAuthenticated
from .gemini_ai import analyze_goal_with_gemini
from rest_framework.views import APIView
import re # Import re for parsing

# Create your views here.
User = get_user_model()

def home_view(request):
    return render(request, 'home.html')

def ask_gemini(request):
    prompt = request.GET.get("prompt", "")

    headers = {
        "Authorization": f"Bearer {settings.GEMINI_API_KEY}",
    }

    response = requests.post(
        "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent",
        headers=headers,
        json={"contents": [{"parts": [{"text": prompt}]}]}
    )
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


def parse_gemini_roadmap_response(text_response):
    """
    Parses the plain text response from Gemini to extract roadmap milestones and full plan.
    Assumes the response format requested in the prompt:
    Milestones:
    - Start: ...
    - 3 months: ...
    - 6 months: ...
    - 9 months: ...
    - 12 months: ...

    Full Plan:
    ...
    """
    roadmap_data = {
        "milestone_start": "",
        "milestone_3_months": "",
        "milestone_6_months": "",
        "milestone_9_months": "",
        "milestone_12_months": "",
        "full_plan": ""
    }

    try:
        # Extract Milestones block
        milestones_match = re.search(r"Milestones:(.*?)Full Plan:", text_response, re.DOTALL | re.IGNORECASE)
        milestones_text = ""
        if milestones_match:
            milestones_text = milestones_match.group(1).strip()

        # Extract Full Plan block
        full_plan_match = re.search(r"Full Plan:(.*)", text_response, re.DOTALL | re.IGNORECASE)
        if full_plan_match:
            roadmap_data["full_plan"] = full_plan_match.group(1).strip()

        # Extract individual milestones
        if milestones_text:
            start_match = re.search(r"- Start:(.*?)(?=(- 3 months:|- 6 months:|- 9 months:|- 12 months:|$))", milestones_text, re.DOTALL | re.IGNORECASE)
            if start_match: roadmap_data["milestone_start"] = start_match.group(1).strip()

            three_months_match = re.search(r"- 3 months:(.*?)(?=(- 6 months:|- 9 months:|- 12 months:|$))", milestones_text, re.DOTALL | re.IGNORECASE)
            if three_months_match: roadmap_data["milestone_3_months"] = three_months_match.group(1).strip()

            six_months_match = re.search(r"- 6 months:(.*?)(?=(- 9 months:|- 12 months:|$))", milestones_text, re.DOTALL | re.IGNORECASE)
            if six_months_match: roadmap_data["milestone_6_months"] = six_months_match.group(1).strip()

            nine_months_match = re.search(r"- 9 months:(.*?)(?=(- 12 months:|$))", milestones_text, re.DOTALL | re.IGNORECASE)
            if nine_months_match: roadmap_data["milestone_9_months"] = nine_months_match.group(1).strip()

            twelve_months_match = re.search(r"- 12 months:(.*)", milestones_text, re.DOTALL | re.IGNORECASE)
            if twelve_months_match: roadmap_data["milestone_12_months"] = twelve_months_match.group(1).strip()
            
    except Exception as e:
        # Log parsing error, or handle as needed
        print(f"Error parsing roadmap response: {e}")
        # Optionally, put the whole raw response into full_plan if parsing fails
        # roadmap_data["full_plan"] = "Could not parse roadmap details. Raw response:\\n" + text_response


    return roadmap_data


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_roadmap(request):
    """
    Generate a roadmap using Gemini AI, parse it, and save it to the Goal.
    Expects 'goal_id' in request.data to identify the target goal.
    Also uses 'goal' title, 'category', 'description' from request.data for the prompt.
    """
    user = request.user
    goal_id = request.data.get('goal_id')
    goal_title = request.data.get('goal') # Assuming 'goal' is the title for the prompt
    category = request.data.get('category')
    description = request.data.get('description')

    if not goal_id:
        return Response({'detail': 'goal_id is required.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        target_goal = Goal.objects.get(id=goal_id, user=user)
    except Goal.DoesNotExist:
        return Response({'detail': 'Goal not found or you do not have permission.'}, status=status.HTTP_404_NOT_FOUND)

    # Check for personality profile
    try:
        profile = PersonalityProfile.objects.get(user=user)
    except PersonalityProfile.DoesNotExist:
        return Response({'detail': 'You must complete your assessment and personality profile before generating a roadmap.'}, status=status.HTTP_400_BAD_REQUEST)

    # Get assessment answers (latest for user)
    assessment_answers = AssessmentAnswer.objects.filter(user=user)
    if not assessment_answers.exists():
        return Response({'detail': 'You must complete your assessment before generating a roadmap.'}, status=status.HTTP_400_BAD_REQUEST)

    assessment_summary = {}
    for answer in assessment_answers:
        # We need the actual text value of the answer, not just 'a', 'b', 'c', 'd'
        # This requires mapping answer.answer to question.value_a, value_b etc.
        # For simplicity in this step, I'm still using answer.answer, but this should be improved
        # to get the richer text value that the profile uses.
        # Example: if answer.answer is 'a', use answer.question.value_a
        answer_choice = answer.answer 
        value = answer_choice # Placeholder - ideally map to actual value
        if hasattr(answer.question, f'value_{answer_choice.lower()}'):
             value = getattr(answer.question, f'value_{answer_choice.lower()}')
        assessment_summary[answer.question.dimension] = value


    personality_summary = {field.name: getattr(profile, field.name) for field in PersonalityProfile._meta.fields if field.name not in ['id', 'user', 'created_at', 'updated_at']}

    # Compose prompt for Gemini
    # Using goal_title, category, description from request for the prompt
    prompt = f"""
    The user has the following goal:
    Title: {goal_title} 
    Category: {category}
    Description: {description}

    Their assessment answers by dimension are:
    {assessment_summary}

    Their personality profile is:
    {personality_summary}

    Please generate a 1-year roadmap for this user, broken into 5 milestones (Start, 3 months, 6 months, 9 months, 12 months) and a detailed full plan. Format as:
    Milestones:
    - Start: ...
    - 3 months: ...
    - 6 months: ...
    - 9 months: ...
    - 12 months: ...

    Full Plan:
    ...
    """
    try:
        ai_response_text = analyze_goal_with_gemini(prompt)
    except Exception as e:
        return Response({'detail': f'Error calling Gemini: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # Parse the AI response
    parsed_roadmap = parse_gemini_roadmap_response(ai_response_text)

    # Update the target Goal object
    target_goal.milestone_start = parsed_roadmap.get("milestone_start", "")
    target_goal.milestone_3_months = parsed_roadmap.get("milestone_3_months", "")
    target_goal.milestone_6_months = parsed_roadmap.get("milestone_6_months", "")
    target_goal.milestone_9_months = parsed_roadmap.get("milestone_9_months", "")
    target_goal.milestone_12_months = parsed_roadmap.get("milestone_12_months", "")
    target_goal.full_plan = parsed_roadmap.get("full_plan", "")
    
    try:
        target_goal.save()
    except Exception as e:
        # Log saving error
        print(f"Error saving roadmap to goal {target_goal.id}: {e}")
        return Response({'detail': f'Could not save roadmap to goal: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    serializer = GoalSerializer(target_goal)
    return Response(serializer.data, status=status.HTTP_200_OK)