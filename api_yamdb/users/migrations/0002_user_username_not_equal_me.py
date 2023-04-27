# Generated by Django 3.2 on 2023-04-27 09:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='user',
            constraint=models.CheckConstraint(check=models.Q(_negated=True, username='me'), name='username_not_equal_me'),
        ),
    ]