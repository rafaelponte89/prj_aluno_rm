from django.shortcuts import render, redirect
from .models import Aluno
from .forms import frmAluno
from django.contrib import messages
from django.http import HttpResponse
from django.db.models import Q
# Create your views here.


def rodarTeste():
    for i in range(5000):
        aluno = Aluno(i,"Aluno"+ str(i))
        aluno.save()
        
# Gravar registro do Aluno
def gravar(request):
    print("gravar")
    tamanho = len(request.POST.get("nome"))
    try:
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        if is_ajax:
            if request.method == 'POST':
                form = frmAluno(request.POST)
                if form.is_valid():
                    if( tamanho > 3):
                
                        form.save()
                        
                       
                        mensagem = criarMensagem("Aluno Registrado com Sucesso!","success")
                        return mensagem
                    else:
                        mensagem = criarMensagem("Nome muito Pequeno!","warning")
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
    tamanho = len(request.POST.get("nome"))
    if rm != '':
        if(tamanho > 3):
            rm = int(request.POST.get("rm"))
            print(rm)
            aluno = Aluno.objects.get(pk=rm)
            nome = request.POST.get("nome")
            aluno.nome = nome
            aluno.save()
            return criarMensagem(f"Registro de Aluno Atualizado com Sucesso!!! RM: {rm} - Nome (Atualizado): {nome}","success")
        else:
            mensagem = criarMensagem("Nome muito Pequeno!","warning")
            return mensagem
    else:
        return recarregarTabela(request)

def gerarIntervalo(rm_inicial, rm_final):
    
    alunos = Aluno.objects.filter(Q(rm__gte=rm_inicial) & Q(rm__lte=rm_final))

    return alunos
    
def index(request):
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    print("index",is_ajax)
    rodarTeste()
    context = {
            'alunos': Aluno.retornarNUltimos(),
            'form': frmAluno()
        }
    return render(request,'index.html', context)


def baixar_pdf(request):
    import io
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Image
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from datetime import datetime
    rmi = int(request.GET.get("rmi"))
    rmf = int(request.GET.get("rmf"))
    maior = ''
    if rmi > rmf:
        maior = rmi
        rmi = rmf
        rmf = maior
    
    alunos = gerarIntervalo(rmi,rmf)
    elements = []
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=18)
    
    primeira_linha = ['RM', 'Nome']
    data_alunos = []
    data_alunos.append(primeira_linha)
    for i in range(len(alunos)):
        data_alunos.append([alunos[i].rm, alunos[i].nome])
    
    print(data_alunos)
    
    t_aluno = Table(data_alunos, style= ([('GRID',(0,0),(-1,-1), 0.5, colors.white),
                            ('LEFTPADDING',(0,0),(-1,-1),2),
                            ('TOPPADDING',(0,0),(-1,-1),2),
                            ('BOTTOMPADDING',(0,0),(-1,-1),2),
                            ('RIGHTPADDING',(0,0),(-1,-1),0),
                            ('ALIGN',(0,0),(-1,-1),'LEFT'),
                            ]),hAlign='LEFT')
    
   
    elements.append(t_aluno)
    
    doc.build(elements)
    nome_arquivo = str(rmi) + '_' + str(rmf) + datetime.strftime(datetime.now(),'_%d/%m/%Y_%H_%M_%S')
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename={nome_arquivo}.pdf'
    response.write(buffer.getvalue())
    buffer.close()

    return response
