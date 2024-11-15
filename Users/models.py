from django.db import models
from django.contrib.auth.models import User

class Supervisor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    designation = models.CharField(max_length=100)
    dept = models.CharField(max_length=100)
    employee_id = models.CharField(max_length=50, unique=True)  
    phone = models.CharField(max_length=15)  
    email = models.EmailField(unique=True)
    requested_groups = models.ManyToManyField("Group", related_name="requested_groups")

    def __str__(self):
        return self.name  

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    matric_id = models.CharField(max_length=10, unique=True) 
    name = models.CharField(max_length=200)
    batch = models.PositiveIntegerField()
    section = models.CharField(max_length=10)
    phone = models.CharField(max_length=15) 
    cgpa = models.FloatField(default=0)
    email = models.EmailField(unique=True) 
    department = models.CharField(max_length=100)
    obtained_marks = models.PositiveSmallIntegerField(null=True,blank=True)

    def __str__(self):
        return self.name

class Group(models.Model):
    supervisor = models.ForeignKey(Supervisor, null=True, on_delete=models.CASCADE, related_name="assigned_supervisors",blank=True)
    supervisor_choices = models.ManyToManyField(Supervisor, related_name="preferred_supervisors")
    students = models.ManyToManyField(Student, related_name="member_students")
    is_project = models.BooleanField(default=False)
    is_thesis = models.BooleanField(default=False)
    project_title = models.CharField(max_length=200, blank=True, null=True)
    comments = models.ManyToManyField(to="Users.Comment",related_name="group_comments",blank=True)
    files = models.ManyToManyField(to="Users.Files",related_name="group_files",blank=True)

    def __str__(self):
        if self.supervisor:
            return f"Group supervised by {self.supervisor.name}"
        else:
            student_matric_ids = ", ".join(student.matric_id for student in self.students.all())
            average_cgpa = self.students.aggregate(avg_cgpa=models.Avg('cgpa'))['avg_cgpa']
            avg_cgpa_formatted = f"{average_cgpa:.2f}" if average_cgpa is not None else "N/A"
            return f"Unassigned Group with students: {student_matric_ids} (Avg CGPA: {avg_cgpa_formatted})"

    
    # Custom method to calculate average CGPA
    def average_cgpa(self):
        # Calculate the average CGPA of the students in this group
        student_cgpas = self.students.values_list('cgpa', flat=True)
        if student_cgpas:
            return round(sum(student_cgpas) / len(student_cgpas), 2)
        return 0.0

    average_cgpa.short_description = 'Average CGPA'  # Label in the admin panel

class Comment(models.Model):
     user = models.ForeignKey(User, on_delete=models.CASCADE)
     text = models.CharField(max_length=1000)
     


class Files(models.Model):
    class FileType(models.IntegerChoices):
        PROPOSAL = 1, "Proposal"
        PRE_DEFENCE = 2, "Pre-Defence"
        DEFENCE = 3, "Defence"

    file = models.FileField(upload_to='uploads/',null=True)
    url = models.URLField(max_length=1000, blank=True, null=True)  # Add this field for S3 URL
    file_type = models.SmallIntegerField(choices=FileType.choices) 
