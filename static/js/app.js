// ============================================
//   SISTEMA DE ETIQUETAS MONTAGEM - JAVASCRIPT
//   Funcionalidades Modernas e Responsivas
// ============================================

// === CONFIGURAÇÕES GLOBAIS ===
const CONFIG = {
    API_BASE_URL: window.location.origin,
    DEBOUNCE_DELAY: 300,
    ANIMATION_DURATION: 300,
    SNACKBAR_DURATION: 4000,
    CAMERA_SCAN_INTERVAL: 100
};

// === ESTADO GLOBAL ===
let globalState = {
    currentData: null,
    cameraActive: false,
    codeReader: null,
    scanningActive: false
};

// === UTILITÁRIOS ===
const Utils = {
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },

    formatDate(dateString) {
        if (!dateString) return 'N/A';
        try {
            const date = new Date(dateString);
            return date.toLocaleDateString('pt-BR', {
                day: '2-digit',
                month: '2-digit',
                year: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            });
        } catch {
            return dateString;
        }
    },

    sanitizeHtml(str) {
        const div = document.createElement('div');
        div.textContent = str;
        return div.innerHTML;
    },

    showLoading() {
        const loading = document.getElementById('loading');
        if (loading) {
            loading.style.display = 'flex';
            document.body.style.overflow = 'hidden';
        }
    },

    hideLoading() {
        const loading = document.getElementById('loading');
        if (loading) {
            loading.style.display = 'none';
            document.body.style.overflow = '';
        }
    }
};

// === SNACKBAR ===
const Snackbar = {
    show(message, type = 'info') {
        const snackbar = document.getElementById('snackbar');
        const messageEl = snackbar.querySelector('.snackbar-message');
        
        // Remove classes anteriores
        snackbar.className = 'snackbar';
        
        // Adiciona nova classe de tipo
        snackbar.classList.add(type);
        
        // Define mensagem
        messageEl.textContent = message;
        
        // Mostra snackbar
        snackbar.style.display = 'block';
        setTimeout(() => snackbar.classList.add('show'), 10);
        
        // Auto-hide
        setTimeout(() => {
            snackbar.classList.remove('show');
            setTimeout(() => {
                snackbar.style.display = 'none';
            }, 300);
        }, CONFIG.SNACKBAR_DURATION);
    }
};

// === CÂMERA E SCANNER ===
const CameraScanner = {
    async init() {
        // Aguardar ZXing carregar
        setTimeout(() => {
            try {
                if (typeof ZXing !== 'undefined') {
                    globalState.codeReader = new ZXing.BrowserMultiFormatReader();
                    console.log('Scanner ZXing inicializado com sucesso');
                } else {
                    console.warn('ZXing não disponível');
                }
            } catch (error) {
                console.error('Erro ao inicializar scanner:', error);
            }
        }, 1000);
    },

    async startCamera() {
        if (globalState.cameraActive) {
            CameraScanner.stopCamera();
            return;
        }

        const cameraContainer = document.getElementById('cameraContainer');
        const video = document.getElementById('video');
        const btnCamera = document.getElementById('btnCamera');
        
        // Sempre mostra o container primeiro
        cameraContainer.style.display = 'block';
        video.style.display = 'block';
        btnCamera.innerHTML = '<i class="fas fa-times"></i><span class="btn-text">Fechar</span>';
        btnCamera.classList.add('active');
        globalState.cameraActive = true;

        // Verificar se getUserMedia está disponível
        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
            Snackbar.show('Câmera não disponível neste navegador', 'warning');
            return;
        }

        try {
            // Tentar câmera traseira primeiro
            const stream = await navigator.mediaDevices.getUserMedia({
                video: { facingMode: 'environment' }
            });
            video.srcObject = stream;
            
            // Iniciar scanning após câmera estar pronta
            video.onloadedmetadata = () => {
                CameraScanner.startScanning();
            };
            
            Snackbar.show('Câmera traseira ativada', 'success');
        } catch (error) {
            try {
                // Fallback para qualquer câmera
                const stream = await navigator.mediaDevices.getUserMedia({ video: true });
                video.srcObject = stream;
                
                // Iniciar scanning após câmera estar pronta
                video.onloadedmetadata = () => {
                    CameraScanner.startScanning();
                };
                
                Snackbar.show('Câmera ativada', 'success');
            } catch (fallbackError) {
                console.error('Erro ao acessar câmera:', fallbackError);
                Snackbar.show('Câmera não disponível. Use digitação manual', 'warning');
            }
        }
    },

    stopCamera() {
        const cameraContainer = document.getElementById('cameraContainer');
        const video = document.getElementById('video');
        const btnCamera = document.getElementById('btnCamera');
        
        // Para o leitor de código se estiver ativo
        if (globalState.codeReader) {
            try {
                globalState.codeReader.reset();
            } catch (e) {
                console.log('Erro ao resetar leitor:', e);
            }
        }
        
        // Para o stream da câmera
        if (video && video.srcObject) {
            const tracks = video.srcObject.getTracks();
            tracks.forEach(track => track.stop());
            video.srcObject = null;
        }
        
        // Esconde container
        if (cameraContainer) cameraContainer.style.display = 'none';
        if (video) video.style.display = 'none';
        
        // Restaura botão
        if (btnCamera) {
            btnCamera.innerHTML = '<i class="fas fa-camera"></i><span class="btn-text">Câmera</span>';
            btnCamera.classList.remove('active');
        }
        
        globalState.cameraActive = false;
        globalState.scanningActive = false;
    },

    startScanning() {
        if (globalState.scanningActive) return;
        
        globalState.scanningActive = true;
        const video = document.getElementById('video');
        
        // Tentar inicializar ZXing se não estiver disponível
        if (!globalState.codeReader && typeof ZXing !== 'undefined') {
            try {
                globalState.codeReader = new ZXing.BrowserMultiFormatReader();
                console.log('ZXing inicializado durante scanning');
            } catch (e) {
                console.error('Erro ao inicializar ZXing:', e);
            }
        }
        
        // Inicia decodificação contínua se ZXing estiver disponível
        if (globalState.codeReader) {
            try {
                globalState.codeReader.decodeFromVideoDevice(null, video, (result, err) => {
                    if (result) {
                        console.log('Código detectado:', result.text);
                        
                        // Para o scanning
                        CameraScanner.stopCamera();
                        
                        // Preenche o campo de input
                        const codigoInput = document.getElementById('codigoBarras');
                        if (codigoInput) {
                            codigoInput.value = result.text;
                            
                            // Dispara busca automática
                            setTimeout(() => {
                                SerialSearch.buscarSerial();
                            }, 500);
                        }
                        
                        Snackbar.show(`Código detectado: ${result.text}`, 'success');
                    }
                    
                    if (err && typeof ZXing !== 'undefined' && !(err instanceof ZXing.NotFoundException)) {
                        console.error('Erro no scanning:', err);
                    }
                });
                console.log('Scanning iniciado com ZXing');
            } catch (error) {
                console.error('Erro ao iniciar scanning:', error);
                Snackbar.show('Erro ao iniciar scanner. Digite manualmente', 'warning');
            }
        } else {
            console.warn('ZXing não disponível para scanning');
            Snackbar.show('Scanner de código não disponível. Digite manualmente', 'warning');
        }
    }
};

// === BUSCA DE SERIAL ===
const SerialSearch = {
    async buscarSerial() {
        const codigoInput = document.getElementById('codigoBarras');
        const codigo = codigoInput.value.trim();
        
        if (!codigo) {
            Snackbar.show('Digite um código de barras', 'warning');
            codigoInput.focus();
            return;
        }
        
        Utils.showLoading();
        
        try {
            const response = await fetch('/buscar', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    codigoBarras: codigo
                })
            });
            
            const result = await response.json();
            
            if (response.ok && result.success) {
                globalState.currentData = {
                    ...result.data,
                    peca: result.peca,
                    op: result.op
                };
                this.exibirResultado(result);
            } else {
                Snackbar.show(result.error || 'Erro ao buscar dados', 'error');
                this.limparResultados();
            }
            
        } catch (error) {
            console.error('Erro na busca:', error);
            Snackbar.show('Erro ao buscar dados. Verifique a conexão.', 'error');
            this.limparResultados();
        } finally {
            Utils.hideLoading();
        }
    },
    
    exibirResultado(result) {
        // Mostra apenas as informações do registro
        this.exibirInformacoes(result);
        
        // Mostra ações
        const actionsCard = document.getElementById('actionsCard');
        actionsCard.style.display = 'block';
        
        // Scroll suave para o resultado
        const infoCard = document.getElementById('infoCard');
        infoCard.scrollIntoView({ behavior: 'smooth', block: 'start' });
    },
    
    exibirInformacoes(result) {
        const infoCard = document.getElementById('infoCard');
        const infoGrid = document.getElementById('infoGrid');
        
        const informacoes = [
            { label: 'Serial Number', value: result.data.serial_number },
            { label: 'Peça', value: result.data.peca || result.peca },
            { label: 'OP', value: result.data.op || result.op },
            { label: 'Projeto', value: result.data.projeto || 'Não encontrado' },
            { label: 'Veículo', value: result.data.veiculo || 'Não encontrado' }
        ];
        
        infoGrid.innerHTML = informacoes.map(info => `
            <div class="info-item">
                <div class="info-label">${Utils.sanitizeHtml(info.label)}</div>
                <div class="info-value">${Utils.sanitizeHtml(info.value)}</div>
            </div>
        `).join('');
        
        infoCard.style.display = 'block';
    },
    
    limparResultados() {
        // Esconde todos os cards de resultado
        ['infoCard', 'actionsCard'].forEach(id => {
            const element = document.getElementById(id);
            if (element) element.style.display = 'none';
        });
        
        // Limpa input
        const codigoInput = document.getElementById('codigoBarras');
        if (codigoInput) {
            codigoInput.value = '';
            codigoInput.focus();
        }
        
        // Reseta estado
        globalState.currentData = null;
    }
};

// === IMPRESSÃO ===
const PrintManager = {
    async imprimirEtiqueta() {
        if (!globalState.currentData) {
            Snackbar.show('Nenhum serial selecionado', 'warning');
            return;
        }
        
        // Impressão direta sem modal
        Utils.showLoading();
        
        try {
            const response = await fetch('/imprimir', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    serialNumber: globalState.currentData.serial_number
                })
            });
            
            const result = await response.json();
            
            if (response.ok && result.success) {
                Snackbar.show('Etiqueta impressa com sucesso!', 'success');
                SerialSearch.limparResultados();
            } else {
                Snackbar.show(result.error || 'Erro ao imprimir etiqueta', 'error');
            }
            
        } catch (error) {
            console.error('Erro na impressão:', error);
            Snackbar.show('Erro ao imprimir etiqueta. Tente novamente.', 'error');
        } finally {
            Utils.hideLoading();
        }
    },
    
    // Função de apontamento removida
    // async imprimirComColaborador(colaborador) { ... }
    
    async buscarEImprimir() {
        const codigoInput = document.getElementById('codigoBarras');
        const codigo = codigoInput.value.trim();
        
        if (!codigo) {
            Snackbar.show('Digite um código de barras', 'warning');
            codigoInput.focus();
            return;
        }
        
        Utils.showLoading();
        
        try {
            const response = await fetch('/buscar-e-imprimir', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    codigoBarras: codigo
                })
            });
            
            const result = await response.json();
            
            if (response.ok && result.success) {
                Snackbar.show('Etiqueta impressa com sucesso!', 'success');
                globalState.currentData = result.data;
                SerialSearch.exibirResultado(result);
            } else {
                Snackbar.show(result.error || 'Erro ao processar', 'error');
                SerialSearch.limparResultados();
            }
            
        } catch (error) {
            console.error('Erro no processo:', error);
            Snackbar.show('Erro ao processar. Verifique a conexão.', 'error');
        } finally {
            Utils.hideLoading();
        }
    }
};

// === RELÓGIO ===
const Clock = {
    init() {
        this.updateTime();
        setInterval(() => this.updateTime(), 1000);
    },
    
    updateTime() {
        const timeDisplay = document.getElementById('timeDisplay');
        if (timeDisplay) {
            const now = new Date();
            const timeString = now.toLocaleTimeString('pt-BR', {
                hour: '2-digit',
                minute: '2-digit',
                second: '2-digit'
            });
            const dateString = now.toLocaleDateString('pt-BR', {
                day: '2-digit',
                month: '2-digit',
                year: 'numeric'
            });
            timeDisplay.textContent = `${timeString} - ${dateString}`;
        }
    }
};

// === MODAL COLABORADOR - REMOVIDO ===
// const ColaboradorModal = { ... };

// === MODAL PDF ===
const PDFModal = {
    show(pdfUrl) {
        const modal = document.getElementById('pdfModal');
        const iframe = document.getElementById('pdfViewer');
        
        if (modal && iframe) {
            iframe.src = pdfUrl;
            modal.style.display = 'flex';
            document.body.style.overflow = 'hidden';
        }
    },
    
    hide() {
        const modal = document.getElementById('pdfModal');
        const iframe = document.getElementById('pdfViewer');
        
        if (modal && iframe) {
            modal.style.display = 'none';
            iframe.src = '';
            document.body.style.overflow = '';
        }
    },
    
    print() {
        const iframe = document.getElementById('pdfViewer');
        if (iframe && iframe.contentWindow) {
            iframe.contentWindow.print();
        }
    }
};

// === INICIALIZAÇÃO ===
document.addEventListener('DOMContentLoaded', function() {
    console.log('Sistema de Etiquetas Montagem iniciado');
    
    // Inicializa componentes
    Clock.init();
    CameraScanner.init();
    
    // Event Listeners
    const btnBuscar = document.getElementById('btnBuscar');
    const btnCamera = document.getElementById('btnCamera');
    const btnImprimirTodos = document.getElementById('btnImprimirTodos');
    const btnLimpar = document.getElementById('btnLimpar');
    const codigoInput = document.getElementById('codigoBarras');
    
    // Busca
    if (btnBuscar) {
        btnBuscar.addEventListener('click', () => SerialSearch.buscarSerial());
    }
    
    // Câmera
    if (btnCamera) {
        btnCamera.addEventListener('click', () => CameraScanner.startCamera());
    }
    
    // Impressão - usar modal de colaborador
    if (btnImprimirTodos) {
        btnImprimirTodos.addEventListener('click', () => PrintManager.imprimirEtiqueta());
    }
    
    // Limpar
    if (btnLimpar) {
        btnLimpar.addEventListener('click', SerialSearch.limparResultados);
    }
    
    // Enter no input de código
    if (codigoInput) {
        codigoInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                SerialSearch.buscarSerial();
            }
        });
        
        // Auto-focus no input
        codigoInput.focus();
    }
    
    // Modal Colaborador - REMOVIDO
    
    // Modal PDF
    const btnFecharModal = document.getElementById('btnFecharModal');
    const btnFecharModalFooter = document.getElementById('btnFecharModalFooter');
    const btnImprimirModal = document.getElementById('btnImprimirModal');
    
    if (btnFecharModal) {
        btnFecharModal.addEventListener('click', PDFModal.hide);
    }
    
    if (btnFecharModalFooter) {
        btnFecharModalFooter.addEventListener('click', PDFModal.hide);
    }
    
    if (btnImprimirModal) {
        btnImprimirModal.addEventListener('click', PDFModal.print);
    }
    
    // Fechar modals clicando no overlay - Modal colaborador removido
    
    const pdfModal = document.getElementById('pdfModal');
    if (pdfModal) {
        pdfModal.addEventListener('click', function(e) {
            if (e.target === pdfModal) {
                PDFModal.hide();
            }
        });
    }
    
    // Esc para fechar modals
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            PDFModal.hide();
            if (globalState.cameraActive) {
                CameraScanner.stopCamera();
            }
        }
    });
    
    console.log('Event listeners configurados');
});