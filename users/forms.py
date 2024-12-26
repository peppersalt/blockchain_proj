from django import forms
from .models import UserProfile

class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['nickname', 'email', 'bio', 'profile_image']
        widgets = {
            'nickname': forms.TextInput(attrs={'class': 'input', 'placeholder': 'Nickname'}),
            'email': forms.EmailInput(attrs={'class': 'input', 'placeholder': 'Email'}),
            'bio': forms.Textarea(attrs={'class': 'textarea', 'placeholder': 'Bio'}),
            'profile_image': forms.FileInput(attrs={'class': 'file-input'}),
        }
