# Generated by Django 5.2.2 on 2025-06-13 11:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_alter_payment_method'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='role',
            field=models.CharField(blank=True, choices=[('worker', 'Worker'), ('customer', 'Customer')], max_length=20, null=True),
        ),
    ]
