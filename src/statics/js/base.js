const markdownDropZone = document.getElementById('markdown-drop-zone');
const markdownFileInput = document.getElementById('markdown_file');
const markdownFileNameSpan = document.getElementById('markdown-file-name');

const jsonDropZone = document.getElementById('json-drop-zone');
const jsonFileInput = document.getElementById('postman_json_file');
const jsonFileNameSpan = document.getElementById('json-file-name');

const uploadForm = document.getElementById('uploadForm');
const messageBox = document.getElementById('messageBox');
const loadingOverlay = document.getElementById('loading-overlay');

function showLoading() {
    loadingOverlay.classList.add('show');
}
function hideLoading() {
    loadingOverlay.classList.remove('show');
}

['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
    markdownDropZone.addEventListener(eventName, preventDefaults, false);
});
markdownDropZone.addEventListener('dragenter', () => markdownDropZone.classList.add('highlight'), false);
markdownDropZone.addEventListener('dragleave', () => markdownDropZone.classList.remove('highlight'), false);
markdownDropZone.addEventListener('drop', handleMarkdownDrop, false);
function handleMarkdownDrop(e) {
    const dt = e.dataTransfer;
    const files = dt.files;
    if (files.length > 0) {
        markdownFileInput.files = files;
        updateMarkdownFileName();
        jsonFileInput.value = '';
        jsonFileNameSpan.textContent = 'Nenhum arquivo JSON selecionado';
        hideMessage();
    }
}
markdownDropZone.addEventListener('click', () => { markdownFileInput.click(); });
markdownFileInput.addEventListener('change', updateMarkdownFileName);

function updateMarkdownFileName() {
    if (markdownFileInput.files.length > 0) {
        const fileName = markdownFileInput.files[0].name;
        markdownFileNameSpan.textContent = `Arquivo selecionado: ${fileName}`;
        if (!fileName.toLowerCase().endsWith('.md') && !fileName.toLowerCase().endsWith('.markdown')) {
            showMessage('Por favor, selecione um arquivo Markdown válido (.md ou .markdown).', 'error');
            markdownFileInput.value = '';
            markdownFileNameSpan.textContent = 'Nenhum arquivo selecionado';
        } else {
            hideMessage();

            jsonFileInput.value = '';
            jsonFileNameSpan.textContent = 'Nenhum arquivo JSON selecionado';
        }
    } else {
        markdownFileNameSpan.textContent = 'Nenhum arquivo selecionado';
    }
}

['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
    jsonDropZone.addEventListener(eventName, preventDefaults, false);
    document.body.addEventListener(eventName, preventDefaults, false); // Para capturar drops fora da zona
});
jsonDropZone.addEventListener('dragenter', () => jsonDropZone.classList.add('highlight'), false);
jsonDropZone.addEventListener('dragleave', () => jsonDropZone.classList.remove('highlight'), false);
jsonDropZone.addEventListener('drop', handleJsonDrop, false);
function handleJsonDrop(e) {
    const dt = e.dataTransfer;
    const files = dt.files;
    if (files.length > 0) {
        jsonFileInput.files = files;
        updateJsonFileName();

        markdownFileInput.value = '';
        markdownFileNameSpan.textContent = 'Nenhum arquivo selecionado';
        hideMessage();
    }
}
jsonDropZone.addEventListener('click', () => { jsonFileInput.click(); });
jsonFileInput.addEventListener('change', updateJsonFileName);

function updateJsonFileName() {
    if (jsonFileInput.files.length > 0) {
        const fileName = jsonFileInput.files[0].name;
        jsonFileNameSpan.textContent = `Arquivo selecionado: ${fileName}`;
        if (!fileName.toLowerCase().endsWith('.json')) {
            showMessage('Por favor, selecione um arquivo JSON válido (.json).', 'error');
            jsonFileInput.value = '';
            jsonFileNameSpan.textContent = 'Nenhum arquivo JSON selecionado';
        } else {
            hideMessage();

            markdownFileInput.value = '';
            markdownFileNameSpan.textContent = 'Nenhum arquivo selecionado';
        }
    } else {
        jsonFileNameSpan.textContent = 'Nenhum arquivo JSON selecionado';
    }
}

uploadForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    messageBox.style.display = 'none';
    messageBox.classList.remove('success', 'error');

    const hasMarkdownFile = markdownFileInput.files.length > 0;
    const hasJsonFile = jsonFileInput.files.length > 0;

    if (!hasMarkdownFile && !hasJsonFile) {
        showMessage('Por favor, selecione ou arraste um arquivo Markdown ou um arquivo JSON da Coleção Postman.', 'error');
        return;
    }
    if (hasMarkdownFile && hasJsonFile) {
        showMessage('Por favor, escolha APENAS UMA opção: upload de arquivo Markdown OU arquivo JSON da Coleção Postman.', 'error');
        return;
    }

    showLoading();

    const formData = new FormData(uploadForm);

    try {
        const response = await fetch('/convert/', {
            method: 'POST',
            body: formData,
        });

        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const disposition = response.headers.get('Content-Disposition');
            let filename = 'document.pdf';
            if (disposition && disposition.indexOf('attachment') !== -1) {
                const filenameMatch = disposition.match(/filename="([^"]+)"/);
                if (filenameMatch && filenameMatch[1]) {
                    filename = filenameMatch[1];
                }
            }

            const a = document.createElement('a');
            a.href = url;
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            a.remove();
            window.URL.revokeObjectURL(url);

            showMessage('PDF gerado com sucesso!', 'success');
            uploadForm.reset();
            markdownFileNameSpan.textContent = 'Nenhum arquivo selecionado';
            jsonFileNameSpan.textContent = 'Nenhum arquivo JSON selecionado';

        } else {
            const errorData = await response.json();
            showMessage(`Erro: ${errorData.detail || 'Ocorreu um erro desconhecido.'}`, 'error');
        }
    } catch (error) {
        showMessage(`Erro de rede ou comunicação: ${error.message}`, 'error');
    } finally {
        hideLoading();
    }
});

function showMessage(message, type) {
    messageBox.textContent = message;
    messageBox.classList.add(type);
    messageBox.style.display = 'block';
}

function hideMessage() {
    messageBox.style.display = 'none';
}

function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
}