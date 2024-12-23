# Generated by Django 4.2.9 on 2024-11-15 17:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Users', '0011_alter_student_cgpa'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='comment_type',
            field=models.SmallIntegerField(choices=[(1, 'Proposal'), (2, 'Pre-Defense'), (3, 'Defense'), (4, 'GENERAL')], default=4),
        ),
        migrations.AddField(
            model_name='group',
            name='is_defense_accepted',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='group',
            name='is_pre_defense_accepted',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='group',
            name='is_proposal_accepted',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='student',
            name='external_marks',
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='student',
            name='pre_defense_marks',
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='student',
            name='supervisor_marks',
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='files',
            name='file_type',
            field=models.SmallIntegerField(choices=[(1, 'Proposal'), (2, 'Pre-Defense'), (3, 'Defense')]),
        ),
        migrations.CreateModel(
            name='Board',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('board_chairmen', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='board_chairmen', to='Users.supervisor')),
                ('board_members', models.ManyToManyField(related_name='board_members', to='Users.supervisor')),
            ],
        ),
        migrations.AddField(
            model_name='group',
            name='defense_board',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='defense_board', to='Users.board'),
        ),
        migrations.AddField(
            model_name='group',
            name='pre_defense_board',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='pre_defense_board', to='Users.board'),
        ),
        migrations.AddField(
            model_name='group',
            name='proposal_board',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='proposal_board', to='Users.board'),
        ),
    ]
