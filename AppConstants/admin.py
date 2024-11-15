from django.contrib import admin
from AppConstants.models import Notice, Constants
# Register your models here.
@admin.register(Notice)
class NoticeAdmin(admin.ModelAdmin):
    fields = ['text','sort_weight']

@admin.register(Constants)
class ConstantAdmin(admin.ModelAdmin):
    fields = ['maximum_number_of_group_per_supervisor','minimum_number_of_group_per_supervisor','proposal_deadline','pre_defence_deadline','defence_deadline']