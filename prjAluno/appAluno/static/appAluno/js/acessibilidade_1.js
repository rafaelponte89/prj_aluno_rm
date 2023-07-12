
// a criação de cookies possibilita armazenar configurações do site no navegador
function configuracoes(){
    document.getElementById("Conteudo").style.fontSize = atribuirTamanhoFonte("tamanhoLetra") + "%";
 }

// simplificação do código através das Web APIS do javascript
// localStorage.setItem("chave","valor") e localStorage.getItem("chave")
function atribuirTamanhoFonte(nome) {
    if (localStorage.getItem(nome) === "NaN")
    {
          localStorage.setItem(nome,"100");
    }
   return localStorage.getItem(nome);
}

function processarTamanhoLetra(limiteFonte, operacao)
{
        let font = atribuirTamanhoFonte("tamanhoLetra");

        if (font === limiteFonte){}
        else {

            if (operacao == "+"){
                font = (parseInt(font) + 10);
            }
            else {
                font = (parseInt(font) - 10);
            }
            document.getElementById("Conteudo").style.fontSize =  font + "%";
        }

        localStorage.setItem("tamanhoLetra",font);

}

function aumentarLetra(){
    processarTamanhoLetra("150","+")
}

function diminuirLetra(){
    processarTamanhoLetra("80","-")
}
