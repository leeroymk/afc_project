# Generated by Django 4.2.1 on 2023-06-28 18:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fwa', '0002_assistentsepl_calendarmatches_goalscorersepl_statepl'),
    ]

    operations = [
        migrations.AddField(
            model_name='assistentsepl',
            name='season',
            field=models.CharField(default='', max_length=15),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='calendarmatches',
            name='season',
            field=models.CharField(default='', max_length=15),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='goalscorersepl',
            name='season',
            field=models.CharField(default='', max_length=15),
            preserve_default=False,
        ),
    ]