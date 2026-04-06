from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Avg, Count, Q
from functools import wraps

from .models import User, SoldierProfile, Assessment, ReadinessScore
from .forms import (
    LoginForm, RegistrationForm, SoldierProfileForm,
    AssessmentForm, ReadinessScoreForm, UserStatusForm,
)


# ---------------------------------------------------------------------------
# Decorators
# ---------------------------------------------------------------------------

def role_required(*roles):
    """Restrict view to users with specific role(s)."""
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapper(request, *args, **kwargs):
            if request.user.role not in roles:
                messages.error(request, "You don't have permission to access this page.")
                return redirect('dashboard')
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


# ---------------------------------------------------------------------------
# Auth Views
# ---------------------------------------------------------------------------

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.get_full_name() or user.username}!')
            return redirect('dashboard')
    else:
        form = LoginForm()
    return render(request, 'auth/login.html', {'form': form})


def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # If soldier, create a blank profile
            if user.role == 'soldier':
                SoldierProfile.objects.create(
                    user=user,
                    service_number=f"SVC-{user.pk:06d}",
                )
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('dashboard')
    else:
        form = RegistrationForm()
    return render(request, 'auth/register.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('login')


# ---------------------------------------------------------------------------
# Dashboard Router
# ---------------------------------------------------------------------------

@login_required
def dashboard_router(request):
    role = request.user.role
    if role == 'admin':
        return redirect('admin_dashboard')
    elif role == 'officer':
        return redirect('officer_dashboard')
    else:
        return redirect('soldier_dashboard')


# ---------------------------------------------------------------------------
# Admin Dashboard
# ---------------------------------------------------------------------------

@role_required('admin')
def admin_dashboard(request):
    users = User.objects.all()
    context = {
        'total_users': users.count(),
        'total_soldiers': users.filter(role='soldier').count(),
        'total_officers': users.filter(role='officer').count(),
        'active_users': users.filter(is_active=True).count(),
        'inactive_users': users.filter(is_active=False).count(),
        'recent_assessments': Assessment.objects.select_related('soldier', 'assessed_by')[:10],
        'avg_readiness': ReadinessScore.objects.aggregate(avg=Avg('overall_score'))['avg'] or 0,
        'users': users.order_by('-date_joined'),
    }
    return render(request, 'dashboards/admin.html', context)


@role_required('admin')
def toggle_user_status(request, user_id):
    target = get_object_or_404(User, pk=user_id)
    if target == request.user:
        messages.error(request, "You cannot deactivate yourself.")
    else:
        target.is_active = not target.is_active
        target.save()
        status = 'activated' if target.is_active else 'deactivated'
        messages.success(request, f'User {target.username} has been {status}.')
    return redirect('admin_dashboard')


# ---------------------------------------------------------------------------
# Officer Dashboard & Actions
# ---------------------------------------------------------------------------

@role_required('officer')
def officer_dashboard(request):
    my_assessments = Assessment.objects.filter(assessed_by=request.user).select_related('soldier')
    my_scores = ReadinessScore.objects.filter(scored_by=request.user).select_related('soldier')
    soldiers = User.objects.filter(role='soldier', is_active=True)

    context = {
        'total_soldiers': soldiers.count(),
        'assessments_count': my_assessments.count(),
        'scores_count': my_scores.count(),
        'recent_assessments': my_assessments[:10],
        'recent_scores': my_scores[:10],
        'soldiers': soldiers,
    }
    return render(request, 'dashboards/officer.html', context)


@role_required('officer')
def create_assessment(request):
    if request.method == 'POST':
        form = AssessmentForm(request.POST)
        if form.is_valid():
            assessment = form.save(commit=False)
            assessment.assessed_by = request.user
            assessment.save()
            messages.success(request, 'Assessment recorded successfully.')
            return redirect('officer_dashboard')
    else:
        form = AssessmentForm()
    return render(request, 'officer/assessment_create.html', {'form': form})


@role_required('officer')
def record_score(request):
    if request.method == 'POST':
        form = ReadinessScoreForm(request.POST)
        if form.is_valid():
            score = form.save(commit=False)
            score.scored_by = request.user
            score.save()
            messages.success(
                request,
                f'Score recorded — Overall: {score.overall_score} ({score.readiness_level})',
            )
            return redirect('officer_dashboard')
    else:
        form = ReadinessScoreForm()
    return render(request, 'officer/score_record.html', {'form': form})


@role_required('officer')
def assessment_list(request):
    assessments = Assessment.objects.filter(assessed_by=request.user).select_related('soldier')
    return render(request, 'officer/assessment_list.html', {'assessments': assessments})


@role_required('officer')
def score_list(request):
    scores = ReadinessScore.objects.filter(scored_by=request.user).select_related('soldier')
    return render(request, 'officer/score_list.html', {'scores': scores})


# ---------------------------------------------------------------------------
# Soldier Dashboard
# ---------------------------------------------------------------------------

@role_required('soldier')
def soldier_dashboard(request):
    my_assessments = Assessment.objects.filter(soldier=request.user)
    my_scores = ReadinessScore.objects.filter(soldier=request.user)
    latest_score = my_scores.first()

    context = {
        'profile': getattr(request.user, 'profile', None),
        'assessments': my_assessments,
        'scores': my_scores,
        'latest_score': latest_score,
        'total_assessments': my_assessments.count(),
        'pass_count': my_assessments.filter(result='pass').count(),
        'fail_count': my_assessments.filter(result='fail').count(),
    }
    return render(request, 'dashboards/soldier.html', context)


@role_required('soldier')
def edit_profile(request):
    profile, created = SoldierProfile.objects.get_or_create(
        user=request.user,
        defaults={'service_number': f"SVC-{request.user.pk:06d}"},
    )
    if request.method == 'POST':
        form = SoldierProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated.')
            return redirect('soldier_dashboard')
    else:
        form = SoldierProfileForm(instance=profile)
    return render(request, 'soldier/profile_edit.html', {'form': form})


@role_required('soldier')
def score_history(request):
    scores = ReadinessScore.objects.filter(soldier=request.user)
    return render(request, 'soldier/score_history.html', {'scores': scores})
