from django.shortcuts import render, redirect
from .models import Aluno
from .forms import frmAluno
from django.contrib import messages
from django.http import HttpResponse
from django.db.models import Q


        
    
# Create your views here.
def buscar_duplicados(alunos):
   
    nomes_rm = {}
    duplicados = {}
    for aluno in alunos:
        
        if aluno.cancelado != True:
            if aluno.nome not in nomes_rm.keys():
                nomes_rm[aluno.nome] = [aluno.rm]
            else:
                nomes_rm[aluno.nome].append(aluno.rm)
   
    for k, v in nomes_rm.items():
        if len(v) > 1:
            duplicados[k] = v
            
    return duplicados.keys()

def rodarTeste():
    j = 0
    for i in range(4999):
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
    
def atualizarTabela(alunos):
    nomes_duplicados = buscar_duplicados(alunos)
    tabela = ''
    print("Duplicados",nomes_duplicados)
    
    for aluno in alunos:
        if aluno.cancelado:
            status_rm = '<tr><td class="align-middle">' + str(aluno.rm) + '</td>'
            
            botao = '<button type="button" class="btn btn-outline-danger btn-lg  disabled"  value='+str(aluno.rm)+'> \
                            <i class="bi bi-x-circle-fill"></i> \
                        </button>' 
        else:
            if aluno.nome in nomes_duplicados:
                status_rm = '<tr><td class="align-middle">' + str(aluno.rm) + \
                '<button "type="button" class="btn btn-outline-primary m-2 advertencia" value='+str(aluno.rm)+' data-bs-toggle="modal" data-bs-target="#resolucaoDuplicidadeModal" ><i class="bi bi-person-fill-exclamation"></i></button></a></td>'
                botao = '<button type="button" class="btn btn-outline-dark btn-lg atualizar disabled"  value='+str(aluno.rm)+'> \
                            <i class="bi bi-arrow-repeat"></i> \
                        </button>'
            else:
                status_rm = '<tr><td class="align-middle">' + str(aluno.rm) + '</td>'
                botao = '<button type="button" class="btn btn-outline-dark btn-lg atualizar disabled"  value='+str(aluno.rm)+'> \
                            <i class="bi bi-arrow-repeat"></i> \
                        </button>'
                
                             
            
        tabela += ' <tr>' + status_rm + \
                    '<td class="align-middle">'+aluno.nome+'</td> \
                        <td class="text-center conteudoAtualizar">' \
                        +botao+ \
                    '</td> </tr>'    
                    
                    
    #print("Atualizar Tabela", tabela)
    return HttpResponse(tabela)
  
def criarMensagem(texto, tipo):
        
    mensagem = HttpResponse(f"<div style='display:block;' id='mensagem' class='alert alert-{tipo}' role='alert' >{texto} </div>")
    return  mensagem

def cancelarRM(request, rm):
    rm_req = int(request.POST.get('rm'))
    aluno = Aluno.objects.get(pk=rm_req)
    aluno.cancelado = True
    aluno.save()
    return criarMensagem(f"{aluno.nome} - {aluno.rm} : Cancelado!!!","success")
       
def recarregarTabela(request):
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    #print("recarregar",is_ajax)
    alunos = Aluno.retornarNUltimos()
    tabela = atualizarTabela(alunos)
    return tabela

def buscar(request, nome):
    nome = request.GET.get("nome").upper().rstrip().lstrip()
    tamanho = len(nome)
    print(nome)
    if (tamanho > 3) :
        alunos = Aluno.objects.filter(nome__contains=nome)[:10]
        buscar_duplicados(alunos)
        tabela = atualizarTabela(alunos)
        
        
        if len(tabela.content)>0:
           
            return tabela
        else:
            mensagem = criarMensagem("Aluno Não Encontrado", "info")
            
            return mensagem
    else:
        return recarregarTabela(request)
    
def buscarRM(request,rm):
    rm = request.POST.get('rm')
    print("RM", rm)
    aluno = Aluno.objects.get(pk=rm)
    dados = f'<div class="col-12"> <p class="text-white bg-dark" > RM: <span id="registroAluno">{aluno.rm} </span> </p> <p class="text-white bg-dark"> Nome: {aluno.nome} </p>  </div>'
    return HttpResponse(dados)
       
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
    rodarTeste()
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
    stylesheet = getSampleStyleSheet()
    normalStyle = stylesheet['BodyText']
    
    for i in range(len(alunos)):
        if alunos[i].cancelado:
            data_alunos.append([Paragraph(f'<para align=center><strike>{alunos[i].rm}</strike></para>',normalStyle), Paragraph(f'<strike>{alunos[i].nome}</strike>')])
        else:
            data_alunos.append([Paragraph(f'<para align=center>{alunos[i].rm}</para>',normalStyle), Paragraph(f'{alunos[i].nome}')])
        
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
    
  
    t_aluno = Table(data_alunos, style= style_table ,hAlign='LEFT', repeatRows=1, colWidths=[60,450])
    
    
    elements.append(t_aluno)
    
    doc.build(elements)
    nome_arquivo = str(rmi) + '_' + str(rmf) + datetime.strftime(datetime.now(),'_%d/%m/%Y_%H_%M_%S')
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename={nome_arquivo}.pdf'
    response.write(buffer.getvalue())
    buffer.close()

    return response
