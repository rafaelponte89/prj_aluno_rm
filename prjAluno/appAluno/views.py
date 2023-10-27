from django.shortcuts import render, redirect
from .models import Aluno, Telefone
from .forms import frmAluno
from django.contrib import messages
from django.http import HttpResponse
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt

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
from .automatization import login_sed_2, acessar_caminho, buscar_dados

from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

gauth = GoogleAuth()
#gauth.CommandLineAuth()
gauth.LocalWebserverAuth()
drive = GoogleDrive(gauth)

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
    
# Migrar Serie,Turma,Ano EM DESENVOLVIMENTO
def migrar_dados_aluno_serie():
    alunos = Aluno.objects.filter(rm__gte=3520)
    j = 0
    acumulador = 0
    ls_arquivo_csv = []
    print(len(alunos))
    with open("serie_turma.csv", "r", encoding="utf-8") as arquivo:
        arquivo_csv = csv.reader(arquivo, delimiter=",")
        for i, linha in enumerate(arquivo_csv):  
            ls_arquivo_csv.append(linha)           
    
    print("Arquivo CsvTamanho", len(ls_arquivo_csv))
    print("Objetos Alunos tamanho", len(alunos))
    for i in range(len(alunos)):
        while j < len(ls_arquivo_csv)-1:
            #print(ls_arquivo_csv[j][3])
            
            if ((alunos[i].ra).lstrip().rstrip() == (ls_arquivo_csv[j][3]).lstrip().rstrip()):
                alunos[i].serie = ls_arquivo_csv[j][0]
                alunos[i].turma = ls_arquivo_csv[j][1]
                if (ls_arquivo_csv[j][1] == 'A' or ls_arquivo_csv[j][1] == 'B'):
                    alunos[i].periodo='M'
                elif (ls_arquivo_csv[j][1] == 'C' or ls_arquivo_csv[j][1] == 'D' or ls_arquivo_csv[j][1] == 'E'):
                    alunos[i].periodo= 'T'
                else:
                    alunos[i].periodo= ''

                alunos[i].ano = ls_arquivo_csv[j][2]
                alunos[i].save()
                acumulador += 1
                print(alunos[i].nome, alunos[i].ra, alunos[i].serie,
                      alunos[i].turma, alunos[i].ano)
    
            j += 1
        j = 0
    print(acumulador)
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
    
# Converte data do formato dd/mm/aaaa para aaaa-mm-dd
def converter_data():
    alunos = Aluno.objects.all()
    
    try:    
        for aluno in alunos:
            if len(aluno.data_nascimento) > 0:
                data_nascimento = datetime.strptime(aluno.data_nascimento, "%d/%m/%Y").date()
                data_convertida = data_nascimento.strftime("%Y-%m-%d")
                aluno.data_nascimento = data_convertida
                aluno.save()
    except:
        pass
# Create your views here.
def criar_log(texto,mensagem):
    with open('log_backup.txt','a') as bkp_log:
        bkp_log.write((datetime.now().strftime('%d/%m/%Y - %H:%M:%S') + ' Status: ' + mensagem + ' Descricao: ' + texto + '\n'))

# backup utilizando pydrive
def realizar_backup_v2(request):
    
    #gauth.LocalWebserverAuth()
   
    #gauth.LocalWebserverAuth()
    arquivo = "db.sqlite3"
    try:
        gfile = drive.CreateFile({'parents': [{'id': '1TeRTAGnqX8gkBvFDQovVGtZrvm8GhK0s'}]})
        gfile.SetContentFile(f"bd/{arquivo}")
        gfile.Upload()
    
        return criarMensagem(f"Backup Efetuado na Nuvem!!! Arquivo: {arquivo}", "info")
    except(Exception):
        return criarMensagem(f"Falha no Backup!!!", "danger")

    
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
            status_rm = '<td class="align-middle">' + str(aluno.rm) + '</td>'
            
            botao = '<button type="button" class="btn btn-outline-danger btn-lg  disabled" aria-label="cancelar'+str(aluno.nome)+  '" value="'+str(aluno.rm)+'"> \
                            <i class="bi bi-x-circle-fill"></i> \
                        </button>' 
        else:
            if nome in nomes_duplicados:
                status_rm = '<td class="align-middle">' + str(aluno.rm) + \
                '<button "type="button" class="btn btn-outline-primary m-2 advertencia" value='+str(aluno.rm)+' data-bs-toggle="modal" data-bs-target="#resolucaoDuplicidadeModal" ><i class="bi bi-person-fill-exclamation"></i></button></a></td>'
                botao = '<button type="button" class="btn btn-outline-dark btn-lg atualizar"  value='+str(aluno.rm)+' data-bs-toggle="modal" data-bs-target="#atualizarModal"> \
                            <i class="bi bi-arrow-repeat"></i> \
                        </button>'
            else:
                status_rm = '<td class="align-middle">' + str(aluno.rm) + '</td>'
                botao = '<button type="button" class="btn btn-outline-dark btn-lg atualizar" aria-label="atualizar'+str(aluno.nome)+'"  value="'+str(aluno.rm)+'" data-bs-toggle="modal" data-bs-target="#atualizarModal"> \
                            <i class="bi bi-arrow-repeat"></i> \
                        </button>'
                
                             
            
        tabela += f"""<tr> {status_rm}
                    <td class="align-middle">{aluno.nome}</td> 
                        <td class="align-middle text-center">{aluno.serie} </td>
                        <td class="align-middle text-center">{aluno.turma} </td>
                        <td class="align-middle text-center">{aluno.ano} </td>
                        <td class="align-middle text-center">{aluno.ra} </td> 
                        <td class="align-middle text-center conteudoAtualizar">
                            {botao} 
                        </td>
                    </tr>"""    
                    
                    
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

# reset na tabela 
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

def buscar_dados_aluno(request):
    rm = request.POST.get('rm')
    print("RM", rm)
    aluno = Aluno.objects.get(pk=rm)
    telefone = Telefone()
  
    periodos = Aluno.retornarPeriodos()
    telefones = Telefone.retornarListaTelefones()
    telefones_aluno = Telefone.objects.filter(aluno=aluno)
    selecionado = "" 
   
    opcoes_periodo = f"<option {selecionado}> Selecione </option>"
   
    print("Telefones",telefones_aluno)
    for i in range(len(periodos)):
        sigla, periodo = periodos[i]
        if aluno.periodo == sigla:
            selecionado = "selected"
            opcoes_periodo += f"""<option value={sigla} {selecionado}>{periodo}</option>"""
        else:
            selecionado = ""
            opcoes_periodo += f"""<option value='{sigla}' {selecionado}>{periodo}</option>"""
    
    def retornar_telefone( telefones_aluno):  
        selecionado_tel = ""     
        opcoes_telefone = f"<option {selecionado}> Selecione </option>"
        for i in range(len(telefones)):
            sigla, contato = telefones[i]
            if telefones_aluno.contato == sigla:
                selecionado_tel = "selected"
                opcoes_telefone += f"""<option value={sigla} {selecionado_tel}>{contato}</option>"""
            else:
                selecionado_tel = ""
                opcoes_telefone += f"""<option value='{sigla}' {selecionado_tel}>{contato}</option>"""
        return opcoes_telefone
    
    dados_telefone = "" 
    for i in range(len(telefones_aluno)):  
        dados_telefone += f"""
                   <div class="col-12 form-group d-flex align-items-center"> 
                  <input        
                    type="text"     
                    class="form-control numTelefone p-2" 
                    id="telefoneAtualizar" 
                    aria-describedby="emailHelp" 
                    placeholder="Telefone" 
                    value="{telefones_aluno[i].numero}"
                  /> 
                      <select class="form-select m-3 contato" aria-label="Default select example" id=periodoAtualizar> 
                        {retornar_telefone(telefones_aluno[i])}
                    </select> 
                   <button type="button" class="btn btn-danger m-1 removerTelefone" value="{telefones_aluno[i].id}">X</button> 
                </div>"""
        
    dados = f"""<form id="cadastroAluno"> 
            <div class="form-group">
              <label for="nomeAtualizar">Nome</label>
              <input
                type="text"
                class="form-control"
                id="nomeAtualizar"
                aria-describedby="emailHelp"
                placeholder="Nome"
                value = "{aluno.nome}"
              />
            </div>
            <div class="row">
              <div class="col form-group">
                <label for="raAtualizar">Registro do Aluno (SED)</label>
                <input
                  type="number"
                  class="form-control"
                  id="raAtualizar"
                  aria-describedby="emailHelp"
                  placeholder="RA"
                  value = "{aluno.ra}"
                />
              </div>
              <div class="col-3 form-group">
                <label for="raDigitoAtualizar">Digito RA (SED)</label>
                <input
                  type="text"
                  class="form-control"
                  id="raDigitoAtualizar"
                  aria-describedby="emailHelp"
                  placeholder="RA Digito"
                  maxlength = "1"
                  value = "{aluno.d_ra}"
                />
              </div>
            </div>
            <div class="form-group">
              <label for="nascimentoAtualizar">Data de Nascimento:</label>
              <input
                type="date"
                class="form-control"
                id="nascimentoAtualizar"
                aria-describedby="emailHelp"
                placeholder="Data de Nascimento"
                value = "{aluno.data_nascimento}"
              />
            </div>
            <div class="row">
              <div class="col-2 form-group">
                <label for="serieAtualizar">Série</label>
                <input
                  type="number"
                  class="form-control"
                  id="serieAtualizar"
                  aria-describedby="emailHelp"
                  value ="{aluno.serie}"
                />
              </div>
              <div class="col-2 form-group">
                <label for="turmaAtualizar">Turma</label>
                <input
                  type="text"
                  class="form-control"
                  id="turmaAtualizar"
                  aria-describedby="emailHelp"
                  maxlength="1"
                  value="{aluno.turma}"
                />
              </div>
              <div class="col form-group">
                <label for="periodoAtualizar">Periodo</label>
                    <select class="form-select" aria-label="Default select example" id=periodoAtualizar>
                        {opcoes_periodo}
                    </select>
              </div> 
              <div class="col form-group">
                <label for="anoAtualizar">Ano</label>
                <input
                  type="number"
                  class="form-control"
                  id="anoAtualizar"
                  aria-describedby="emailHelp"
                  placeholder="Ano"
                  value="{aluno.ano}"
                />
              </div>
            </div>
             <div class="row">
               <div class="col-1 form-group d-flex">
                  <button id="addTelefone" type="button" class="btn btn-primary mt-3">+</button>
                </div>
            </div>
            <div class="row mb-2" id="telefones">
                   {dados_telefone}
            </div>
             
               <div class="modal-footer">
        <button type="button" class="btn btn-danger" data-bs-dismiss="modal">
          Cancelar
        </button>
         <button
              id="simAtualizar"
              type="button"
              class="btn btn-primary"
              data-bs-dismiss="modal"
              value={aluno.rm}
            >
              Atualizar
            </button>
      </div>
           
          """ 
    return HttpResponse(dados)  

def buscarRMCancelar(request):
    rm = request.POST.get('rm')
    print("RM", rm)
    aluno = Aluno.objects.get(pk=rm)
    dados = f'<div class="col-12"> <p class="text-white bg-dark" > RM: <span id="registroAluno">{aluno.rm} </span> </p> <p class="text-white bg-dark"> Nome: {aluno.nome} </p>  </div>'
    return HttpResponse(dados)

def del_telefone(request):
    id_tel = request.POST.get('id_tel')
    telefone = Telefone.objects.get(pk=id_tel)
    telefone.delete()
    
    return HttpResponse("Telefone Excluido")
    
# busca aluno por rm
@csrf_exempt
def buscarRM(request):
    rm = request.POST.get('rm')
    print("RM", rm)
    aluno = Aluno.objects.get(pk=rm)
   
    dados = f'<div class="col-sm-6 p-3"> \
           <div class="input-group"> \
      <div class="input-group-prepend"> \
        <span class="input-group-text bg-dark text-white" id="basic-addon1"><i class="bi bi-search"></i></span>\
      </div> \
            <input type="text" name="nome" maxlength="100" class="form-control formulario" placeholder="Nome do Aluno" aria-describedby="basic-addon1" required="" id="id_nome" value="{aluno.nome}"> \
            </div> \
            </div> \
            <div class="col-sm-2 p-3"> \
            <input type="number" name="ra" maxlength="20" class="form-control formulario" placeholder="RA" required="" id="id_ra" value="{aluno.ra}"> \
        </div> \
            <div class="col-sm-4 d-flex justify-content-center"> \
    <button id="gravar" class="btn btn-outline-dark m-3" title="Registrar Aluno" style={"display:none"}> \
      Gravar \
    </button> \
    <button \
      id="atualizar2" \
      class="btn btn-outline-primary m-3"\
      title="Atualizar Aluno" \
      value="{aluno.rm}" \
    > \
      Atualizar\
    </button>\
    \
    <button\
      id="relatorio"\
      class="btn btn-outline-dark m-3"\
      title="Gerar Relatório"\
      data-bs-toggle="modal"\
      data-bs-target="#relatorioModal"\
    >\
      Relatório\
    </button>\
    <button\
      id="bkp"\
      class="btn btn-outline-primary m-3"\
      title="Enviar Cópia para a Nuvem"\
    >\
      <i class="bi bi-cloud-arrow-up-fill"></i>\
    </button>\
  </div>'
        
    return HttpResponse(dados)
       
def atualizar(request):
    nome = padronizar_nome(request.POST.get("nome").lstrip().rstrip())
    ra = request.POST.get("ra")
    dra = request.POST.get("dra").upper()
    dt_nascimento = request.POST.get("dt_nascimento")
    serie = request.POST.get("serie")
    turma = request.POST.get("turma")
    periodo = request.POST.get("periodo")
    ano = request.POST.get("ano")
    telefones = request.POST.getlist("telefones[]")
    contatos = request.POST.getlist("contatos[]")
    novos_tel = request.POST.getlist("novos_tel[]")
    print("Telefones", telefones)
    print("Contatos", contatos)
    
    tamanho_ra = len(ra)

    rm = int(request.POST.get("rm"))
    print(nome, ra, rm)
    tamanho_nome = len(nome)
    if rm != '':
        if (tamanho_nome > REF_TAMANHO_NOME):
            #rm = int(request.POST.get("rm"))
            #print(rm)
            aluno = Aluno.objects.get(pk=rm)            
            aluno.nome = nome
            aluno.d_ra = dra
            aluno.data_nascimento = dt_nascimento
            aluno.serie = serie
            aluno.turma = turma
            aluno.periodo = periodo
            aluno.ano = ano
            
            # em desenvolvimento
           
            print("Novos Tel", novos_tel)
            
            for i in range(len(telefones)):
                if len(novos_tel) > 0:
                    telefone = Telefone()
                    if novos_tel[i] == "0":
                        
                        telefone.numero = telefones[i]
                        telefone.contato = contatos[i]
                        telefone.aluno = aluno
                        
                       
                    else:
                        telefone = Telefone.objects.get(pk=int(novos_tel[i]))
                        telefone.numero = telefones[i]
                        telefone.contato = contatos[i]
                    telefone.save()
                
                
            ######
            if tamanho_ra > REF_TAMANHO_RA:
                aluno.ra = ra

            aluno.save()
            mensagem = criarMensagem(f"Registro de Aluno Atualizado com Sucesso!!! RM: {rm} - Nome (Atualizado): {nome}","success")
        else:
            if tamanho_ra > REF_TAMANHO_RA:
                aluno.ra = ra
            elif (tamanho_nome == 0):
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
    #migrar_dados_aluno_serie()  
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
   
    context = {
            'form': frmAluno(),
        }

    return render(request, 'index.html', context)

def baixar_pdf(request):
   
    rmi = int(request.POST.get("rmi"))
    rmf = int(request.POST.get("rmf"))
    maior = ''
    if rmi > rmf:
        maior = rmi
        rmi = rmf
        rmf = maior
    
    alunos = gerarIntervalo(rmi, rmf)
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
    
    t_aluno = Table(data_alunos, style=style_table, hAlign='LEFT', repeatRows=1, colWidths=[60, 450])
    
    elements.append(t_aluno)
    
    doc.build(elements)
    nome_arquivo = str(rmi) + '_' + str(rmf) + datetime.strftime(datetime.now(),'_%d/%m/%Y_%H_%M_%S')
    response = HttpResponse(content_type='application/pdf')
    
    response['Content-Disposition'] = (
        f'attachment; filename={nome_arquivo}.pdf')
    
    response.write(buffer.getvalue())
    buffer.close()
    
    return response
