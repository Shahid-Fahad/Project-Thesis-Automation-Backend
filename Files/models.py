from django.db import models
from Users.models import Group

# Create your models here.
class Notice(models.Model):
    title = models.CharField(max_length=200)
    caption = models.TextField()
    related_file = models.FileField(upload_to='notices/')  

    def __str__(self):
        return self.title

class Group_Files(models.Model):
    group_id = models.ForeignKey(Group, related_name='group_files', on_delete=models.CASCADE)
    files = models.FileField(upload_to='group_files/')  

    def __str__(self):
        return f"File for Group: {self.group_id.id}"