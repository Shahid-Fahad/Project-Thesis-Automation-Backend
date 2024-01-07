from django.db import models

# Create your models here.

class Teacher(models.Model):
    name = models.CharField(max_length=200)
    designation = models.CharField(max_length=100)
    dept = models.CharField(max_length=100)
    employee_id = models.CharField(max_length=50, unique=True)  
    phone = models.CharField(max_length=15)  
    email = models.EmailField(unique=True)  

    def __str__(self):
        return self.name  

class Student(models.Model):
    matric_id = models.CharField(max_length=10, unique=True) 
    name = models.CharField(max_length=200)
    batch = models.PositiveIntegerField()
    section = models.CharField(max_length=10)
    phone = models.CharField(max_length=15)  
    email = models.EmailField(unique=True)  
    department = models.CharField(max_length=100)

    def __str__(self):
        return self.name


    
class Group(models.Model):
    supervisor = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    students = models.ManyToManyField(Student)
    is_project = models.BooleanField(default=False)
    is_thesis = models.BooleanField(default=False)
    project_title = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return f"Group supervised by {self.supervisor.name}"