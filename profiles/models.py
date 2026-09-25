from django.conf import settings
from django.db import models


class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    name = models.CharField(max_length=150)
    headline = models.CharField(
        max_length=200,
        blank=True,
    )
    bio = models.TextField(blank=True)
    location = models.CharField(
        max_length=150,
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name or self.user.get_username()


class WorkExperience(models.Model):
    profile = models.ForeignKey(
        Profile, on_delete=models.CASCADE, related_name="work_experiences"
    )
    company = models.CharField(max_length=150)
    title = models.CharField(max_length=150)
    start_date = models.DateField()
    end_date = models.DateField(
        blank=True, null=True, help_text="Leave blank if this is your current role."
    )
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["-start_date"]

    def __str__(self):
        return f"{self.title} at {self.company}"


class Education(models.Model):
    profile = models.ForeignKey(
        Profile, on_delete=models.CASCADE, related_name="educations"
    )
    institution = models.CharField(max_length=150)
    degree = models.CharField(max_length=150, blank=True)
    field_of_study = models.CharField(max_length=150, blank=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)

    class Meta:
        ordering = ["-start_date"]

    def __str__(self):
        return f"{self.degree} - {self.institution}".strip(" -")


class Skill(models.Model):
    profile = models.ForeignKey(
        Profile, on_delete=models.CASCADE, related_name="skills"
    )
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


class Project(models.Model):
    profile = models.ForeignKey(
        Profile, on_delete=models.CASCADE, related_name="projects"
    )
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Link(models.Model):
    profile = models.ForeignKey(
        Profile, on_delete=models.CASCADE, related_name="links"
    )
    label = models.CharField(
        max_length=60, help_text="e.g. GitHub, LinkedIn, Portfolio"
    )
    url = models.URLField()

    def __str__(self):
        return self.label