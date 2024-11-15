from rest_framework.permissions import BasePermission
from .models import Group

class IsGroupSupervisor(BasePermission):
    def has_permission(self, request, view):
        # Fetch the student object
        student_id = view.kwargs.get('pk')
        try:
            group = Group.objects.get(students__id=student_id)
            # Check if the current user is the group's supervisor
            return group.supervisor and group.supervisor.user == request.user
        except Group.DoesNotExist:
            return False
