# Generated by Django 4.2 on 2023-08-01 21:18

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ochre', '0024_alter_article_date'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='researchartifact',
            name='creators',
        ),
        migrations.AddField(
            model_name='researchartifact',
            name='contributors',
            field=models.ManyToManyField(related_name='contributed_to', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='article',
            name='date',
            field=models.DateField(),
        ),
    ]