// Estado global de la aplicación
const state = {
    selectedPipeline: 'amazon',
    files: [],
    isProcessing: false,
    jobId: null
};

// API base URL
const API_BASE = '';

// Elementos del DOM
const elements = {
    pipelineButtons: document.querySelectorAll('.pipeline-btn'),
    uploadArea: document.getElementById('uploadArea'),
    fileInput: document.getElementById('fileInput'),
    fileList: document.getElementById('fileList'),
    processBtn: document.getElementById('processBtn'),
    progressContainer: document.getElementById('progressContainer'),
    progressFill: document.getElementById('progressFill'),
    progressText: document.getElementById('progressText'),
    statusLog: document.getElementById('statusLog'),
    resultsSection: document.getElementById('resultsSection'),
    resultsInfo: document.getElementById('resultsInfo'),
    downloadBtn: document.getElementById('downloadBtn'),
    errorMessage: document.getElementById('errorMessage')
};

// Inicialización
document.addEventListener('DOMContentLoaded', function() {
    initializePipelineSelection();
    initializeFileUpload();
    initializeProcessing();
});

// === PIPELINE SELECTION ===
function initializePipelineSelection() {
    elements.pipelineButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            selectPipeline(btn.dataset.pipeline);
        });
    });
}

function selectPipeline(pipeline) {
    state.selectedPipeline = pipeline;

    elements.pipelineButtons.forEach(btn => {
        btn.classList.toggle('active', btn.dataset.pipeline === pipeline);
    });

    console.log(`Pipeline seleccionado: ${pipeline}`);
}

// === FILE UPLOAD ===
function initializeFileUpload() {
    // Click to upload
    elements.uploadArea.addEventListener('click', () => {
        if (!state.isProcessing) {
            elements.fileInput.click();
        }
    });

    // File input change
    elements.fileInput.addEventListener('change', (e) => {
        handleFiles(e.target.files);
    });

    // Drag and drop
    elements.uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        if (!state.isProcessing) {
            elements.uploadArea.classList.add('dragover');
        }
    });

    elements.uploadArea.addEventListener('dragleave', () => {
        elements.uploadArea.classList.remove('dragover');
    });

    elements.uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        elements.uploadArea.classList.remove('dragover');

        if (!state.isProcessing) {
            handleFiles(e.dataTransfer.files);
        }
    });
}

function handleFiles(fileList) {
    const validFiles = Array.from(fileList).filter(file => {
        return file.type.startsWith('image/');
    });

    if (validFiles.length === 0) {
        showError('Por favor selecciona archivos de imagen válidos');
        return;
    }

    // Agregar archivos al estado
    validFiles.forEach(file => {
        if (!state.files.find(f => f.name === file.name && f.size === file.size)) {
            state.files.push(file);
        }
    });

    updateFileList();
    updateProcessButton();
    hideError();
}

function updateFileList() {
    elements.fileList.innerHTML = '';

    state.files.forEach((file, index) => {
        const fileItem = document.createElement('div');
        fileItem.className = 'file-item fade-in';

        fileItem.innerHTML = `
            <div class="file-info">
                <span>📄 ${file.name}</span>
                <span class="file-size">(${formatFileSize(file.size)})</span>
            </div>
            <button class="remove-file" onclick="removeFile(${index})">✕</button>
        `;

        elements.fileList.appendChild(fileItem);
    });
}

function removeFile(index) {
    state.files.splice(index, 1);
    updateFileList();
    updateProcessButton();
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function updateProcessButton() {
    elements.processBtn.disabled = state.files.length === 0 || state.isProcessing;
}

// === PROCESSING ===
function initializeProcessing() {
    elements.processBtn.addEventListener('click', startProcessing);
    elements.downloadBtn.addEventListener('click', downloadResults);
}

async function startProcessing() {
    if (state.files.length === 0) {
        showError('Selecciona al menos una imagen para procesar');
        return;
    }

    state.isProcessing = true;
    updateProcessButton();

    showProgress();
    logStatus('Iniciando procesamiento...', 'info');

    try {
        // 1. Upload files
        logStatus('Subiendo archivos...', 'info');
        const uploadResponse = await uploadFiles();

        if (!uploadResponse.ok) {
            throw new Error(`Error al subir archivos: ${uploadResponse.statusText}`);
        }

        const uploadData = await uploadResponse.json();
        logStatus(`Archivos subidos exitosamente. Job ID: ${uploadData.job_id}`, 'success');

        state.jobId = uploadData.job_id;

        // 2. Start processing
        logStatus('Iniciando procesamiento...', 'info');
        const processResponse = await fetch(`${API_BASE}/api/v1/process`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                job_id: uploadData.job_id,
                pipeline: state.selectedPipeline,
                settings: {}
            })
        });

        if (!processResponse.ok) {
            throw new Error(`Error al iniciar procesamiento: ${processResponse.statusText}`);
        }

        // 3. Monitor progress
        await monitorProgress();

    } catch (error) {
        logStatus(`Error: ${error.message}`, 'error');
        showError(error.message);
        state.isProcessing = false;
        updateProcessButton();
    }
}

async function uploadFiles() {
    const formData = new FormData();

    state.files.forEach(file => {
        formData.append('files', file);
    });

    return fetch(`${API_BASE}/api/v1/upload`, {
        method: 'POST',
        body: formData
    });
}

async function monitorProgress() {
    const maxAttempts = 120; // 10 minutos máximo
    let attempts = 0;

    const checkProgress = async () => {
        try {
            const response = await fetch(`${API_BASE}/api/v1/status/${state.jobId}`);

            if (!response.ok) {
                throw new Error(`Error al obtener estado: ${response.statusText}`);
            }

            const data = await response.json();

            updateProgress(data.progress_percentage || 0);
            logStatus(`Progreso: ${data.progress_percentage || 0}% - ${data.status}`, 'info');

            if (data.status === 'completed') {
                onProcessingComplete(data);
                return;
            }

            if (data.status === 'failed') {
                throw new Error(data.error || 'El procesamiento falló');
            }

            attempts++;
            if (attempts >= maxAttempts) {
                throw new Error('Tiempo de espera agotado');
            }

            // Continuar monitoreando
            setTimeout(checkProgress, 5000);

        } catch (error) {
            logStatus(`Error al monitorear progreso: ${error.message}`, 'error');
            showError(error.message);
            state.isProcessing = false;
            updateProcessButton();
        }
    };

    checkProgress();
}

function updateProgress(progress) {
    const percentage = Math.min(100, Math.max(0, progress));
    elements.progressFill.style.width = `${percentage}%`;
    elements.progressText.textContent = `${Math.round(percentage)}%`;
}

function logStatus(message, type = 'info') {
    const entry = document.createElement('div');
    entry.className = `status-log-entry ${type}`;
    entry.textContent = `${new Date().toLocaleTimeString()}: ${message}`;

    elements.statusLog.appendChild(entry);
    elements.statusLog.scrollTop = elements.statusLog.scrollHeight;
}

function onProcessingComplete(data) {
    state.isProcessing = false;
    updateProcessButton();

    logStatus('¡Procesamiento completado exitosamente!', 'success');
    updateProgress(100);

    // Mostrar resultados
    elements.resultsInfo.textContent = `Se procesaron ${state.files.length} imágenes exitosamente.`;
    elements.resultsSection.style.display = 'block';
    elements.resultsSection.classList.add('fade-in');
}

async function downloadResults() {
    if (!state.jobId) {
        showError('No hay resultados para descargar');
        return;
    }

    try {
        logStatus('Preparando descarga...', 'info');

        const response = await fetch(`${API_BASE}/api/v1/download/${state.jobId}`);

        if (!response.ok) {
            throw new Error(`Error al descargar: ${response.statusText}`);
        }

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);

        const a = document.createElement('a');
        a.href = url;
        a.download = `masterpost_${state.jobId}.zip`;
        document.body.appendChild(a);
        a.click();

        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);

        logStatus('Descarga completada', 'success');

    } catch (error) {
        logStatus(`Error en descarga: ${error.message}`, 'error');
        showError(error.message);
    }
}

// === UI HELPERS ===
function showProgress() {
    elements.progressContainer.style.display = 'block';
    elements.progressContainer.classList.add('fade-in');
    elements.resultsSection.style.display = 'none';
    hideError();
}

function showError(message) {
    elements.errorMessage.textContent = message;
    elements.errorMessage.style.display = 'block';
    elements.errorMessage.classList.add('fade-in');
}

function hideError() {
    elements.errorMessage.style.display = 'none';
}

// === RESET FUNCTION ===
function resetApplication() {
    state.files = [];
    state.isProcessing = false;
    state.jobId = null;

    updateFileList();
    updateProcessButton();
    elements.progressContainer.style.display = 'none';
    elements.resultsSection.style.display = 'none';
    elements.statusLog.innerHTML = '';
    hideError();

    logStatus('Aplicación reiniciada', 'info');
}

// Función global para remover archivos (llamada desde HTML)
window.removeFile = removeFile;