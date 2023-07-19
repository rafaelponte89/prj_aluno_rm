from django.shortcuts import render, redirect
from .models import Aluno
from .forms import frmAluno
from django.contrib import messages
from django.http import HttpResponse
from django.db.models import Q

# Create your views here.
def buscar_duplicados():
    alunos = Aluno.objects.all()
    nomes_rm = {}
    duplicados = {}
    
    for aluno in alunos:
        
        if aluno.nome not in nomes_rm.keys():
            nomes_rm[aluno.nome] = [aluno.rm]
        else:
            nomes_rm[aluno.nome].append(aluno.rm)
    for k, v in nomes_rm.items():
        if len(v) > 1:
            duplicados[k] = v
    #print("Total Duplicados: ", len(duplicados))
    #print("\n",duplicados)
    return duplicados.keys()

def rodarTeste():
    j = 5000
    for i in range(5000):
        aluno = Aluno(j,"NOME "+ str(i) + "SOBRENOME1 "+ str(i) + "SOBRENOME2"+ str(i))
        j += 1
        aluno.save()
        
# Gravar registro do Aluno
def gravar(request):
    #print("gravar")
    tamanho = len(request.POST.get("nome").lstrip(' ').rstrip(''))
    try:
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        if is_ajax:
            if request.method == 'POST':
                form = frmAluno(request.POST)
                if form.is_valid():
                    if( tamanho > 3): 
                        #print(form.save()) 
                        form.save()       
                        mensagem = criarMensagem("Aluno Registrado com Sucesso!","success")
                        
                    else:
                        mensagem = criarMensagem("Nome muito Pequeno!","warning")
                else:
                    if tamanho > 3: 
                        mensagem = criarMensagem("Aluno já existe!!","danger")
                    else:
                        mensagem = criarMensagem("Nome em Branco!!","warning")
                return mensagem
                        
                        
    except:
        pass
    
def retornarTabela(alunos):
    nomes_duplicados = buscar_duplicados()
    tabela = ''
    icon_exclamacao = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-person-fill-exclamation" viewBox="0 0 16 16"> \
    <path d="M11 5a3 3 0 1 1-6 0 3 3 0 0 1 6 0Zm-9 8c0 1 1 1 1 1h5.256A4.493 4.493 0 0 1 8 12.5a4.49 4.49 0 0 1 1.544-3.393C9.077 9.038 8.564 9 8 9c-5 0-6 3-6 4Z"/> \
    <path d="M16 12.5a3.5 3.5 0 1 1-7 0 3.5 3.5 0 0 1 7 0Zm-3.5-2a.5.5 0 0 0-.5.5v1.5a.5.5 0 0 0 1 0V11a.5.5 0 0 0-.5-.5Zm0 4a.5.5 0 1 0 0-1 .5.5 0 0 0 0 1Z"/> \
    </svg>'
    for aluno in alunos:
        if aluno.nome in nomes_duplicados:
            advertencia = '<tr><td class="align-middle">' + str(aluno.rm) + \
            '<button type="button" class="btn btn-outline-warning m-2" data-bs-toggle="modal"  data-bs-target="#resolucaoDuplicidadeModal">'+icon_exclamacao+'</a></td>'
        else:
            advertencia = '<tr><td class="align-middle">' + str(aluno.rm) + '</td>'
            
        tabela += ' <tr>' + advertencia + \
                    '<td class="align-middle">'+aluno.nome+'</td> \
                        <td class="text-center conteudoAtualizar">  \
                        <button type="button" class="btn btn-outline-dark btn-lg atualizar disabled"  value='+str(aluno.rm)+'> \
                            <i class="bi bi-arrow-repeat"></i> \
                        </button> \
                    </td> </tr>'    
    return tabela
  
def criarMensagem(texto, tipo):
        
    mensagem = HttpResponse(f"<div style='display:block;' id='mensagem' class='alert alert-{tipo}' role='alert' >{texto} </div>")
    return  mensagem


    
    
def recarregarTabela(request):
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    #print("recarregar",is_ajax)
    alunos = Aluno.retornarNUltimos()
    tabela = retornarTabela(alunos)
    return HttpResponse(tabela)

def buscar(request, nome):
    nome = request.GET.get("nome").upper().rstrip().lstrip()
    tamanho = len(nome)
    #print(nome)
    if (tamanho > 3) :
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
    nome = request.POST.get("nome").lstrip().rstrip()
    tamanho = len(nome)
    if rm != '':
        if(tamanho > 3):
            rm = int(request.POST.get("rm"))
            #print(rm)
            aluno = Aluno.objects.get(pk=rm)
            aluno.nome = nome
            aluno.save()
            mensagem = criarMensagem(f"Registro de Aluno Atualizado com Sucesso!!! RM: {rm} - Nome (Atualizado): {nome}","success")
        else:
            if(tamanho == 0):
                mensagem = criarMensagem("Nome em Branco!!","warning")
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
   
    #print("index",is_ajax)
    #rodarTeste()
    context = {
            'form': frmAluno(),
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
    doc = SimpleDocTemplate(buffer, rightMargin=30, leftMargin=50, topMargin=30, bottomMargin=20)
    
    primeira_linha = ['RM', 'Nome']
    data_alunos = []
    data_alunos.append(primeira_linha)
    for i in range(len(alunos)):
        data_alunos.append([alunos[i].rm, alunos[i].nome])
    
    #print(data_alunos)
    
    style_table = TableStyle(([('GRID',(0,0),(-1,-1), 0.5, colors.white),
                            ('LEFTPADDING',(0,0),(-1,-1),6),
                            ('TOPPADDING',(0,0),(-1,-1),4),
                            ('BOTTOMPADDING',(0,0),(-1,-1),3),
                            ('RIGHTPADDING',(0,0),(-1,-1),6),
                            ('ALIGN',(0,0),(-1,-1),'LEFT'),
                             ('ALIGN',(0,0),(0,-1),'CENTER'),
                            ('BACKGROUND',(0,0),(1,0), colors.lavender),
                            ('LINEBELOW',(0,0),(-1,-1),1, colors.black),
                            ('FONTSIZE',(0,0), (-1,-1), 13)
                            ]))
    
  
    t_aluno = Table(data_alunos, style= style_table ,hAlign='LEFT', repeatRows=1)
    
    elements.append(t_aluno)
    
    doc.build(elements)
    nome_arquivo = str(rmi) + '_' + str(rmf) + datetime.strftime(datetime.now(),'_%d/%m/%Y_%H_%M_%S')
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename={nome_arquivo}.pdf'
    response.write(buffer.getvalue())
    buffer.close()

    return response
