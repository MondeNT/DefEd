# Generated by Django 5.1.5 on 2025-02-01 19:52

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recognition', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='leaderboard',
            name='game',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='leaderboard', to='recognition.game'),
        ),
        migrations.AlterField(
            model_name='leaderboard',
            name='player',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='leaderboard_entries', to='recognition.playerprofile'),
        ),
        migrations.AlterField(
            model_name='playerscore',
            name='game',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='scores', to='recognition.game'),
        ),
        migrations.AlterField(
            model_name='playerscore',
            name='player',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='scores', to='recognition.playerprofile'),
        ),
    ]
