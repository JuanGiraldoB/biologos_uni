# Generated by Django 4.1.7 on 2023-03-14 20:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('procesamiento', '0003_progreso_cantidad'),
    ]

    operations = [
        migrations.AlterField(
            model_name='progreso',
            name='cantidad',
            field=models.IntegerField(default=100, null=True),
        ),
    ]
