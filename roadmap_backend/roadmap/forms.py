from django import forms
from .models import PersonalityProfile

class PersonalityProfileForm(forms.ModelForm):
    class Meta:
        model = PersonalityProfile
        exclude = ['user', 'created_at', 'updated_at']
