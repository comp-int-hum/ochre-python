# Generated by Django 4.2 on 2023-07-19 01:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ochre', '0019_course_researchartifact_creators_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='researchproject',
            name='artifacts',
            field=models.ManyToManyField(related_name='related_to', to='ochre.researchartifact'),
        ),
    ]
