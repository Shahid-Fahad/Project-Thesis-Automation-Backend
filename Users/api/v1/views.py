# views.py
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from Users.models import Student, Supervisor, Group
from .serializers import (
    StudentRegistrationSerializer, LoginSerializer, StudentListSerializer,
                         GroupCreateSerializer, SupervisorListSerializer,GroupCreateSerializer, GroupSerializer
                    )
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import logout
from django.shortcuts import get_object_or_404

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = StudentRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Registration successful. Please log in."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                return Response({"message": "Login successful"}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Invalid username or password"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LogoutView(APIView):
    def post(self, request):
        logout(request)
        return Response({"message": "Successfully logged out."}, status=status.HTTP_200_OK)
    
class StudentListAPIView(ListAPIView):
    pagination_class = None
    queryset = Student.objects.all()
    serializer_class = StudentListSerializer

class SupervisorListAPIView(ListAPIView):
    pagination_class = None
    queryset = Supervisor.objects.all()
    serializer_class = SupervisorListSerializer


class GroupCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # The logged-in student should be the one creating the group
        serializer = GroupCreateSerializer(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            group = serializer.save()
            return Response({
                'message': 'Group created successfully.',
                'group_id': group.id,
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class AcceptGroupAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, group_id):
        try:
            supervisor = Supervisor.objects.get(user=request.user)
            group = supervisor.requested_groups.get(id=group_id)
            
            group.supervisor = supervisor
            group.save()

            # Remove the group from the supervisor's requested_groups
            supervisor.requested_groups.remove(group)
            
            return Response({"detail": "Group accepted successfully."}, status=status.HTTP_200_OK)
        except Supervisor.DoesNotExist:
            return Response({"detail": "Supervisor not found."}, status=status.HTTP_404_NOT_FOUND)
        except Group.DoesNotExist:
            return Response({"detail": "Group not found in requested groups."}, status=status.HTTP_404_NOT_FOUND)


class RejectGroupAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, group_id):
        try:
            supervisor = Supervisor.objects.get(user=request.user)
            group = supervisor.requested_groups.get(id=group_id)
            
            # Remove group from current supervisor's requested groups
            supervisor.requested_groups.remove(group)
            
            # Get the next supervisor in the supervisor_choices list, if available
            supervisor_choices = list(group.supervisor_choices.all())
            if supervisor in supervisor_choices:
                current_index = supervisor_choices.index(supervisor)
                if current_index + 1 < len(supervisor_choices):
                    next_supervisor = supervisor_choices[current_index + 1]
                    next_supervisor.requested_groups.add(group)

            return Response({"detail": "Group rejected and next supervisor notified."}, status=status.HTTP_200_OK)
        except Supervisor.DoesNotExist:
            return Response({"detail": "Supervisor not found."}, status=status.HTTP_404_NOT_FOUND)
        except Group.DoesNotExist:
            return Response({"detail": "Group not found in requested groups."}, status=status.HTTP_404_NOT_FOUND)


class RequestedGroupsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        supervisor = Supervisor.objects.get(user=request.user.id)
        requested_groups = supervisor.requested_groups.all()
        serializer = GroupSerializer(requested_groups, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class UserInfoAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        # Check if the user is a student
        if hasattr(user, 'student'):
            student = get_object_or_404(Student, user=user)
            group = Group.objects.filter(students=student).first()

            if group:
                if group.supervisor:
                    group_data = GroupSerializer(group).data
                else:
                    group_data = {"status": "Pending assignment to a supervisor"}
            else:
                group_data = {"status": "No group assigned"}

            student_data = StudentListSerializer(student).data
            student_data['groups'] = [group_data]
            student_data['in_group'] = True if group else False
            return Response(student_data)

        # Check if the user is a supervisor
        elif hasattr(user, 'supervisor'):
            supervisor = get_object_or_404(Supervisor, user=user)
            groups = Group.objects.filter(supervisor=supervisor)
            groups_data = GroupSerializer(groups, many=True).data

            supervisor_data = SupervisorListSerializer(supervisor).data
            supervisor_data['groups'] = groups_data
            supervisor_data['dept'] = supervisor.dept
            supervisor_data['has_request'] = True if supervisor.requested_groups.count()>0 else False
            return Response(supervisor_data)

        # Default response if user is neither
        return Response({"error": "User is neither a student nor a supervisor"}, status=400)