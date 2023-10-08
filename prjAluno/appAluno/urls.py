from django.urls import path
from .views import index, gravar, buscar, recarregarTabela, atualizar, baixar_pdf, cancelarRM, buscarRM, realizar_backup, buscarRMCancelar

urlpatterns = [
    path("", index, name="inicial" ),  
    path("gravar", gravar, name="gravar"),
    path("buscar", buscar, name ="buscar"),
    path("buscarRM", buscarRM, name ="buscarRM"), # em desenvolvimento
    path("buscarRMCancelar", buscarRMCancelar, name ="buscarRMCancelar"), # em desenvolvimento
    path("recarregarTabela", recarregarTabela, name ="recarregarTabela"),
    path("atualizar", atualizar, name="atualizar"),
    path("cancelarRM", cancelarRM, name="cancelarRM"), # em desenvolvimento
    path("baixarpdf", baixar_pdf, name="baixarpdf"),
    path("bkp", realizar_backup, name="realizarbackup")
]