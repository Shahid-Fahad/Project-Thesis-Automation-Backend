# serializers.py
from rest_framework import serializers
from django.contrib.auth.models import User
from Users.models import Student,Supervisor,Group

class StudentRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = Student
        fields = ['password', 'matric_id', 'cgpa', 'name', 'batch', 'section', 'phone', 'email', 'department']

    def create(self, validated_data):
        user_data = {
            'username': validated_data['matric_id'],
            'password': validated_data.pop('password'),
        }
        user = User.objects.create_user(**user_data)
        student = Student.objects.create(user=user, **validated_data)
        return student

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

class SupervisorListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supervisor
        fields = [
                'id',
                'name',
                'designation'
        ]

    
class StudentListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = [
            'id',
            'name',
            'matric_id',
            'cgpa'
        ]
    
class GroupCreateSerializer(serializers.ModelSerializer):
    supervisor_choices = serializers.PrimaryKeyRelatedField(
        queryset=Supervisor.objects.all(), 
        many=True
    )
    students = serializers.PrimaryKeyRelatedField(
        queryset=Student.objects.all(), 
        many=True
    )

    class Meta:
        model = Group
        fields = ['supervisor_choices', 'students', 'is_project', 'is_thesis', 'project_title']

    def validate(self, data):
        # Check if there are exactly 3 students
        if len(data['students']) != 3:
            raise serializers.ValidationError("A group must have exactly 3 members.")
        
        # Check if there are exactly 3 supervisor choices
        if len(data['supervisor_choices']) != 3:
            raise serializers.ValidationError("You must choose exactly 3 supervisors.")
        
        # # Check if the requesting student is already in a group
        # student = self.context['request'].user
        # if Group.objects.filter(students=student).exists():
        #     raise serializers.ValidationError("You are already in a group.")
        
        return data

    def create(self, validated_data):
        supervisor_choices = validated_data.pop('supervisor_choices')
        students = validated_data.pop('students')

        # Create the group with the validated data
        group = Group.objects.create(**validated_data)

        # Add supervisor choices and students
        group.supervisor_choices.set(supervisor_choices)
        group.students.set(students)
        group.save()
        
        return group
    # Fields to accept supervisor and student IDs
    supervisor_choices = serializers.PrimaryKeyRelatedField(queryset=Supervisor.objects.all(), many=True)
    students = serializers.PrimaryKeyRelatedField(queryset=Student.objects.all(), many=True)

    class Meta:
        model = Group
        fields = ['supervisor_choices', 'students', 'is_project', 'is_thesis', 'project_title']

    def create(self, validated_data):
        students = validated_data.pop('students')
        supervisor_choices = validated_data.pop('supervisor_choices')
        group = Group.objects.create(**validated_data)
        group.students.set(students)
        group.supervisor_choices.set(supervisor_choices)
        return group

    class Meta:
        model = Supervisor
        fields = ['id', 'name', 'designation']

class GroupSerializer(serializers.ModelSerializer):
    students = StudentListSerializer(many=True, read_only=True)
    supervisor = SupervisorListSerializer(read_only=True)
    supervisor_choices = SupervisorListSerializer(many=True, read_only=True)
    average_cgpa = serializers.SerializerMethodField()

    class Meta:
        model = Group
        fields = [
            'id',
            'supervisor',
            'supervisor_choices',
            'students',
            'is_project',
            'is_thesis',
            'project_title',
            'average_cgpa',
        ]
    def get_average_cgpa(self,obj:Group):
        return obj.average_cgpa()