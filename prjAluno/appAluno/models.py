from django.db import models


# Create your models here.



    
# Aluno
class Aluno (models.Model):
    rm = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=150)
    cancelado = models.BooleanField(default=False)
    ra = models.CharField(max_length=100,default='')
    d_ra = models.CharField(max_length=1, default='')
    data_nascimento = models.CharField(max_length=10, default='')
    

    def __str__(self):
       
        return f'[{self.rm}] {self.nome}'
    
    
    # Retorna o último aluno no banco de dados
    def retornarUltimo():
        aluno = Aluno.objects.last()
        return aluno
    
    def retornarNUltimos(n=5):
        alunos = Aluno.objects.order_by('-rm')[:n]
        return alunos
    
#Telefones do aluno (NÃO IMPLEMENTADO)
class Telefones(models.Model):
    TEL_CHOICES = (
        ('M','MÓVEL'),
        ('F','FIXO')
    )
    rm = models.ForeignKey(Aluno, on_delete=models.RESTRICT)
    tel_tipo = models.CharField(max_length=1, choices=TEL_CHOICES, blank=False, null=False)
    tel_desc = models.CharField(max_length=10)
    
#Documentos do aluno (NÃO IMPLEMENTADO)
class Documento(models.Model):
    DOCUMENTO_CHOICES = (
        ('CN','Certidão de Nascimento'),
        ('RGA','RG - Aluno'),
        ('CPFA','CPF - Aluno'),
        ('CV','Carteira Vacinação'),
        ('RGR','RG - Responsável'),
        ('CPFR','CPF - Responsável'),
        ('CNH','CNH'),
        ('FM','Ficha de Matrícula'),
        ('CR','Comprovante de Residência'),
        ('LD','Laudo'),
        ('OT','Outros')
    )
    #aluno = models.ForeignKey(Aluno)
    descricao = models.CharField(max_length=4, choices=DOCUMENTO_CHOICES, blank=False, null=False) 
    caminho = models.ImageField()

    
    

    