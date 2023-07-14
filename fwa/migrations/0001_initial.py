# Generated by Django 4.2.1 on 2023-07-14 22:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Teams',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
                ('url', models.URLField(null=True)),
                ('slug', models.CharField(max_length=25, null=True)),
                ('logo', models.URLField(null=True)),
                ('league', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='StatEpl',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('position', models.IntegerField()),
                ('matches', models.IntegerField()),
                ('win', models.IntegerField()),
                ('draw', models.IntegerField()),
                ('loss', models.IntegerField()),
                ('scored', models.IntegerField()),
                ('conceded', models.IntegerField()),
                ('points', models.IntegerField()),
                ('season', models.CharField(max_length=15)),
                ('team', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='fwa.teams')),
            ],
        ),
        migrations.CreateModel(
            name='News',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField()),
                ('title', models.TextField()),
                ('source', models.URLField(unique=True)),
                ('team', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='fwa.teams')),
            ],
        ),
        migrations.CreateModel(
            name='GoalscorersEPL',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('position', models.IntegerField()),
                ('player', models.CharField(max_length=50)),
                ('goals', models.IntegerField()),
                ('season', models.CharField(max_length=15)),
                ('team', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='fwa.teams')),
            ],
        ),
        migrations.CreateModel(
            name='CalendarMatches',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_match', models.DateTimeField()),
                ('tournament', models.CharField(max_length=50)),
                ('place_match', models.CharField(max_length=10)),
                ('match_score', models.CharField(max_length=10)),
                ('season', models.CharField(max_length=15)),
                ('rival', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rival', to='fwa.teams')),
                ('team', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='fwa.teams')),
            ],
        ),
        migrations.CreateModel(
            name='AssistantsEPL',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('position', models.IntegerField()),
                ('player', models.CharField(max_length=50)),
                ('assists', models.IntegerField()),
                ('season', models.CharField(max_length=15)),
                ('team', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='fwa.teams')),
            ],
        ),
    ]
