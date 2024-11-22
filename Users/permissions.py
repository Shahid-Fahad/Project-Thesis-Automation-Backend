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

class IsBoardChairmen(BasePermission):
    def has_permission(self, request, view):
        # Fetch the student object
        student_id = view.kwargs.get('pk')
        try:
            group = Group.objects.get(students__id=student_id)
            # Check if the current user is the group's supervisor
            return group.pre_defense_board and group.pre_defense_board.board_chairmen.user == request.user
        except Group.DoesNotExist:
            return False

class IsSupervisorOrBoardChairmenOfStudent(BasePermission):
    def has_permission(self, request, view):
        # Fetch the student object
        student_id = view.kwargs.get('pk')
        try:
            group = Group.objects.get(students__id=student_id)
            # Check if the current user is either the supervisor or the board chairperson
            is_supervisor = group.supervisor and group.supervisor.user == request.user
            is_board_chairmen = (
                group.pre_defense_board 
                and group.pre_defense_board.board_chairmen.user == request.user
            )
            print("SSSS", is_supervisor, is_board_chairmen)
            return is_supervisor or is_board_chairmen
        except Group.DoesNotExist:
            return False
        
class IsSupervisorOrBoardChairmenOfGroup(BasePermission):
    def has_permission(self, request, view):
        # Fetch the student object
        group_id = view.kwargs.get('pk')
        try:
            group = Group.objects.get(id=group_id)
            print("DD", group_id, group)
            # Check if the current user is either the supervisor or the board chairperson
            is_supervisor = group.supervisor and group.supervisor.user == request.user
            is_board_chairmen = (
                group.pre_defense_board 
                and group.pre_defense_board.board_chairmen.user == request.user
            )
            print("SSSS", is_supervisor, is_board_chairmen)
            return is_supervisor or is_board_chairmen
        except Group.DoesNotExist:
            return False