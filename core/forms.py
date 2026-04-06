from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User, SoldierProfile, Assessment, ReadinessScore


# ---------------------------------------------------------------------------
# Auth Forms
# ---------------------------------------------------------------------------

class LoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Username',
            'autocomplete': 'username',
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Password',
            'autocomplete': 'current-password',
        })
    )


class RegistrationForm(UserCreationForm):
    first_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'First Name'}),
    )
    last_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Last Name'}),
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'Email'}),
    )
    role = forms.ChoiceField(
        choices=User.ROLE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-input'}),
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'role', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-input', 'placeholder': 'Username'})
        self.fields['password1'].widget.attrs.update({'class': 'form-input', 'placeholder': 'Password'})
        self.fields['password2'].widget.attrs.update({'class': 'form-input', 'placeholder': 'Confirm Password'})


# ---------------------------------------------------------------------------
# Profile Form
# ---------------------------------------------------------------------------

class SoldierProfileForm(forms.ModelForm):
    class Meta:
        model = SoldierProfile
        fields = ['rank', 'service_number', 'branch', 'unit', 'date_of_enlistment']
        widgets = {
            'rank': forms.Select(attrs={'class': 'form-input'}),
            'service_number': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. SVC-20250001'}),
            'branch': forms.Select(attrs={'class': 'form-input'}),
            'unit': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Unit / Company'}),
            'date_of_enlistment': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
        }


# ---------------------------------------------------------------------------
# Assessment Form
# ---------------------------------------------------------------------------

class AssessmentForm(forms.ModelForm):
    class Meta:
        model = Assessment
        fields = ['soldier', 'assessment_type', 'result', 'notes']
        widgets = {
            'soldier': forms.Select(attrs={'class': 'form-input'}),
            'assessment_type': forms.Select(attrs={'class': 'form-input'}),
            'result': forms.Select(attrs={'class': 'form-input'}),
            'notes': forms.Textarea(attrs={'class': 'form-input', 'rows': 4, 'placeholder': 'Assessment notes…'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['soldier'].queryset = User.objects.filter(role='soldier', is_active=True)
        self.fields['soldier'].label_from_instance = lambda u: f"{u.get_full_name() or u.username}"


# ---------------------------------------------------------------------------
# Readiness Score Form
# ---------------------------------------------------------------------------

class ReadinessScoreForm(forms.ModelForm):
    class Meta:
        model = ReadinessScore
        fields = ['soldier', 'physical_score', 'mental_score', 'equipment_score']
        widgets = {
            'soldier': forms.Select(attrs={'class': 'form-input'}),
            'physical_score': forms.NumberInput(attrs={
                'class': 'form-input score-input', 'min': 0, 'max': 100, 'step': 0.1,
                'placeholder': '0 – 100', 'data-weight': '0.40',
            }),
            'mental_score': forms.NumberInput(attrs={
                'class': 'form-input score-input', 'min': 0, 'max': 100, 'step': 0.1,
                'placeholder': '0 – 100', 'data-weight': '0.35',
            }),
            'equipment_score': forms.NumberInput(attrs={
                'class': 'form-input score-input', 'min': 0, 'max': 100, 'step': 0.1,
                'placeholder': '0 – 100', 'data-weight': '0.25',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['soldier'].queryset = User.objects.filter(role='soldier', is_active=True)
        self.fields['soldier'].label_from_instance = lambda u: f"{u.get_full_name() or u.username}"


# ---------------------------------------------------------------------------
# Admin – User Management
# ---------------------------------------------------------------------------

class UserStatusForm(forms.ModelForm):
    """Toggle user active/inactive status."""
    class Meta:
        model = User
        fields = ['is_active']
        widgets = {
            'is_active': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        }
