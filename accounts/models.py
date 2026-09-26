from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Account(models.Model):
    ROLE_CHOICES = [
        ('candidate', 'Candidate'),
        ('recruiter', 'Recruiter')
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='candidate'
    )

    company_name = models.CharField(max_length=150, blank=True, null=True)
    company_email = models.EmailField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.role}"

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    name = models.CharField(max_length=150)
    headline = models.CharField(max_length=200)
    bio = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class WorkExperience(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="work_experiences")
    company = models.CharField(max_length=150)
    title = models.CharField(max_length=150)
    start_date = models.DateField()
    end_date = models.DateField(help_text="Leave blank if this is your current role.")
    description = models.TextField()

    class Meta:
        ordering = ["-start_date"]

    def __str__(self):
        return f"{self.title} at {self.company}"


class Education(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="educations")
    institution = models.CharField(max_length=150)
    degree = models.CharField(max_length=150)
    field_of_study = models.CharField(max_length=150)
    start_date = models.DateField(null=True)
    end_date = models.DateField(null=True)

    class Meta:
        ordering = ["-start_date"]

    def __str__(self):
        return f"{self.degree} - {self.institution}"


class Skill(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="skills")
    name = models.CharField(max_length=60)

    class Meta:
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["profile", "name"], name="unique_skill_per_profile"
            )
        ]

    def __str__(self):
        return self.name


class Link(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="links")
    label = models.CharField(max_length=60, help_text="e.g. GitHub, LinkedIn, Portfolio")
    url = models.URLField()

    def __str__(self):
        return self.label
