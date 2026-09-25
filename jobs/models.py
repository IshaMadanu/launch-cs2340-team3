from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Job(models.Model):
    recruiter = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="jobs"
    )


    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    salary = models.IntegerField()
    skills = models.TextField()
    location = models.TextField()
    description = models.TextField()
    image = models.ImageField(upload_to='job_images/')

    WORK_TYPE_CHOICES = [
    ('remote', 'Remote'),
    ('onsite', 'On-site'),
    ('hybrid', 'Hybrid'),
    ]

    work_type = models.CharField(
        max_length=10,
        choices=WORK_TYPE_CHOICES,
        default='onsite'
    )

    visa_sponsorship = models.BooleanField(default=False)

    def __str__(self):
        return str(self.id) + ' - ' + self.title

class CartItem(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='cart_items'
    )

    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE,
        related_name='cart_items'
    )

    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'job')

    def __str__(self):
        return self.user.username + ' - ' + self.job.title

class Application(models.Model):
    id = models.AutoField(primary_key=True)
    note = models.TextField(max_length=500)
    date = models.DateTimeField(auto_now_add=True)
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.id) + ' - ' + self.job.title
class Report(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('reviewed', 'Reviewed'),
        ('dismissed', 'Dismissed'),
    ]

    reporter = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='submitted_reports'
    )

    reported_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reports_received',
        null=True,
        blank=True
    )

    reported_job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE,
        related_name='reports_received',
        null=True,
        blank=True
    )

    reason = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.reason
