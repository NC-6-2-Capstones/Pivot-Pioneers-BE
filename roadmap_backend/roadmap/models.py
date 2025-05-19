from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Goal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='goals')
    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_completed = models.BooleanField(default=False)
    milestone_start = models.TextField(blank=True, null=True)
    milestone_3_months = models.TextField(blank=True, null=True)
    milestone_6_months = models.TextField(blank=True, null=True)
    milestone_9_months = models.TextField(blank=True, null=True)
    milestone_12_months = models.TextField(blank=True, null=True)
    full_plan = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f'{self.title} - {self.user.username}'

class PersonalityProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='personality_profile')
    problem_solving = models.CharField(max_length=50)  # creative, analytical, collaborative, or action-oriented
    goal_energy = models.CharField(max_length=50)  # social, progress-focused, growth-focused, vision-focused
    strengths = models.CharField(max_length=50)  # empathy, discipline, strategy, adaptability
    change_response = models.CharField(max_length=50)  # stability-seeking, planner, resilient, opportunistic
    goal_motivation = models.CharField(max_length=50)  # prove_self, others, values, accomplishment
    daily_motivation = models.CharField(max_length=50)  # external_reward, growth, impact, competition
    core_belief = models.CharField(max_length=50)  # discipline, curiosity, community, purpose
    time_structure = models.CharField(max_length=50)  # routine, flow, accountability, flexibility
    environment_preference = models.CharField(max_length=50)  # quiet_focus, collaborative, creative_flex, high_challenge
    progress_block = models.CharField(max_length=50)  # structure_needed, support, solitude, challenge
    obstacle_type = models.CharField(max_length=50)  # consistency, starting, self_doubt, distractions
    future_focus = models.CharField(max_length=50)  # freedom, milestones, recognition, fulfillment
    success_definition = models.CharField(max_length=50)  # relationships, mastery, freedom, impact
    project_style = models.CharField(max_length=50)  # break_down, timeline, research, just_start
    support_type = models.CharField(max_length=50)  # mentor, community, tools, independent
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username}'s Personality and Strengths Profile"

class RoadmapStep(models.Model):
    goal = models.ForeignKey(Goal, on_delete=models.CASCADE, related_name='steps')
    step_text = models.TextField()
    order = models.IntegerField()
    completed = models.BooleanField(default=False)
    due_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'Step {self.order} of {self.goal.title}'

class Resource(models.Model):
    title = models.CharField(max_length=255)
    link = models.URLField()
    category = models.CharField(max_length=100, blank=True, null=True)
    goal = models.ForeignKey(Goal, on_delete=models.CASCADE, related_name='resources', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title

class AssessmentQuestion(models.Model):
    question_id = models.IntegerField(unique=True)
    dimension = models.CharField(max_length=100)
    text = models.TextField()
    option_a = models.CharField(max_length=255)
    option_b = models.CharField(max_length=255)
    option_c = models.CharField(max_length=255)
    option_d = models.CharField(max_length=255)
    value_a = models.CharField(max_length=50)
    value_b = models.CharField(max_length=50)
    value_c = models.CharField(max_length=50)
    value_d = models.CharField(max_length=50)
    
    def __str__(self):
        return f"Question {self.question_id}: {self.dimension}"


class AssessmentAnswer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assessment_answers')
    question = models.ForeignKey(AssessmentQuestion, on_delete=models.CASCADE)
    answer = models.CharField(max_length=1)  # a, b, c, or d
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'question')
    
    def __str__(self):
        return f"{self.user.username}'s answer to question {self.question.question_id}"
    


class UserPoints(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='points')
    total_points = models.IntegerField(default=0)
    level = models.IntegerField(default=1)
    goals_completed = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username}'s Points - Level {self.level}"
    
    def calculate_level(self):
        """Calculate user level based on points"""
        if self.total_points < 500:
            return 1
        elif self.total_points < 1500:
            return 2
        elif self.total_points < 3000:
            return 3
        elif self.total_points < 5000:
            return 4
        else:
            return 5
    
    def add_points(self, points):
        """Add points and update level if needed"""
        self.total_points += points
        self.goals_completed += 1
        new_level = self.calculate_level()
        level_up = new_level > self.level
        self.level = new_level
        self.save()
        return level_up


class Achievement(models.Model):
    ACHIEVEMENT_TYPES = [
        ('completion', 'Goal Completion'),
        ('streak', 'Completion Streak'),
        ('category', 'Category Mastery'),
        ('special', 'Special Achievement')
    ]
    
    name = models.CharField(max_length=100)
    description = models.TextField()
    points = models.IntegerField(default=50)
    achievement_type = models.CharField(max_length=20, choices=ACHIEVEMENT_TYPES)
    icon = models.CharField(max_length=100, default='trophy')  # FontAwesome or Material icon name
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name


class UserAchievement(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='achievements')
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE)
    achieved_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'achievement')
    
    def __str__(self):
        return f"{self.user.username} - {self.achievement.name}"