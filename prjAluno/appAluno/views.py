from django.shortcuts import render, redirect
from .models import Aluno
from .forms import frmAluno
from django.contrib import messages
from django.http import HttpResponse
from django.db.models import Q
# Create your views here.

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
 
    context = {
            'alunos': Aluno.retornarNUltimos(),
            'form': frmAluno()
        }
    return render(request,'index.html', context)



def pdf_v3(request):
    import io
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Image
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    contexto = buscar_informacoes_ficha_v2(pessoa_id,ano)
   
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(A4), rightMargin=30,leftMargin=30, topMargin=30,bottomMargin=18)
   
    elements = []

    # cria informações para a primeira linha da tabela
    mes_dias = ["Mês/Dia"]
    for i in range(1,32):
        mes_dias.append(i)
    # mes_dias.append('Tempos')

    # insere a chave dentro da lista dos meses na posição 0. Ex ['janeiro','C','C'...]
    for k,v in contexto['meses'].items():
        v.insert(0,k)

    # insere no dicionario faltas na posição 0 a sigla da falta Ex 'contexto['FJ']'=['FJ','FALTA JUSTIFICADA',10]
    for k,v in contexto['tp_faltas'].items():
        v.insert(0,k)

    # cria lista com os valores não a chave
    data_tp_falta = [tp for tp in contexto['tp_faltas'].values()]
    
    # cria lista com os valores dos meses 
    data_frequencia = [m for m in contexto['meses'].values()]

    # dentro dessa lista insere a lista mes_dias
    data_frequencia.insert(0, mes_dias)

    faltas_mes_a_mes = contexto['falta_por_mes']
    linha = 0
    eventos_por_mes = []
    intermediaria = []
    
    for k in faltas_mes_a_mes:
        linha +=1
        if k in ['janeiro','marco','maio','julho','agosto','outubro','dezembro']:
            eventos_por_mes.append(list(faltas_mes_a_mes[k].values()))
        elif k in ['abril','junho','setembro','novembro']:
            intermediaria = list(faltas_mes_a_mes[k].values())
            eventos_por_mes.append(intermediaria)
        else:
            intermediaria = list(faltas_mes_a_mes[k].values())
            eventos_por_mes.append(intermediaria)

    # pega chaves de um mes qualquer que será a linha de eventos
    eventos_por_mes.insert(0,list(contexto['falta_por_mes']['janeiro'].keys()))
    
    # extend a tabela frequencia com informação dos eventos
    for i in range(0,len(data_frequencia)):
        data_frequencia[i].extend(eventos_por_mes[i])
    
    linha = []
    linha2 = []
    brancos = 0
    brancos = len(contexto['tp_faltas'])
    brancos += 33
    for i in range(brancos):
        linha.append(' ')
    data_frequencia.insert(1,linha)

    for i in range(brancos):
        linha2.append(' ')
    data_frequencia.insert(0,linha2)

    data_frequencia[0].extend(['Tempos'])
    data_frequencia[1].extend(['Função','Cargo','Unidade'])
    data_frequencia[2].extend([contexto['funcao_a'],contexto['cargo_a'],contexto['ue_a']])
    
    funcao_anual = []
    cargo_anual = []
    ue_anual = []
    for v in contexto['cargo'].values():
        cargo_anual.append(v)
    for v in contexto['funcao'].values():
        funcao_anual.append(v)
    for v in contexto['ue'].values():
        ue_anual.append(v)

    # data_frequencia.extend(cargo)
    print(cargo_anual,funcao_anual,ue_anual)
    inicio_linha = 3
    for i in range(12):
        data_frequencia[inicio_linha].extend([funcao_anual[i],cargo_anual[i],ue_anual[i]])
        inicio_linha += 1
    # print("Cargo",contexto['cargo'],"Funcao",contexto['funcao'],'UE',contexto['ue'])
   
    # data_frequencia[5].extend(['Atribuição'])
    # data_frequencia[6].extend([contexto['cargo_at'], contexto['funcao_at'], contexto['ue_at']])
    # data_frequencia[7].extend(['Anterior'])
    # data_frequencia[8].extend([contexto['cargo_a'], contexto['funcao_a'], contexto['ue_a']])
    # data_frequencia[9].extend(['Atual'])
    # data_frequencia[10].extend([contexto['cargo'], contexto['funcao'], contexto['ue']])

   
    tamanho_fonte = 12
    qtd_eventos = len(contexto['tp_faltas'])
    if  qtd_eventos > 3 :
        if qtd_eventos > 6 and qtd_eventos <= 9:
            tamanho_fonte = tamanho_fonte / qtd_eventos  * 5
        else:
            tamanho_fonte = tamanho_fonte / qtd_eventos  * 3.3

   
    print(tamanho_fonte)

    # cria estilo 
    style_table_corpo = TableStyle([('GRID',(0,0),(-1,-1), 0.5, colors.black),
                            ('LEFTPADDING',(0,0),(-1,-1),2),
                            ('TOPPADDING',(0,0),(-1,-1),2),
                            ('BOTTOMPADDING',(0,0),(-1,-1),2),
                            ('RIGHTPADDING',(0,0),(-1,-1),2),
                            ('ALIGN',(0,0),(-1,-1),'CENTER'),
                            ('FONTSIZE',(0,0), (-1,-1),tamanho_fonte), 
                            # ('SPAN',(-3,-13),(-1,-12)),
                            # ('SPAN',(-3,-8),(-1,-8)),
                            # ('SPAN',(-3,-6),(-1,-6)),
                            # ('SPAN',(-3,-4),(-1,-4)),
                            # ('BOX',(-3,-13),(-1,-1),2,colors.black),
                            # ('BOX',(32,0),(-1,-1),2,colors.black),
                            # ('BACKGROUND',(32,0),(-4,-1),colors.antiquewhite),
                            # ('BOX',(0,0),(32,13),2,colors.black)             
                            ], spaceBefore=20)

    # cria tabela com as informações de data_faltas
    t_frequencia = Table(data_frequencia, hAlign='CENTER',)

    
    # aplica estilo diferente conforme a condição, ou seja, as faltas ficam com cor de background
    for row, values in enumerate(data_frequencia):
       for column, value in enumerate(values):
        #    print(column, value)
           if value in contexto['tp_faltas']:
               style_table_corpo.add('BACKGROUND',(column,row),(column,row),colors.lightblue)

    t_frequencia.setStyle(style_table_corpo)

    t_tipos = Table(data_tp_falta, style=[('GRID',(0,0),(-1,-1), 0.5, colors.black),
                            ('ALIGN',(0,0),(-1,-1),'CENTER'),
                            ('FONTSIZE',(0,0), (-1,-1),7.5),
                            ('LEFTPADDING',(0,0),(-1,-1),1),
                            ('TOPPADDING',(0,0),(-1,-1),1),
                            ('BOTTOMPADDING',(0,0),(-1,-1),1),
                            ('RIGHTPADDING',(0,0),(-1,-1),1),
                            ], hAlign='LEFT')

    styles = getSampleStyleSheet()
    
    styleH = ParagraphStyle('Cabeçalho',
                            fontSize=20,
                            parent=styles['Heading1'],
                            alignment=1,
                            spaceAfter=14)
    
    styleB = ParagraphStyle('Corpo',
                        spaceAfter=14
                    ) 
    styleAss = ParagraphStyle('Assinatura',
                        alignment=1,
            
                    ) 

    styleAssTrac =  ParagraphStyle('AssinaturaTrac',
                        alignment=1,
                        spaceBefore=20
            
                    ) 

    stylePessoa = ParagraphStyle('Pessoa',
                        # alignment=0,
                        spaceAfter=4
                        
                    ) 
   
    # elements.append(Paragraph('<para><img src="https://www.orlandia.sp.gov.br/novo/wp-content/uploads/2017/01/brasaoorlandia.png" width="40" height="40"/> </para>'))
    elements.append(Paragraph(f"<strong>Ficha Frequência - Ano</strong>:{contexto['ano']}", styleH))
    # elements.append(Paragraph(f"<strong>Nome</strong>: {contexto['pessoa'].nome}  RM: {contexto['pessoa'].id}", styleB))
    
  
    
    saida = '' if contexto['pessoa'].saida == None else  contexto['pessoa'].saida.strftime('%d/%m/%Y')

    data_pessoa = [
        [Paragraph(f"<strong>Nome: </strong>{contexto['pessoa'].nome}",stylePessoa),Paragraph(f"<strong>Matrícula: </strong>{contexto['pessoa'].id}", stylePessoa),
        Paragraph(f"<strong>Cargo: </strong>{contexto['des_cargo']}", stylePessoa), Paragraph(f"<strong>Disciplina: </strong>{contexto['disciplina']}", stylePessoa)],
        [Paragraph(f"<strong>CPF: </strong>{contexto['pessoa'].cpf}", stylePessoa),Paragraph(f"<strong>Data de Admissão: </strong>{contexto['pessoa'].admissao.strftime('%d/%m/%Y')}", stylePessoa),
        Paragraph(f"<strong>Data de Saída: </strong>{saida}", stylePessoa),
        Paragraph(f"<strong>Efetivo: </strong>{contexto['pessoa'].efetivo}", stylePessoa)]
    ]

    tb_pessoa = Table(data_pessoa,style=([('GRID',(0,0),(-1,-1), 0.5, colors.white),
                            ('LEFTPADDING',(0,0),(-1,-1),2),
                            ('TOPPADDING',(0,0),(-1,-1),2),
                            ('BOTTOMPADDING',(0,0),(-1,-1),2),
                            ('RIGHTPADDING',(0,0),(-1,-1),0),
                            ('ALIGN',(0,0),(-1,-1),'CENTER'),
                            ]), hAlign='CENTER')

    #Send the data and build the file
    elements.append(tb_pessoa)
    elements.append(t_frequencia)

    elements.append(Paragraph(f"", styleB))
    
    elements.append(Paragraph('____________________________', styleAssTrac))
    elements.append(Paragraph('Nome', styleAss))
    elements.append(Paragraph('RG:11.111.111',styleAss))
    elements.append(Paragraph('Diretora',styleAss))
    
    elements.append(t_tipos)
    doc.build(elements)
    nome_arquivo = str(contexto["pessoa"].nome).replace(' ','_') + datetime.strftime(datetime.now(),'_%d/%m/%Y_%H_%M_%S')
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename={nome_arquivo}.pdf'
    response.write(buffer.getvalue())
    buffer.close()

    return response