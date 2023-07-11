from django.urls import path
from .views import index, gravar, buscar, recarregarTabela, atualizar

urlpatterns = [
    path("", index, name="inicial" ),  
    path("gravar", gravar, name="gravar"),
    path("buscar/<str:nome>", buscar, name ="buscar"),
    path("recarregarTabela", recarregarTabela, name ="recarregarTabela"),
    path("atualizar/<str:rm>", atualizar, name="atualizar")
]