# Generated by Django 4.1.7 on 2023-04-04 23:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('procesamiento', '0008_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='progreso',
            name='cantidad_archivos',
            field=models.IntegerField(default=0, null=True),
        ),
    ]
