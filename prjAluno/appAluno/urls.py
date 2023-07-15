from django.urls import path
from .views import index, gravar, buscar, recarregarTabela, atualizar, baixar_pdf

urlpatterns = [
    path("", index, name="inicial" ),  
    path("gravar", gravar, name="gravar"),
    path("buscar/<str:nome>", buscar, name ="buscar"),
    path("recarregarTabela", recarregarTabela, name ="recarregarTabela"),
    path("atualizar/<str:rm>", atualizar, name="atualizar"),
    path("baixarpdf", baixar_pdf, name="baixarpdf"),
]