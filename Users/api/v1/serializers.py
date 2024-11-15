# serializers.py
from rest_framework import serializers
from django.contrib.auth.models import User
from Users.models import Student,Supervisor,Group,Comment,Files
import boto3
from django.conf import settings
from AppConstants.models import (
   Constants,Notice
)

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
            'cgpa',
            'obtained_marks'
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



class CommentSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = Comment
        fields = ['id', 'username', 'text']
    def get_username(self,obj:Comment):
        if Supervisor.objects.filter(user=obj.user).exists():
            return Supervisor.objects.filter(user=obj.user).first().name
        elif Student.objects.filter(user=obj.user).exists():
            return Student.objects.filter(user=obj.user).first().name
        return ""




class FileSerializer(serializers.ModelSerializer):
    # Adding a file field to handle file uploads
    file = serializers.FileField(write_only=True)  # This field will allow file uploads

    class Meta:
        model = Files
        fields = ['id', 'file_type','url', 'file']  # Include 'file' in the fields

    def create(self, validated_data):
        uploaded_file = validated_data.pop('file')
        file_type = validated_data['file_type']
        file_name = f"{file_type}/{uploaded_file.name}"
        s3_url = self.upload_to_s3(uploaded_file, file_name)

        instance = Files.objects.create(
            url=s3_url, 
            file_type=file_type
        )

        return instance

    def upload_to_s3(self, file, file_name):
        s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME,
        )

        try:
            s3_client.upload_fileobj(
                file,
                settings.AWS_STORAGE_BUCKET_NAME,
                file_name,
                ExtraArgs={'ACL': 'public-read'}
            )
        except Exception as e:
            raise serializers.ValidationError(f"Failed to upload to S3: {e}")

        file_url = f"https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.{settings.AWS_S3_REGION_NAME}.amazonaws.com/{file_name}"
        return file_url


class GroupSerializer(serializers.ModelSerializer):
    students = StudentListSerializer(many=True, read_only=True)
    supervisor = SupervisorListSerializer(read_only=True)
    supervisor_choices = SupervisorListSerializer(many=True, read_only=True)
    average_cgpa = serializers.SerializerMethodField()
    comments = CommentSerializer(many=True, read_only=True)
    files = FileSerializer(many=True, read_only=True)
    proposal_deadline_date = serializers.SerializerMethodField()
    pre_defence_deadline_date = serializers.SerializerMethodField()
    defence_deadline_date = serializers.SerializerMethodField()

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
            'comments',
            'files',
            'proposal_deadline_date',
            'pre_defence_deadline_date',
            'defence_deadline_date'
        ]
    def get_average_cgpa(self,obj:Group):
        return obj.average_cgpa()
    
    def get_pre_defence_deadline_date(self,obj:Group):
        return Constants.get_pre_defence_deadline()
    def get_proposal_deadline_date(self,obj:Group):
        return Constants.get_proposal_deadline()
    def get_defence_deadline_date(self,obj:Group):
        return Constants.get_defence_deadline()
    
    
class StudentMarkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ['obtained_marks']
        
    def update(self, instance, validated_data):
        instance.obtained_marks = validated_data.get('obtained_marks', instance.obtained_marks)
        instance.save()
        return instance
    
class NoticeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notice
        fields = ['text']