# Generated by Django 4.2 on 2023-06-28 12:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ochre', '0013_article_delete_slide_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='researchartifact',
            name='year',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
    ]
