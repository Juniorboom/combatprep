from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class User(AbstractUser):
    """Custom user with role-based access."""
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('officer', 'Officer'),
        ('soldier', 'Soldier'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='soldier')

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"

    @property
    def is_admin_role(self):
        return self.role == 'admin'

    @property
    def is_officer(self):
        return self.role == 'officer'

    @property
    def is_soldier(self):
        return self.role == 'soldier'


class SoldierProfile(models.Model):
    """Extended profile for soldiers."""
    RANK_CHOICES = (
        ('pvt', 'Private'),
        ('pfc', 'Private First Class'),
        ('cpl', 'Corporal'),
        ('sgt', 'Sergeant'),
        ('ssgt', 'Staff Sergeant'),
        ('sfc', 'Sergeant First Class'),
        ('msg', 'Master Sergeant'),
        ('lt', 'Lieutenant'),
        ('cpt', 'Captain'),
        ('maj', 'Major'),
    )
    BRANCH_CHOICES = (
        ('infantry', 'Infantry'),
        ('armor', 'Armor'),
        ('artillery', 'Artillery'),
        ('engineers', 'Engineers'),
        ('signals', 'Signals'),
        ('aviation', 'Aviation'),
        ('medical', 'Medical'),
        ('logistics', 'Logistics'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    rank = models.CharField(max_length=10, choices=RANK_CHOICES, default='pvt')
    service_number = models.CharField(max_length=20, unique=True)
    branch = models.CharField(max_length=20, choices=BRANCH_CHOICES, default='infantry')
    unit = models.CharField(max_length=100, blank=True)
    date_of_enlistment = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.get_rank_display()} {self.user.get_full_name()} — {self.service_number}"

    class Meta:
        ordering = ['user__last_name', 'user__first_name']


class Assessment(models.Model):
    """Assessment record for a soldier conducted by an officer."""
    TYPE_CHOICES = (
        ('physical', 'Physical'),
        ('mental', 'Mental'),
        ('equipment', 'Equipment'),
        ('combined', 'Combined'),
    )
    RESULT_CHOICES = (
        ('pass', 'Pass'),
        ('fail', 'Fail'),
        ('conditional', 'Conditional'),
        ('pending', 'Pending'),
    )

    soldier = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='assessments',
        limit_choices_to={'role': 'soldier'},
    )
    assessed_by = models.ForeignKey(
        User, on_delete=models.SET_NULL,
        null=True,
        related_name='conducted_assessments',
        limit_choices_to={'role': 'officer'},
    )
    assessment_type = models.CharField(max_length=15, choices=TYPE_CHOICES)
    result = models.CharField(max_length=15, choices=RESULT_CHOICES, default='pending')
    date = models.DateField(auto_now_add=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.get_assessment_type_display()} — {self.soldier} — {self.get_result_display()}"

    class Meta:
        ordering = ['-date']


class ReadinessScore(models.Model):
    """Readiness score with weighted overall calculation."""
    soldier = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='readiness_scores',
        limit_choices_to={'role': 'soldier'},
    )
    scored_by = models.ForeignKey(
        User, on_delete=models.SET_NULL,
        null=True,
        related_name='recorded_scores',
        limit_choices_to={'role': 'officer'},
    )
    physical_score = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Physical readiness (0–100)",
    )
    mental_score = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Mental readiness (0–100)",
    )
    equipment_score = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Equipment readiness (0–100)",
    )
    overall_score = models.FloatField(editable=False, default=0)
    date = models.DateField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Auto-calculate overall score: Physical 40%, Mental 35%, Equipment 25%
        self.overall_score = round(
            (self.physical_score * 0.40)
            + (self.mental_score * 0.35)
            + (self.equipment_score * 0.25),
            2,
        )
        super().save(*args, **kwargs)

    @property
    def readiness_level(self):
        if self.overall_score >= 85:
            return 'Combat Ready'
        elif self.overall_score >= 70:
            return 'Mostly Ready'
        elif self.overall_score >= 50:
            return 'Needs Improvement'
        else:
            return 'Not Ready'

    def __str__(self):
        return f"{self.soldier} — {self.overall_score} ({self.readiness_level})"

    class Meta:
        ordering = ['-date']
