from django.db import models

# Create your models here.
class Notice(models.Model):
    text = models.CharField(max_length=2000)
    sort_weight = models.IntegerField(default=1000)

class Constants(models.Model):
    maximum_number_of_group_per_supervisor = models.PositiveSmallIntegerField(default=8)
    minimum_number_of_group_per_supervisor = models.PositiveSmallIntegerField(default=2)
    proposal_deadline = models.DateField(null=True,blank=True)
    pre_defence_deadline = models.DateField(null=True,blank=True)
    defence_deadline = models.DateField(null=True,blank=True)
    
    @classmethod 
    def get_constants(cls):
        """Returns the singleton instance of Constants."""
        return cls.objects.first()
    @classmethod
    def get_maximum_number_of_group_per_supervisor(cls):
        """Returns the maximum number of groups per supervisor."""
        constants = cls.get_constants()
        return constants.maximum_number_of_group_per_supervisor if constants else None
    @classmethod
    def get_minimum_number_of_group_per_supervisor(cls):
        """Returns the minimum number of groups per supervisor."""
        constants = cls.get_constants()
        return constants.minimum_number_of_group_per_supervisor if constants else None
    @classmethod
    def get_proposal_deadline(cls):
        """Returns the proposal deadline."""
        constants = cls.get_constants()
        return constants.proposal_deadline if constants else None
    @classmethod
    def get_pre_defence_deadline(cls):
        """Returns the pre-defence deadline."""
        constants = cls.get_constants()
        return constants.pre_defence_deadline if constants else None
    @classmethod
    def get_defence_deadline(cls):
        """Returns the defence deadline."""
        constants = cls.get_constants()
        return constants.defence_deadline if constants else None
    