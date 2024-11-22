from django.conf import settings
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from Users.models import Board
from django.core.exceptions import ValidationError

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)

@receiver(post_save, sender=Board)
def validate_board_chairman(sender, instance, **kwargs):
    """
    Ensures that the board chairman is also a member of the board.
    This validation happens before saving the instance.
    """
    # Avoid validation for an unsaved instance
    if instance.board_chairmen and instance.board_chairmen not in instance.board_members.all():
        instance.board_chairmen = instance.board_members.first()
        instance.save()
        raise ValidationError(f"Board chairman must be a board member.Making {instance.board_chairmen} as board chairmen.Update if required.")