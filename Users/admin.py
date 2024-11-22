from django.contrib import admin
from .models import Supervisor,Student, Group, Board
from django.db.models import Avg
from django.core.exceptions import ObjectDoesNotExist
from django.core.exceptions import ValidationError
import csv
from django.forms import forms
from django.contrib.auth.models import User
from django.utils.html import format_html
from django.contrib import admin, messages
from django.shortcuts import render, redirect
from django.urls import path
import io
from django.http import FileResponse
from django.contrib import admin
from reportlab.platypus import Paragraph, Table, TableStyle, SimpleDocTemplate
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from django.http import HttpResponse
from django.db import transaction

# Register your models here.


@admin.register(Supervisor)
class SupervisorAdmin(admin.ModelAdmin):
    list_display = ('name', 'designation', 'dept', 'employee_id', 'phone', 'email')
    filter_horizontal=('requested_groups',)
    actions = ["clear_request"]
    
    @admin.action(description="Clear Requests")
    def clear_request(self,request,queryset):
        for supervisor in queryset:
            supervisor.requested_groups.set([])
            supervisor.save()
    
@admin.register(Board)
class BoardAdmin(admin.ModelAdmin):
    list_display = ['id','board_chairmen']
    def save_model(self, request, obj, form, change):
        try:
            obj.save()  # This calls the `save` method in the model
        except ValidationError as e:
            # Add the validation error as a message to the admin interface
            self.message_user(request, f"Error: {e.message}", level=messages.ERROR)
            return  # Prevent saving if validation fails

        super().save_model(request, obj, form, change)

class ImportCSVForm(forms.Form):
    csv_file = forms.FileField()

# Define Grade Calculation
def calculate_grade(marks):
    percentage = (marks / 100) * 100
    if percentage >= 80:
        return "A+", 4.00
    elif percentage >= 75:
        return "A", 3.75
    elif percentage >= 70:
        return "A-", 3.50
    elif percentage >= 65:
        return "B+", 3.25
    elif percentage >= 60:
        return "B", 3.00
    elif percentage >= 55:
        return "B-", 2.75
    elif percentage >= 50:
        return "C+", 2.50
    elif percentage >= 45:
        return "C", 2.25
    elif percentage >= 40:
        return "D", 2.00
    else:
        return "F", 0.00



class StudentAdmin(admin.ModelAdmin):
    list_display = ('name', 'matric_id', 'batch', 'department')
    change_list_template = "admin/student_changelist.html"  # Custom template for the list view
    actions = ["generate_grade_sheet"]

    def delete_queryset(self, request, queryset):
        """
        Override delete_queryset to delete associated User objects.
        """
        for student in queryset:
            if student.user:  # Check if the student has an associated User
                student.user.delete()  # Delete the associated User
        super().delete_queryset(request, queryset)  # Delete the Student objects
        
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('import-csv/', self.import_csv, name='import_csv'),
            path('import-marks/', self.import_marks, name='import_marks'),
        ]
        return custom_urls + urls

    def import_marks(self, request):
        if request.method == 'POST':
            form = ImportCSVForm(request.POST, request.FILES)
            if form.is_valid():
                csv_file = form.cleaned_data['csv_file']
                reader = csv.reader(csv_file.read().decode('utf-8').splitlines())

                # Skip the header row if present
                next(reader, None)

                

                for row in reader:
                    try:
                        matric_id, external_marks = row
                        
                        student = Student.objects.filter(matric_id=matric_id).first()
                        student.external_marks = external_marks
                        student.save()

                        
                    except Exception as e:
                        messages.error(request, f"Error in row {row}: {e}")
                        continue

              

                messages.success(request, "Marks imported successfully!")
                return redirect("..")

        else:
            form = ImportCSVForm()

        return render(request, "admin/import_marks.html", {"form": form})
    
    def import_csv(self, request):
        if request.method == 'POST':
            form = ImportCSVForm(request.POST, request.FILES)
            if form.is_valid():
                csv_file = form.cleaned_data['csv_file']
                reader = csv.reader(csv_file.read().decode('utf-8').splitlines())

                # Skip the header row if present
                next(reader, None)


                existing_users = set(User.objects.values_list('username', flat=True))

                for row in reader:
                    if len(row) != 8:  # Validate row format
                        messages.error(request, f"Invalid row format: {row}")
                        continue
                    
                    

                    try:
                        matric_id, name, batch, section, phone, cgpa, email, department = [col.strip() for col in row]
                        matric_id = matric_id.lower()  # Normalize matric_id

                        if matric_id in existing_users:
                            continue

                        # Prepare User and Student objects
                        user = User.objects.create_user(username=matric_id, password="123456")
                        Student.objects.create(
                            user=user,
                            matric_id=matric_id,
                            name=name,
                            batch=int(batch),
                            section=section,
                            phone=phone,
                            cgpa=float(cgpa),
                            email=email,
                            department=department
                        )
                        
                        
                        # students_to_create.append(student)
                    except Exception as e:
                        messages.error(request, f"Error processing row {row}: {e}")
                        continue

                # with transaction.atomic():
                #     # Bulk create users
                #     created_users = User.objects.bulk_create(users_to_create)

                    # Map created users to their corresponding students
                    # user_map = {user.username: user for user in created_users}

                    # for student in students_to_create:
                    #     user = user_map.get(student.matric_id)
                    #     if user:
                    #         student.user = user
                    #         student.save()
                    #     else:
                    #         messages.error(request, f"User not found for Student: {student.matric_id}")

                messages.success(request, "Students imported successfully!")
                return redirect("..")

        else:
            form = ImportCSVForm()

        return render(request, "admin/import_csv.html", {"form": form})

    # Admin Action to Generate PDF
    
    @admin.action(description="Generate Tabular Grade Sheet as PDF")
    def generate_grade_sheet(modeladmin, request, queryset):
        # Create an in-memory buffer
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)

        # University Name and Grade Sheet Title
        styles = getSampleStyleSheet()
        header_style = styles["Title"]

        elements = [
            Paragraph("International Islamic University Chittagong", header_style),
            Paragraph("Grade Sheet", header_style),
            Paragraph("<br/>", styles["Normal"])  # Line break for spacing
        ]

        # Table Data (Header)
        data = [
            ["Name", "Matric ID", "Pre-Defense Marks", "Supervisor Marks", "External Marks", "Total Marks", "Grade"]
        ]

        # Populate Data
        for student in queryset:
            pre_defense = student.pre_defense_marks or 0
            supervisor = student.supervisor_marks or 0
            external = student.external_marks or 0
            total_marks = pre_defense + supervisor + external
            grade, _ = calculate_grade(total_marks)

            data.append([
                student.name,
                student.matric_id,
                pre_defense,
                supervisor,
                external,
                total_marks,
                grade
            ])

        # Create Table
        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),  # Header background
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),  # Header text color
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),             # Center alignment for all cells
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),   # Header font
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),           # Header padding
            ('GRID', (0, 0), (-1, -1), 1, colors.black),      # Add grid lines
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),   # Body background
        ]))

        # Add Table to Elements
        elements.append(table)

        # Build PDF
        doc.build(elements)

        # Prepare Response
        buffer.seek(0)
        return FileResponse(buffer, as_attachment=True, filename="grade_sheet.pdf")
admin.site.register(Student, StudentAdmin)


def generate_pdf(groups, filename, column, title):
    """Helper function to generate PDF."""
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}.pdf"'

    c = canvas.Canvas(response, pagesize=letter)
    width, height = letter

    # Set title
    c.setFont("Helvetica-Bold", 16)
    c.drawString(200, height - 50, title)

    # Table headers
    c.setFont("Helvetica-Bold", 12)
    x_start, y_start = 50, height - 100
    c.drawString(x_start, y_start, "Matric IDs")
    c.drawString(x_start + 200, y_start, "Supervisor")
    c.drawString(x_start + 400, y_start, column)

    y = y_start - 20
    c.setFont("Helvetica", 10)

    for group in groups:
        matric_ids = ", ".join(student.matric_id for student in group.students.all())
        supervisor_name = group.supervisor.name if group.supervisor else "No Supervisor"
        status = getattr(group, column.lower())

        c.drawString(x_start, y, matric_ids)
        c.drawString(x_start + 200, y, supervisor_name)
        c.drawString(x_start + 400, y, "Yes" if status else "No")
        y -= 20

        if y < 50:  # Start a new page if content exceeds the page
            c.showPage()
            y = height - 100

    c.save()
    return response

@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('project_title','average_cgpa', 'supervisor', 'is_project', 'is_thesis')
    filter_horizontal = ('students','supervisor_choices')
   
    fieldsets = [
        (None, {
            'fields': (
                'project_title',
                'supervisor',
                'supervisor_choices',
                'students',
                'is_project',
                'is_thesis',
                'proposal_board',
                'is_proposal_accepted',
                'pre_defense_board',
                'is_pre_defense_accepted',
                'defense_board',
                'is_defense_accepted',
                
                )
        })
    ]

     # Custom admin action
    actions = [
        'assign_supervisors_to_top_groups',
         "download_proposal_accepted_report",
        "download_pre_defense_accepted_report",
        "download_defense_accepted_report"
        ]

    def save_model(self, request, obj, form, change):
        try:
            obj.save()  # Call the `save` method in the model
        except ValidationError as e:
            # Handle ValidationError gracefully
            for message in e.messages:
                self.message_user(request, message, level=messages.ERROR)
            return  # Prevent saving the object if validation fails
        super().save_model(request, obj, form, change)

        
    # Custom action function
    def download_proposal_accepted_report(modeladmin, request, queryset):
        return generate_pdf(
            queryset,
            filename="proposal_accepted_report",
            column="is_proposal_accepted",
            title="Proposal Acceptance Report"
        )


    def download_pre_defense_accepted_report(modeladmin, request, queryset):
        """Generate a PDF report for pre-defense acceptance status."""
        return generate_pdf(
            queryset,
            filename="pre_defense_accepted_report",
            column="is_pre_defense_accepted",
            title="Pre-Defense Acceptance Report"
        )


    def download_defense_accepted_report(modeladmin, request, queryset):
        """Generate a PDF report for defense acceptance status."""
        return generate_pdf(
            queryset,
            filename="defense_accepted_report",
            column="is_defense_accepted",
            title="Defense Acceptance Report"
        )

    def assign_supervisors_to_top_groups(self, request, queryset):
        # Custom sorting function to handle tie-breaking
        def group_sort_key(group):
            # Get a sorted list of individual CGPAs (descending)
            individual_cgpas = sorted([student.cgpa for student in group.students.all()], reverse=True)
            # Append the group's creation time to the key to handle tie-breaking
            return (group.average_cgpa(), individual_cgpas, -group.id)

        # Order the queryset by average CGPA and additional tie-breaking rules
        sorted_groups = sorted(queryset, key=group_sort_key, reverse=True)

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
