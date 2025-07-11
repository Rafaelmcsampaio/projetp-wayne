// projetp-wayne/static/js/confirm_actions.js

function confirmAction(message) {
    // Esta função recebe a mensagem de confirmação e exibe o diálogo
    return confirm(message);
}


// Se houver outros scripts específicos para a página de usuários, podem ser adicionados aqui
// Exemplo (se houvesse um clique em botão sem formulário):
/*
document.addEventListener('DOMContentLoaded', function() {
    const deleteButtons = document.querySelectorAll('.delete-button'); // Exemplo de seletor
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(event) {
            const message = this.dataset.confirmMessage || 'Tem certeza?';
            if (!confirmAction(message)) {
                event.preventDefault(); // Impede a ação padrão se o usuário cancelar
            }
        });
    });
});
*/