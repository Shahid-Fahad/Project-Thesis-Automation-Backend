from django.contrib import admin
from .models import Notice, Group_Files

# Register your models here.
@admin.register(Notice)
class NoticeAdmin(admin.ModelAdmin):
    list_display = ('title', 'caption', 'related_file')
    list_filter = ('title',)

@admin.register(Group_Files)
class GroupFilesAdmin(admin.ModelAdmin):
    list_display = ('group_id', 'files')