# Generated by Django 4.1.7 on 2023-09-25 14:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('procesamiento', '0009_alter_progreso_cantidad_archivos'),
    ]

    operations = [
        migrations.AddField(
            model_name='progreso',
            name='uno_porciento',
            field=models.IntegerField(default=0),
        ),
    ]
