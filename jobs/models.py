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