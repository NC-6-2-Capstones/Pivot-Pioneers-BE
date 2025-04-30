from django.contrib import admin
from .models import Goal, PersonalityProfile, RoadmapStep, Resource, AssessmentQuestion

@admin.register(Goal)
class GoalAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'category', 'created_at', 'is_completed')
    list_filter = ('is_completed', 'category', 'created_at')
    search_fields = ('title', 'description', 'user__username')

@admin.register(PersonalityProfile)
class PersonalityProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'problem_solving', 'strengths', 'created_at')
    list_filter = ('problem_solving', 'strengths', 'core_belief')
    search_fields = ('user__username',)

@admin.register(RoadmapStep)
class RoadmapStepAdmin(admin.ModelAdmin):
    list_display = ('goal', 'order', 'completed', 'due_date')
    list_filter = ('completed', 'due_date')
    search_fields = ('step_text', 'goal__title')
    ordering = ('goal', 'order')

@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'goal')
    list_filter = ('category',)
    search_fields = ('title', 'link', 'goal__title')

@admin.register(AssessmentQuestion)
class AssessmentQuestionAdmin(admin.ModelAdmin):
    list_display = ('question_id', 'dimension', 'text')
    list_filter = ('dimension',)
    search_fields = ('text', 'dimension')
    ordering = ('question_id',)