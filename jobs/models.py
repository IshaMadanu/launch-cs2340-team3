from django.db import models

# Create your models here.
class Job(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    salary = models.IntegerField()
    skills = models.TextField()
    location = models.TextField()
    description = models.TextField()
    image = models.ImageField(upload_to='job_images/')
    def __str__(self):
        return str(self.id) + ' - ' + self.title