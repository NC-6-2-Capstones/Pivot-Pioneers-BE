
import os
import django
import sys

# Set up Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'roadmap_backend.settings')
django.setup()

from roadmap.models import AssessmentQuestion

# Define the questions data
questions_data = [
    {
        "question_id": 1,
        "dimension": "problem_solving",
        "text": "How do you most naturally approach problems?",
        "option_a": "I brainstorm creatively and look for novel ideas",
        "option_b": "I gather all the data and analyze the patterns",
        "option_c": "I ask for advice or feedback from others",
        "option_d": "I take immediate action and iterate as I go",
        "value_a": "creative",
        "value_b": "analytical",
        "value_c": "collaborative",
        "value_d": "action-oriented"
    },
    {
        "question_id": 2,
        "dimension": "goal_energy",
        "text": "When working toward a goal, what energizes you most?",
        "option_a": "Collaborating with others",
        "option_b": "Seeing visible progress",
        "option_c": "Learning and mastering new skills",
        "option_d": "Picturing the long-term vision",
        "value_a": "social",
        "value_b": "progress-focused",
        "value_c": "growth-focused",
        "value_d": "vision-focused"
    },
    {
        "question_id": 3,
        "dimension": "strengths",
        "text": "Which of the following best describes your natural strengths?",
        "option_a": "Communication & empathy",
        "option_b": "Structure & discipline",
        "option_c": "Strategic thinking",
        "option_d": "Adaptability under pressure",
        "value_a": "empathy",
        "value_b": "discipline",
        "value_c": "strategy",
        "value_d": "adaptability"
    },
    {
        "question_id": 4,
        "dimension": "change_response",
        "text": "How do you handle uncertainty or change?",
        "option_a": "I get overwhelmed and prefer stability",
        "option_b": "I research and plan a way forward",
        "option_c": "I stay calm and adjust quickly",
        "option_d": "I see it as an opportunity to reinvent",
        "value_a": "stability-seeking",
        "value_b": "planner",
        "value_c": "resilient",
        "value_d": "opportunistic"
    },
    {
        "question_id": 5,
        "dimension": "goal_motivation",
        "text": "Why do you want to achieve your goal?",
        "option_a": "To prove something to myself or others",
        "option_b": "To create a better life for people I care about",
        "option_c": "To live a life aligned with my values",
        "option_d": "To feel accomplished and successful",
        "value_a": "prove_self",
        "value_b": "others",
        "value_c": "values",
        "value_d": "accomplishment"
    },
    {
        "question_id": 6,
        "dimension": "daily_motivation",
        "text": "What motivates you more in your day-to-day efforts?",
        "option_a": "Recognition and external reward",
        "option_b": "Personal growth and self-improvement",
        "option_c": "A sense of impact or contribution",
        "option_d": "Competition and outperforming others",
        "value_a": "external_reward",
        "value_b": "growth",
        "value_c": "impact",
        "value_d": "competition"
    },
    {
        "question_id": 7,
        "dimension": "core_belief",
        "text": "Which phrase best reflects your belief system?",
        "option_a": "\"Discipline beats motivation.\"",
        "option_b": "\"Stay curious and keep growing.\"",
        "option_c": "\"Together, we go further.\"",
        "option_d": "\"Clarity of purpose unlocks everything.\"",
        "value_a": "discipline",
        "value_b": "curiosity",
        "value_c": "community",
        "value_d": "purpose"
    },
    {
        "question_id": 8,
        "dimension": "time_structure",
        "text": "How do you prefer to structure your time?",
        "option_a": "I follow a clear daily or weekly schedule",
        "option_b": "I work in bursts of energy and flow",
        "option_c": "I need external accountability to stay focused",
        "option_d": "I like setting intentions but staying flexible",
        "value_a": "routine",
        "value_b": "flow",
        "value_c": "accountability",
        "value_d": "flexibility"
    },
    {
        "question_id": 9,
        "dimension": "environment_preference",
        "text": "What kind of environment brings out your best work?",
        "option_a": "Quiet, focused spaces where I control the flow",
        "option_b": "High-energy, collaborative atmospheres",
        "option_c": "Flexible setups with room for creativity",
        "option_d": "Challenging environments that push me",
        "value_a": "quiet_focus",
        "value_b": "collaborative",
        "value_c": "creative_flex",
        "value_d": "high_challenge"
    },
    {
        "question_id": 10,
        "dimension": "progress_block",
        "text": "When you're struggling with progress, what's most helpful?",
        "option_a": "A system or checklist to follow",
        "option_b": "Encouragement and positive feedback",
        "option_c": "Time alone to regroup and refocus",
        "option_d": "A bold challenge to re-spark momentum",
        "value_a": "structure_needed",
        "value_b": "support",
        "value_c": "solitude",
        "value_d": "challenge"
    },
    {
        "question_id": 11,
        "dimension": "obstacle_type",
        "text": "What's the biggest challenge you've faced while chasing a goal?",
        "option_a": "Staying consistent long term",
        "option_b": "Knowing where to start",
        "option_c": "Believing in myself",
        "option_d": "Navigating distractions or doubt",
        "value_a": "consistency",
        "value_b": "starting",
        "value_c": "self_doubt",
        "value_d": "distractions"
    },
    {
        "question_id": 12,
        "dimension": "future_focus",
        "text": "When you picture your future success, what do you focus on first?",
        "option_a": "The lifestyle and freedom it brings",
        "option_b": "The milestones you'll reach",
        "option_c": "The recognition and respect earned",
        "option_d": "The way you'll feel fulfilled and proud",
        "value_a": "freedom",
        "value_b": "milestones",
        "value_c": "recognition",
        "value_d": "fulfillment"
    },
    {
        "question_id": 13,
        "dimension": "success_definition",
        "text": "How do you define success?",
        "option_a": "Fulfillment in life and relationships",
        "option_b": "Mastery of your craft or mission",
        "option_c": "Financial freedom and time control",
        "option_d": "Making a meaningful impact",
        "value_a": "relationships",
        "value_b": "mastery",
        "value_c": "freedom",
        "value_d": "impact"
    },
    {
        "question_id": 14,
        "dimension": "project_style",
        "text": "When you're assigned a large project or task, what do you do first?",
        "option_a": "Break it down into smaller, manageable chunks",
        "option_b": "Create a timeline or plan",
        "option_c": "Seek advice or look for examples",
        "option_d": "Dive in and adjust along the way",
        "value_a": "break_down",
        "value_b": "timeline",
        "value_c": "research",
        "value_d": "just_start"
    },
    {
        "question_id": 15,
        "dimension": "support_type",
        "text": "What kind of support helps you thrive most on your journey?",
        "option_a": "A mentor or coach guiding me",
        "option_b": "A community of like-minded peers",
        "option_c": "Tools, templates, and structured plans",
        "option_d": "Time and space to work solo and reflect",
        "value_a": "mentor",
        "value_b": "community",
        "value_c": "tools",
        "value_d": "independent"
    },
]

def seed_questions():
    # Delete existing questions
    AssessmentQuestion.objects.all().delete()
    print("Deleted existing assessment questions")
    
    # Create new questions
    for question_data in questions_data:
        AssessmentQuestion.objects.create(**question_data)
    
    print(f"Created {len(questions_data)} assessment questions")

if __name__ == "__main__":
    seed_questions()