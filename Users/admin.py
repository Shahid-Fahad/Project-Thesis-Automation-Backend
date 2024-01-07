from django.contrib import admin
from .models import Teacher, Student, Group
# Register your models here.

@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('name', 'designation', 'dept', 'employee_id', 'phone', 'email')

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('matric_id', 'name', 'batch', 'section', 'phone', 'email', 'department')

@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('supervisor', 'is_project', 'is_thesis', 'project_title')
    filter_horizontal = ('students',)