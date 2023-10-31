
botaoContraste = document.getElementById("contraste");
botaoContraste.addEventListener("click", verificarContraste);

function verificarContraste() {
  //conteudo = document.getElementById("Conteudo");
  /*var btnContraste = document.getElementById("contraste");
  
  if (btnContraste.value == 0){
    btnContraste.setAttribute("value","1");
  }
  else {
    btnContraste.setAttribute("value","0");
  }*/
  
  let conteudo = document.getElementById("corpo");
  let tabela = document.getElementById("tabela");
  let acessibilidade = document.getElementById("acessibilidade");
  let iconeLuz = document.getElementById("iconeContraste");
  let modal = document.getElementsByClassName("modal-content");
  let btnGravar = document.getElementById("gravar");
  let btnRelatorio = document.getElementById("relatorio");
  let btnBkp = document.getElementById("bkp");
  let infoAluno = document.getElementById("aluno");

  infoAluno.classList.toggle("bg-body-secondary");
  btnGravar.classList.toggle("btn-outline-dark");
  btnGravar.classList.toggle("btn-outline-warning");
  btnRelatorio.classList.toggle("btn-outline-dark");
  btnRelatorio.classList.toggle("btn-outline-warning");
  btnBkp.classList.toggle("btn-outline-primary");
  btnBkp.classList.toggle("btn-outline-success");
  

  iconeLuz.classList.toggle("bi-lightbulb");
  acessibilidade.classList.toggle("bg-warning");
  iconeLuz.classList.toggle('bi-lightbulb-fill');
  conteudo.classList.toggle('bg-dark');
  document.body.classList.toggle('text-white');
  tabela.classList.toggle('table-success');
  tabela.classList.toggle('table-dark');

  for(let i=0; i < modal.length; i++) {
    modal[i].classList.toggle('bg-dark');
  }

  
}
