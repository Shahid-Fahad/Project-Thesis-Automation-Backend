from django.contrib import admin
from .models import Supervisor,Student, Group
from django.db.models import Avg
from django.core.exceptions import ObjectDoesNotExist
# Register your models here.

@admin.register(Supervisor)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('name', 'designation', 'dept', 'employee_id', 'phone', 'email')
    filter_horizontal=('requested_groups',)

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ( 'name', 'batch', 'section', 'phone', 'email', 'department')

@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('project_title','average_cgpa', 'supervisor', 'is_project', 'is_thesis')
    filter_horizontal = ('students','supervisor_choices')
    
     # Custom admin action
    actions = ['assign_supervisors_to_top_groups']

    # Custom action function
    def assign_supervisors_to_top_groups(self, request, queryset):
        # Order the queryset by average CGPA
        sorted_groups = sorted(queryset, key=lambda group: group.average_cgpa(), reverse=True)
        
        # Split into top and bottom halves
        midpoint = len(sorted_groups) // 2
        top_half_groups = sorted_groups[:midpoint]

        for group in top_half_groups:
            # Try to get the first supervisor choice for the group
            try:
                first_choice_supervisor = group.supervisor_choices.first()
                if first_choice_supervisor:
                    # Add the group to the supervisor's requested_groups field
                    first_choice_supervisor.requested_groups.add(group)
                    self.message_user(request, f"Sent assigning request for '{group}' to supervisor '{first_choice_supervisor.name}'.")
                else:
                    self.message_user(request, f"Group '{group}' has no supervisor choices.", level="warning")
            except ObjectDoesNotExist:
                self.message_user(request, f"Group '{group}' could not be assigned due to missing supervisor.", level="error")

    assign_supervisors_to_top_groups.short_description = "Assign supervisors to top half of selected groups based on CGPA"