# Generated by Django 4.2 on 2023-05-01 22:31

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ochre', '0005_documentation_ochre_documentation_unique_name_and_user_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='annotation',
            name='primarysources',
        ),
        migrations.RemoveField(
            model_name='annotation',
            name='queries',
        ),
        migrations.AddField(
            model_name='annotation',
            name='primarysource',
            field=models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, to='ochre.primarysource'),
        ),
        migrations.AddField(
            model_name='annotation',
            name='user',
            field=models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='annotator', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='annotation',
            name='machinelearningmodel',
            field=models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, to='ochre.machinelearningmodel'),
        ),
    ]
