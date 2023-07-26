from django.db import models


# Create your models here.


    
class Aluno (models.Model):
    rm = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=150)
    cancelado = models.BooleanField(default=False)

    

        
    def __str__(self):
       
        return f'[{self.rm}] {self.nome}'
    
    
    # Retorna o último aluno no banco de dados
    def retornarUltimo():
        aluno = Aluno.objects.last()
        return aluno
    
    def retornarNUltimos(n=5):
        alunos = Aluno.objects.order_by('-rm')[:n]
        return alunos
    
    
    
    
    

    