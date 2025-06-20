# Generated by Django 5.2.2 on 2025-06-13 13:59

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_alter_user_is_customer_alter_user_is_worker'),
    ]

    operations = [
        migrations.AddField(
            model_name='job',
            name='assigned_worker',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='assigned_jobs', to='api.worker'),
        ),
        migrations.AlterField(
            model_name='user',
            name='is_customer',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='user',
            name='is_worker',
            field=models.BooleanField(default=False),
        ),
    ]
