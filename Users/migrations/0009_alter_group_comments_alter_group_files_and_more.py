# Generated by Django 4.2.9 on 2024-11-08 09:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Users', '0008_alter_group_comments_alter_group_files'),
    ]

    operations = [
        migrations.AlterField(
            model_name='group',
            name='comments',
            field=models.ManyToManyField(blank=True, related_name='group_comments', to='Users.comment'),
        ),
        migrations.AlterField(
            model_name='group',
            name='files',
            field=models.ManyToManyField(blank=True, related_name='group_files', to='Users.files'),
        ),
        migrations.AlterField(
            model_name='group',
            name='supervisor',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='assigned_supervisors', to='Users.supervisor'),
        ),
    ]