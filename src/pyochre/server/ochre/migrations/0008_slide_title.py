# Generated by Django 4.2 on 2023-05-30 19:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ochre', '0007_alter_query_options_slide_active_slide_ordering'),
    ]

    operations = [
        migrations.AddField(
            model_name='slide',
            name='title',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
    ]
