from django.shortcuts import render, redirect
from .models import Aluno
from .forms import frmAluno
from django.contrib import messages
from django.http import HttpResponse
# Create your views here.


# Gravar registro do Aluno
def gravar(request):
    print("gravar")
    try:
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        if is_ajax:
            if request.method == 'POST':
                form = frmAluno(request.POST)
                if form.is_valid():
                    form.save()
                    mensagem = criarMensagem("Aluno Registrado com Sucesso!","success")
                    
                    return mensagem
                else:
                    mensagem = criarMensagem("Aluno já existe!!","danger")
                    return mensagem
    except:
        pass
    
def retornarTabela(alunos):
    tabela = ''
    for aluno in alunos:
        tabela += " <tr><td class='align-middle'>" + str(aluno.rm) + "</td> \
                    <td class='align-middle'>"+aluno.nome+"</td> \
                        <td class='text-center conteudoAtualizar'>  \
                        <button type='button' class='btn btn-outline-dark btn-lg atualizar disabled' value="+str(aluno.rm)+"> \
                            <i class='bi bi-arrow-repeat'></i> \
                        </button> \
                    </td> "    
    return tabela
  
def criarMensagem(texto, tipo):
        
    mensagem = HttpResponse(f"<div style='display:block;' id='mensagem' class='alert alert-{tipo}' role='alert' >{texto} </div>")
    return  mensagem

def recarregarTabela(request):
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    print("recarregar",is_ajax)
    alunos = Aluno.retornarNUltimos()
    tabela = retornarTabela(alunos)
    return HttpResponse(tabela)

def buscar(request, nome):
    
    nome = request.GET.get("nome")
    print(nome)
    if len(nome) > 3:
        alunos = Aluno.objects.filter(nome__contains=nome)[:10]
        tabela = retornarTabela(alunos)
        if tabela != '':
            return HttpResponse(tabela)
        else:
            mensagem = criarMensagem("Aluno Não Encontrado", "info")
            return mensagem
    else:
        return recarregarTabela(request)
    
def atualizar(request, rm):
    
    if rm != '':
        rm = int(request.POST.get("rm"))
        print(rm)
        aluno = Aluno.objects.get(pk=rm)
        nome = request.POST.get("nome")
        aluno.nome = nome
        aluno.save()
        return criarMensagem(f"Registro de Aluno Atualizado com Sucesso!!! RM: {rm} - Nome (Atualizado): {nome}","success")
    else:
        return recarregarTabela(request)
        
    
    
def index(request):
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    print("index",is_ajax)
    # op = request.POST.get("codigo")
    # nome = request.POST.get("nome")
    # rm = request.POST.get("rm")
  
    # if is_ajax:
    #     if request.method == 'POST':
    #         form = frmAluno(request.POST)
    #         context['form'] = form
            # if op == 'atualizar':
            #     aluno = Aluno.objects.get(pk=rm)
            #     nome = request.POST.get("nome")
            #     aluno.nome = nome
            #     aluno.save()
                
    # else:
    # if request.method == 'GET':
    #     alunos = Aluno.retornarNUltimos()
    #     form = frmAluno()
    
    context = {
            'alunos': Aluno.retornarNUltimos(),
            'form': frmAluno()
        }
    
    return render(request,'index.html', context)
