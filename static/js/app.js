// Confirmação genérica para formulários destrutivos (data-confirm="mensagem").
(function () {
  document.querySelectorAll("form[data-confirm]").forEach(function (form) {
    form.addEventListener("submit", function (e) {
      if (!window.confirm(form.getAttribute("data-confirm"))) e.preventDefault();
    });
  });
})();

// Tour "Comece por aqui": aparece até o usuário clicar em "Entendi" (lembrado no navegador).
(function () {
  document.querySelectorAll("[data-tour]").forEach(function (card) {
    var chave = "tour-" + card.getAttribute("data-tour");
    try { if (window.localStorage.getItem(chave)) return; } catch (e) { /* armazenamento indisponível: mostra sempre */ }
    card.hidden = false;
    var botao = card.querySelector("[data-tour-fechar]");
    if (botao) botao.addEventListener("click", function () {
      try { window.localStorage.setItem(chave, "1"); } catch (e) { /* ignora */ }
      card.hidden = true;
    });
  });
})();
