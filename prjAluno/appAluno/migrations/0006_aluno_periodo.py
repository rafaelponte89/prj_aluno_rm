# Generated by Django 4.2.3 on 2023-10-23 02:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appAluno', '0005_documento_aluno_ano_aluno_serie_aluno_turma_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='aluno',
            name='periodo',
            field=models.CharField(choices=[('M', 'MANHÃ'), ('T', 'TARDE')], default='', max_length=1),
        ),
    ]