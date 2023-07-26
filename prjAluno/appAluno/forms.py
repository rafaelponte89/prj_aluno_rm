from django import forms
from .models import Aluno

class frmAluno(forms.ModelForm):
    nome = forms.CharField(max_length=150, required=True)
    
    nome.widget.attrs["class"] = "form-control"
    nome.widget.attrs["placeholder"] = "Nome do Aluno"
    
    def __str__(self):
        return self.nome
    
    class Meta:
        model = Aluno
        fields = ['nome']