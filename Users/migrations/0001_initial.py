# Generated by Django 4.2.9 on 2024-11-01 06:22

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_project', models.BooleanField(default=False)),
                ('is_thesis', models.BooleanField(default=False)),
                ('project_title', models.CharField(blank=True, max_length=200, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Supervisor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('designation', models.CharField(max_length=100)),
                ('dept', models.CharField(max_length=100)),
                ('employee_id', models.CharField(max_length=50, unique=True)),
                ('phone', models.CharField(max_length=15)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('requested_groups', models.ManyToManyField(related_name='requested_groups', to='Users.group')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Student',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('matric_id', models.CharField(max_length=10, unique=True)),
                ('name', models.CharField(max_length=200)),
                ('batch', models.PositiveIntegerField()),
                ('section', models.CharField(max_length=10)),
                ('phone', models.CharField(max_length=15)),
                ('cgpa', models.IntegerField(default=0)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('department', models.CharField(max_length=100)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='group',
            name='students',
            field=models.ManyToManyField(to='Users.student'),
        ),
        migrations.AddField(
            model_name='group',
            name='supervisor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='assigned_supervisors', to='Users.supervisor'),
        ),
        migrations.AddField(
            model_name='group',
            name='supervisor_choices',
            field=models.ManyToManyField(related_name='preferred_supervisors', to='Users.supervisor'),
        ),
    ]
