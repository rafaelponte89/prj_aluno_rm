from django.shortcuts import render, redirect
from .models import Aluno
from .forms import frmAluno
from django.contrib import messages
from django.http import HttpResponse
from django.db.models import Q

import time
import io
from pathlib import Path
from os import path
import os.path
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from datetime import datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import HttpError
from googleapiclient.http import MediaFileUpload
import os
from datetime import datetime
import csv


REF_TAMANHO_NOME = 2
REF_TAMANHO_RA = 7

# Códigos para testar a aplicação e/ou em desenvolvimento
def rodarTeste():
    j = 0
    for i in range(4999):
        aluno = Aluno(j,"NOME "+ str(i) + "SOBRENOME1 "+ str(i) + "SOBRENOME2"+ str(i))
        j += 1
        aluno.save()
        
def testePadronizaNome():
    alunos = Aluno.objects.all()
    
    padronizar_nomes(alunos)

# Migração para base de dados
def migrar_dados_aluno():
    alunos = Aluno.objects.filter(rm__gte=3520)
    j = 0
    acumulador = 0
    nomes_migrados = []
    nao_migrados = []
    nao_migrados_count = 0
    ls_arquivo_csv = []
    print(len(alunos))
    with open("alunos.csv","r",encoding="utf-8") as arquivo:
        arquivo_csv = csv.reader(arquivo, delimiter=",")
        for i, linha in enumerate(arquivo_csv):  
            ls_arquivo_csv.append(linha)           
    
    print("Arquivo CsvTamanho",len(ls_arquivo_csv))
    print("Objetos Alunos tamanho", len(alunos))
    for i in range(len(alunos)):
        while j < len(ls_arquivo_csv)-1:
            nome_aluno = padronizar_nome(alunos[i].nome)
            nome_aluno_csv = padronizar_nome(ls_arquivo_csv[j][0])
            if nome_aluno == nome_aluno_csv and nome_aluno not in nomes_migrados:
                    alunos[i].ra = ls_arquivo_csv[j][1]
                    alunos[i].d_ra = ls_arquivo_csv[j][2]
                    alunos[i].data_nascimento = ls_arquivo_csv[j][3]
                    alunos[i].save()
                    nomes_migrados.append(nome_aluno)
                    acumulador += 1
                    print(nome_aluno == nome_aluno)
                    print(acumulador)
            j += 1
        j = 0
        
    for i in range(len(alunos)):
        nome_aluno = padronizar_nome(alunos[i].nome)
        for j in range(len(nomes_migrados)):
            if nome_aluno not in nomes_migrados and nome_aluno not in nao_migrados:
                nao_migrados.append(nome_aluno)
                nao_migrados_count += 1
                #print(padronizar_nome(linha[0]),"RA:", linha[1],"Digito RA",linha[2],"Data Nascimento:",linha[3] )
    with open("migracao_quantidade_alunos.txt","w") as arquivo:
        for nome in nomes_migrados:
            arquivo.write(nome + '\n')    
        arquivo.write("Total de Mudancas: " +  str(acumulador))
    with open("nao_migrados.txt","w") as arquivo:
        for nome in nao_migrados:
            arquivo.write(nome + '\n')    
        arquivo.write("Nao Migrados: " +  str(nao_migrados_count))
    
# Create your views here.

def criar_log(texto,mensagem):
    with open('log_backup.txt','a') as bkp_log:
        bkp_log.write((datetime.now().strftime('%d/%m/%Y - %H:%M:%S') + ' Status: ' + mensagem + ' Descricao: ' + texto + '\n'))




def realizar_backup(request):
    SCOPES =["https://www.googleapis.com/auth/drive"]
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json",SCOPES)
    
    
    # Observação erro na atualização do token
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
            
    with open('token.json','w') as token:
        token.write(creds.to_json())
        
    try:
        service = build("drive","v3", credentials=creds)
        
        response = service.files().list(
            q = "name='BkpRegistroAlunosVictoria' and mimeType='application/vnd.google-apps.folder'",
            spaces='drive'
        ).execute()
        
        if not response['files']:
            file_metadata = {
                "name": "BkpRegistroAlunosVictoria",
                "mimeType": "application/vnd.google-apps.folder"
            }
            
            file = service.files().create(body=file_metadata, fields="id").execute()
            
            folder_id = file.get('id')
        else:
            folder_id = response['files'][0]['id']
            
       
        for file in os.listdir('bd'):
            file_metadata = {
                "name": file,
                "parents": [folder_id]
            }

            
            media = MediaFileUpload(f"bd/{file}")
            upload_file = service.files().create(body=file_metadata, media_body=media, fields="id").execute()
            print("Upload arquivo: " + file)
            criar_log("Upload " + file,"Sucesso")
        return criarMensagem(f"Backup Efetuado na Nuvem!!! Arquivo: {file}", "info")
    except HttpError as e:
       criar_log(str(e), "Falha")
       print("Error: " + str(e))
       return criarMensagem("Falha no Backup!!!", "danger")

def padronizar_nome(nome):
    acentuados = {'Á':'A','Ã':'A','Â':'A','É':'E','Ê':'E','Í':'I','Î':'I','Ó':'O','Õ':'O','Ô':'O','Ú':'U','Û':'U','Ç':'C','\'':'','\`':''}   
    #acentuados = {'Á':'A','Ã':'A','Â':'A','É':'E','Ê':'E','Í':'I','Î':'I','Ó':'O','Õ':'O','Ô':'O','Ú':'U','Û':'U'}   

    letra_nova = ''
    for letra in nome:
        if letra in acentuados.keys():
            letra_nova = acentuados[letra]
            nome = nome.replace(letra,letra_nova)
            
    return nome.rstrip(' ').lstrip(' ')

def padronizar_nomes(alunos):
    acentuados = {'Á':'A','Ã':'A','Â':'A','É':'E','Ê':'E','Í':'I','Î':'I','Ó':'O','Õ':'O','Ô':'O','Ú':'U','Û':'U','Ç':'C'}   

    #acentuados = {'Á':'A','Ã':'A','Â':'A','É':'E','Ê':'E','Í':'I','Î':'I','Ó':'O','Õ':'O','Ô':'O','Ú':'U','Û':'U'}   
    letra_nova = ''
    for aluno in alunos:
        for letra in aluno.nome:
            if letra in acentuados.keys():
                letra_nova = acentuados[letra]
                aluno.nome = aluno.nome.replace(letra,letra_nova)
                print(aluno.nome)
                aluno.save()
             
def buscar_duplicados(alunos):
   
    nomes_rm = {}
    duplicados = {}
    for aluno in alunos:
        nome = aluno.nome.rstrip().lstrip().upper()
       
        if aluno.cancelado != True:
            if nome not in nomes_rm.keys():
                nomes_rm[nome] = [aluno.rm]
            else:
                nomes_rm[nome].append(aluno.rm)
   
    for k, v in nomes_rm.items():
        if len(v) > 1:
            duplicados[k] = v
            
    return duplicados.keys()
    
# Gravar registro do Aluno
def gravar(request):
    #print("gravar")
    nome = padronizar_nome(request.POST.get("nome"))
    ra = request.POST.get("ra")
    tamanho_nome = len(nome)
    tamanho_ra = len(ra)

    try:
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        if is_ajax:
            if request.method == 'POST':
                form = frmAluno({"nome":nome,"ra":ra})
                if form.is_valid():
                    if( tamanho_nome > REF_TAMANHO_NOME):
                        if(tamanho_ra > REF_TAMANHO_RA): 
                         
                            print('formulario',form["nome"])
                            form.save() 
                            #print('nome',padronizar_nome(request.POST.get("nome").lstrip(' ').rstrip('')))
      
                            mensagem = criarMensagem("Aluno Registrado com Sucesso!","success")
                        else:
                            mensagem = criarMensagem("RA muito Pequeno","warning")
                        
                    else:
                        mensagem = criarMensagem("Nome muito Pequeno!","warning")
                else:
                    if tamanho_nome == 0: 
                        mensagem = criarMensagem("Nome em Branco!!","warning")
                    elif tamanho_ra == 0: 
                        mensagem = criarMensagem("RA em Branco!!","warning")


                    
                return mensagem
                        
                        
    except Exception as err:
        print(err)
    
def atualizarTabela(alunos):
    nomes_duplicados = buscar_duplicados(alunos)
    tabela = ''
    print("Duplicados",nomes_duplicados)
    
    for aluno in alunos:
        nome = aluno.nome.rstrip().lstrip().upper()
        if aluno.cancelado:
            status_rm = '<tr><td class="align-middle">' + str(aluno.rm) + '</td>'
            
            botao = '<button type="button" class="btn btn-outline-danger btn-lg  disabled" aria-label="cancelar'+str(aluno.nome)+  '" value='+str(aluno.rm)+'> \
                            <i class="bi bi-x-circle-fill"></i> \
                        </button>' 
        else:
            if nome in nomes_duplicados:
                status_rm = '<tr><td class="align-middle">' + str(aluno.rm) + \
                '<button "type="button" class="btn btn-outline-primary m-2 advertencia" value='+str(aluno.rm)+' data-bs-toggle="modal" data-bs-target="#resolucaoDuplicidadeModal" ><i class="bi bi-person-fill-exclamation"></i></button></a></td>'
                botao = '<button type="button" class="btn btn-outline-dark btn-lg atualizar disabled"  value='+str(aluno.rm)+'> \
                            <i class="bi bi-arrow-repeat"></i> \
                        </button>'
            else:
                status_rm = '<tr><td class="align-middle">' + str(aluno.rm) + '</td>'
                botao = '<button type="button" class="btn btn-outline-dark btn-lg atualizar disabled" aria-label=atualizar'+str(aluno.nome)+'  value='+str(aluno.rm)+'> \
                            <i class="bi bi-arrow-repeat"></i> \
                        </button>'
                
                             
            
        tabela += ' <tr>' + status_rm + \
                    '<td class="align-middle">'+aluno.nome+'</td> \
                        <td>' + aluno.ra+  '</td> \
                        <td class="text-center conteudoAtualizar">' \
                        +botao+ \
                    '</td> </tr>'    
                    
                    
    #print("Atualizar Tabela", tabela)
    return HttpResponse(tabela)
  
def criarMensagem(texto, tipo):
        
    mensagem = HttpResponse(f"<div style='display:block;' id='mensagem' class='alert alert-{tipo}' role='alert' >{texto} </div>")
    return  mensagem

def cancelarRM(request):
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

def buscar(request):
    nome = padronizar_nome(request.POST.get("nome").upper().rstrip().lstrip())
    tamanho = len(nome)
    print(nome)
    if (tamanho > REF_TAMANHO_NOME) :
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
    
def buscarRM(request):
    rm = request.POST.get('rm')
    print("RM", rm)
    aluno = Aluno.objects.get(pk=rm)
    dados = f'<div class="col-12"> <p class="text-white bg-dark" > RM: <span id="registroAluno">{aluno.rm} </span> </p> <p class="text-white bg-dark"> Nome: {aluno.nome} </p>  </div>'
    return HttpResponse(dados)
       
def atualizar(request):
    nome = padronizar_nome(request.POST.get("nome").lstrip().rstrip())
    ra = request.POST.get("ra")
    tamanho_ra = len(ra)

    rm = int(request.POST.get("rm"))
    
    tamanho_nome = len(nome)
    if rm != '':
        if(tamanho_nome > REF_TAMANHO_NOME):
            rm = int(request.POST.get("rm"))
            #print(rm)
            aluno = Aluno.objects.get(pk=rm)
            aluno.nome = nome
            if tamanho_ra > REF_TAMANHO_RA:
                aluno.ra = ra
           
            aluno.save()
            mensagem = criarMensagem(f"Registro de Aluno Atualizado com Sucesso!!! RM: {rm} - Nome (Atualizado): {nome}","success")
        else:
            if tamanho_ra > REF_TAMANHO_RA:
                aluno.ra = ra
            elif(tamanho_nome == 0):
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
   
   
    #login_sed()
    #acessar_caminho()
    #buscar_dados_historico(lista_ra)
    
    #aba = driver.find_element(By.XPATH,'//*[@id="aba5"]/a')
    
    #aba = driver.find_element(By.ID,'btnConsultarIrmao')

   
    #aba.click()
    #driver.execute_script("arguments[0].click(listarMatriculasFichaAluno(false));",aba)
    #print(aba)

    #driver.implicitly_wait(0.5)

    #driver.execute_script("arguments[0].click();",link_matricula)
    
    

    
    #time.sleep(10)


    #print("index",is_ajax)
    #rodarTeste()
    context = {
            'form': frmAluno(),
        }
    #testePadronizaNome()
    #migrar_dados_aluno()
   
    return render(request,'index.html', context)

def baixar_pdf(request):
   
    rmi = int(request.POST.get("rmi"))
    rmf = int(request.POST.get("rmf"))
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
            data_alunos.append([Paragraph(f'<para align=center size=12><strike>{alunos[i].rm}</strike></para>',normalStyle), Paragraph(f'<para size=12><strike>{alunos[i].nome}</strike></para>')])
        else:
            data_alunos.append([Paragraph(f'<para align=center size=12>{alunos[i].rm}</para>',normalStyle), Paragraph(f'<para size=12>{alunos[i].nome}</para>')])
        
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
