from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Goal, PersonalityProfile, RoadmapStep, Resource, AssessmentQuestion

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']


class PersonalityProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = PersonalityProfile
        exclude = ['created_at', 'updated_at']


class RoadmapStepSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoadmapStep
        fields = '__all__'
        read_only_fields = ['created_at']


class ResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resource
        fields = '__all__'
        read_only_fields = ['created_at']


class GoalSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    steps = RoadmapStepSerializer(many=True, read_only=True)
    resources = ResourceSerializer(many=True, read_only=True)

    class Meta:
        model = Goal
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


class AssessmentQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssessmentQuestion
        fields = '__all__'
