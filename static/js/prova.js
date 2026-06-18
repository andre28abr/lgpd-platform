// Barra de progresso + cronômetro + confirmação ao enviar incompleta.
(function () {
  var form = document.querySelector("form[data-prova]");
  if (!form) return;

  var total = parseInt(form.getAttribute("data-total"), 10) || 0;
  var barra = document.getElementById("prova-progresso");
  var rotulo = document.getElementById("prova-contagem");

  function respondidas() {
    var nomes = {};
    form.querySelectorAll('input[type="radio"]:checked').forEach(function (r) {
      nomes[r.name] = true;
    });
    return Object.keys(nomes).length;
  }

  function atualizar() {
    var n = respondidas();
    if (barra) barra.style.width = total ? (n / total * 100) + "%" : "0";
    if (rotulo) rotulo.textContent = n + " de " + total + " respondidas";
  }

  form.addEventListener("change", atualizar);
  form.addEventListener("submit", function (e) {
    if (respondidas() < total) {
      if (!window.confirm("Há questões sem resposta. Deseja enviar mesmo assim?")) {
        e.preventDefault();
      }
    }
  });
  atualizar();

  // Cronômetro: form.submit() (programático) não dispara o listener acima,
  // então o envio automático no tempo esgotado não pede confirmação.
  var seg = form.getAttribute("data-segundos");
  if (seg !== null) {
    var restante = parseInt(seg, 10);
    var elTimer = document.getElementById("prova-timer");
    var mostrar = function () {
      var m = Math.floor(restante / 60), s = restante % 60;
      if (elTimer) elTimer.textContent = (m < 10 ? "0" : "") + m + ":" + (s < 10 ? "0" : "") + s;
    };
    mostrar();
    var tick = setInterval(function () {
      restante -= 1;
      if (restante <= 0) { clearInterval(tick); form.submit(); return; }
      mostrar();
    }, 1000);
  }
})();
