from django.urls import path
from .views import index, gravar, buscar, recarregarTabela, atualizar, baixar_pdf, cancelarRM, buscarRM

urlpatterns = [
    path("", index, name="inicial" ),  
    path("gravar", gravar, name="gravar"),
    path("buscar/<str:nome>", buscar, name ="buscar"),
    path("buscarRM/<str:rm>", buscarRM, name ="buscarRM"), # em desenvolvimento
    path("recarregarTabela", recarregarTabela, name ="recarregarTabela"),
    path("atualizar/<str:rm>", atualizar, name="atualizar"),
    path("cancelarRM/<str:rm>", cancelarRM, name="cancelarRM"), # em desenvolvimento
    path("baixarpdf", baixar_pdf, name="baixarpdf"),
]