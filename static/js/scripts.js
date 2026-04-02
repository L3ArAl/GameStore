// ================================================
// GameStore — scripts.js
// JavaScript: confirmação de exclusão e extras
// ================================================

// Confirmação de exclusão em todos os botões .btn-excluir
document.addEventListener('DOMContentLoaded', function () {

    // ── Confirmação ao excluir ──────────────────
    const botoesExcluir = document.querySelectorAll('.btn-excluir');
    botoesExcluir.forEach(function (btn) {
        btn.addEventListener('click', function () {
            const confirmado = confirm('⚠️ Tem certeza que deseja excluir este registro?\nEsta ação não pode ser desfeita.');
            if (!confirmado) {
                return false;
            }
            // Aqui iria a lógica de exclusão real (rota DELETE/POST)
        });
    });

    // ── Fechar alertas automaticamente após 4s ──
    const alertas = document.querySelectorAll('.alert');
    alertas.forEach(function (alerta) {
        setTimeout(function () {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alerta);
            if (bsAlert) bsAlert.close();
        }, 4000);
    });

});
