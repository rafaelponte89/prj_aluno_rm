# Generated by Django 4.2.3 on 2023-10-29 03:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appAluno', '0007_classe_matricula_prontuario_telefone_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='telefone',
            name='numero',
            field=models.CharField(default='', max_length=10),
        ),
    ]
