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
 
    # name (first, last, visibility)
    first_name = models.CharField(max_length=75, blank=True)
    last_name = models.CharField(max_length=75, blank=True)
    name_visible = models.BooleanField(default=False)
 
    # profile picture
    profile_picture = models.ImageField(upload_to="profile_pictures/", blank=True, null=True)
    picture_visible = models.BooleanField(default=False)
 
    # headline, visibility
    headline = models.TextField(blank=True)
    headline_visible = models.BooleanField(default=False)
 
    # bio
    bio = models.TextField(blank=True)
 
    # location, visibility
    location = models.CharField(max_length=200, blank=True)
    location_visible = models.BooleanField(default=False)
  
    # date created and updated
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
 
    # uses first and last name to create a full name
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()
 
    # sets a name variable to full name so that other things that rely on name aren't messed up
    @property
    def name(self):
        return self.full_name
    
    # only lets recruiters see educations marked as visible
    @property
    def visible_educations(self):
        return [e for e in self.educations.all() if e.visible]
    
    # only lets recruiters see work experiences marked as visible
    @property
    def visible_experience(self):
        return [e for e in self.work_experiences.all() if e.visible]
    
    # only lets recruiters see skills marked as visible
    @property
    def visible_skills(self):
        return [s for s in self.skills.all() if s.skills_visible]

    def __str__(self):
        return self.full_name or self.user.username
 
 
class Education(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="educations")
    institution = models.CharField(max_length=150)
    dates = models.CharField(max_length=100, blank=True, help_text="e.g. August 2025 - December 2028")
    notes = models.TextField(blank=True)
    visible = models.BooleanField(default=False)
 
    class Meta:
        ordering = ["id"]
 
    def __str__(self):
        return self.institution
 
class WorkExperience(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="work_experiences")
    company = models.CharField(max_length=150, blank=True)
    title = models.CharField(max_length=200)
    dates = models.CharField(max_length=100, blank=True, help_text="e.g. September 2025 - Present")
    description = models.TextField(blank=True)
    visible = models.BooleanField(default=False)
 
    class Meta:
        ordering = ["id"]
 
    def __str__(self):
        return self.title
 
 
class Skill(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="skills")
    name = models.CharField(max_length=60)
    skills_visible = models.BooleanField(default=False)
 
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
    url = models.URLField()
    visible = models.BooleanField(default=False)
 
    def __str__(self):
        return self.url
 


