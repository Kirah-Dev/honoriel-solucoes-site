document.addEventListener('DOMContentLoaded', () => {

    // =========================================================
    // BLOCO 1: NOVO CONTROLADOR DE MODAL GENÉRICO
    // (Substitui a lógica antiga dos especialistas)
    // =========================================================
    // Seleciona todos os botões/links que têm o atributo 'data-modal-target'
    const modalTriggers = document.querySelectorAll('[data-modal-target]');
    
    // Seleciona todos os botões de fechar que estão dentro de qualquer modal
    const closeButtons = document.querySelectorAll('.modal .close-button');

    // Adiciona um evento de clique para cada botão que abre um modal
    modalTriggers.forEach(trigger => {
        trigger.addEventListener('click', () => {
            // Pega o ID do modal do atributo 'data-modal-target' (ex: '#modal-especialista-1')
            const modal = document.querySelector(trigger.dataset.modalTarget);
            if (modal) {
                modal.style.display = 'block'; // Mostra o modal correspondente
            }
        });
    });

    // Adiciona um evento de clique para cada botão 'x' que fecha um modal
    closeButtons.forEach(button => {
        button.addEventListener('click', () => {
            // Encontra o modal pai mais próximo do botão 'x'
            const modal = button.closest('.modal');
            if (modal) {
                modal.style.display = 'none'; // Esconde o modal
            }
        });
    });

    // Adiciona um evento para fechar o modal se o usuário clicar fora da caixa de conteúdo
    window.addEventListener('click', (event) => {
        if (event.target.classList.contains('modal')) {
            event.target.style.display = 'none';
        }
    });


    // =========================================================
    // BLOCO 2: MÁSCARA DE TELEFONE GLOBAL
    // =========================================================
    const todosOsCamposDeTelefone = document.querySelectorAll('.phone-mask');
    todosOsCamposDeTelefone.forEach(function(input) {
        // Verifica se a biblioteca IMask existe antes de usá-la
        if (typeof IMask !== 'undefined') {
            IMask(input, { mask: '(00) 00000-0000' });
        }
    });


    // =========================================================
    // BLOCO 3: MÁSCARA DE CPF/CNPJ DO FORMULÁRIO DE EMPRESAS
    // =========================================================
    const cnpjCpfInput = document.getElementById('cnpj_cpf');
    if (cnpjCpfInput && typeof IMask !== 'undefined') {
        IMask(cnpjCpfInput, {
            mask: [
                { mask: '000.000.000-00', maxLength: 11 },
                { mask: '00.000.000/0000-00' }
            ]
        });
    }


    // =========================================================
    // BLOCO 4: LÓGICA DO FEEDBACK DE UPLOAD DE ARQUIVO
    // =========================================================
    const fileInput = document.getElementById('curriculo_pdf');
    const fileNameSpan = document.getElementById('file-name');
    if (fileInput && fileNameSpan) {
        fileInput.addEventListener('change', () => {
            if (fileInput.files.length > 0) {
                fileNameSpan.textContent = fileInput.files[0].name;
            } else {
                fileNameSpan.textContent = 'Nenhum arquivo selecionado';
            }
        });
    }


    // =========================================================
    // BLOCO 5: LÓGICA DO FORMULÁRIO DE CURRÍCULO DINÂMICO
    // =========================================================
    function setupDynamicSection(addButtonId, containerId, templateId) {
        const addButton = document.getElementById(addButtonId);
        const container = document.getElementById(containerId);
        const template = document.getElementById(templateId);

        if (!addButton || !container || !template) {
            return;
        }

        addButton.addEventListener('click', () => {
            const clone = template.content.cloneNode(true);
            const newItem = clone.querySelector('.dynamic-item');
            
            const removeButton = newItem.querySelector('.btn-remove');
            removeButton.addEventListener('click', () => {
                newItem.remove();
            });

            container.appendChild(newItem);
        });
    }
    setupDynamicSection('add-formacao', 'formacao-container', 'template-formacao');
    setupDynamicSection('add-experiencia', 'experiencia-container', 'template-experiencia');
    setupDynamicSection('add-idioma', 'idiomas-container', 'template-idioma');
    setupDynamicSection('add-curso', 'cursos-container', 'template-curso');

}); // <--- FIM DO ÚNICO DOMContentLoaded