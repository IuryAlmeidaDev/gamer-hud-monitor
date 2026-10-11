# Especificação de Design: Gamer HUD Monitor

## 1. Visão Geral
O **Gamer HUD Monitor** é um monitor de desempenho de hardware ultra-leve, discreto e elegante para Windows, projetado especificamente para rodar sobreposto a jogos. Ele exibe em tempo real o uso e temperatura do processador (CPU), placa de vídeo (GPU) e memória RAM através de um mini widget translúcido (estilo HUD Gamer "Frosted Glass").

O diferencial do sistema é o suporte nativo a **Modo Jogo (Click-Through)**: através de uma tecla de atalho (`F9`), o widget alterna entre um modo em que pode ser arrastado livremente com o mouse e um modo 100% transparente a cliques, permitindo que o jogador atire, mire e interaja com o jogo sem nenhum clique acidental no monitor.

---

## 2. Princípios de Design & UI/UX (Diretrizes Impeccable)
1. **Zero Distração & Máxima Legibilidade:**
   - Formato de cápsula horizontal compacta (~260px x 64px) posicionável em qualquer canto da tela.
   - Fundo em "Dark Frosted Glass" semitransparente (`rgba(15, 17, 23, 0.78)`), cantos arredondados (`border-radius: 12px`) e borda sutil de 1px (`rgba(255, 255, 255, 0.12)`).
   - Tipografia de largura fixa / tabular (*Segoe UI Variable* / *Consolas*) para impedir que os números oscilem a largura do HUD.
2. **Semântica de Cores Inteligente (Feedback Imediato):**
   - 🟢 **Verde/Ciano (#00e676 / #00e5ff):** Operação normal (temperatura < 70°C, carga moderada).
   - 🟡 **Âmbar/Laranja (#ffab00 / #ff9100):** Carga elevada (temperatura entre 70°C e 82°C).
   - 🔴 **Vermelho Coral (#ff5252):** Alerta térmico crítico (temperatura > 85°C).
3. **Comportamento dos Modos:**
   - **Modo Ajuste (Destravado):** Borda suavemente iluminada em ciano; cursor `SizeAllCursor`; usuário pode clicar e arrastar para qualquer posição do monitor.
   - **Modo Jogo (Travado & Click-Through):** Borda sutil; a janela ganha os atributos de estilo estendido `WS_EX_TRANSPARENT | WS_EX_LAYERED` da Win32 API. Cliques passam diretamente para a janela de jogo subjacente.
   - **Atalho de Alternância:** Tecla `F9` (global no Windows, detectada mesmo com jogos em foco).
   - **Feedback Visual:** Notificação sutil ou pulso de cor ao alternar de modo.

---

## 3. Arquitetura Técnica & Componentes

### 3.1 Stack Tecnológico
- **Linguagem & Runtime:** Python 3.12 (instalado nativamente).
- **Interface Gráfica:** `PyQt6` (alta performance de renderização, suporte a janelas translúcidas com aceleração gráfica).
- **GPU Metrics (NVIDIA):** `pynvml` (NVIDIA Management Library oficial). Leitura sem latência de % de carga da GPU, temperatura do chip em °C e uso de VRAM da RTX 3070 Ti.
- **CPU & RAM Metrics:** `psutil` para uso percentual e alocação de memória RAM.
- **Sensor Térmico de CPU:** Módulo híbrido com leitura WMI / LibreHardwareMonitor / driver de placa-mãe e fallback gracioso (se sensores não estiverem acessíveis sem privilégios elevados, exibe carga com etiqueta limpa sem falhar).
- **Win32 API Interop:** `ctypes.windll.user32` para `SetWindowLongPtrW`, `GetWindowLongPtrW`, flags `WS_EX_TRANSPARENT`, `WS_EX_LAYERED`, `WS_EX_TOOLWINDOW`, `WS_EX_TOPMOST`, e registro de hotkey global via `RegisterHotKey`.

### 3.2 Diagrama de Componentes
```
+------------------------------------------------------------------------+
|                            gamer-hud-monitor                           |
|                                                                        |
|  +--------------------+   Signals   +-------------------------------+  |
|  |  HardwareCollector | ----------->|          GamerHudWindow       |  |
|  |  (QThread Worker)  |             |  - Frameless & Topmost Window |  |
|  |  - pynvml (GPU)    |             |  - Frosted Glass QSS Styling  |  |
|  |  - psutil (CPU/RAM)|             |  - Win32 Click-through toggle |  |
|  +--------------------+             +---------------+---------------+  |
|                                                     |                  |
|  +--------------------+                             |                  |
|  |   HotkeyListener   | ----------------------------+                  |
|  |   (Win32 F9 Hook)  |                                                |
|  +--------------------+                                                |
|                                                     |                  |
|  +--------------------+                             v                  |
|  |   TrayIconManager  |<--------------------+  ConfigManager           |
|  |   (System Tray)    |                     |  (config.json)           |
|  +--------------------+                     +--------------------------+
+------------------------------------------------------------------------+
```

### 3.3 Estrutura de Arquivos do Projeto
```text
gamer-hud-monitor/
├── .gitignore
├── README.md
├── requirements.txt
├── config.json                     # Posição salva, taxas, atalhos
├── docs/
│   └── superpowers/
│       └── specs/
│           └── 2026-10-10-gamer-hud-monitor-design.md
└── src/
    ├── __init__.py
    ├── main.py                     # Entry point da aplicação
    ├── config.py                   # Gerenciamento de persistência de configurações
    ├── hardware/
    │   ├── __init__.py
    │   ├── collector.py            # Coleta de métricas em QThread
    │   ├── gpu_nvml.py             # Leitor de dados NVIDIA via NVML
    │   └── cpu_sensors.py          # Leitor de CPU/RAM com fallback seguro
    ├── ui/
    │   ├── __init__.py
    │   ├── overlay_window.py       # Janela HUD frameless com PyQt6
    │   ├── styles.py               # Folha de estilos QSS (Dark Glass)
    │   └── tray_icon.py            # Ícone e menu na bandeja do sistema
    └── win32/
        ├── __init__.py
        ├── window_effects.py       # Funções ctypes para click-through e topmost
        └── hotkey_manager.py       # Hook nativo de atalho F9
```

---

## 4. Fluxo de Dados e Ciclo de Vida
1. **Inicialização:**
   - Carrega `config.json` (recupera posição X, Y anterior ou centraliza no topo direito por padrão).
   - Inicializa `pynvml` e `psutil`.
   - Cria `GamerHudWindow` com atributos `FramelessWindowHint`, `WindowStaysOnTopHint` e `Tool`.
   - Inicializa ícone no System Tray.
   - Registra Hotkey global `F9`.
   - Inicia `HardwareCollector` (intervalo de 1000ms).
2. **Atualização Visual:**
   - A cada 1 segundo, `HardwareCollector` emite sinal PyQt `metrics_updated(HardwareMetrics)`.
   - `GamerHudWindow` atualiza os labels e classes CSS (verde/laranja/vermelho).
3. **Alternância de Modo:**
   - Usuário pressiona `F9`.
   - `HotkeyListener` dispara evento.
   - `GamerHudWindow` chama `window_effects.toggle_click_through(hwnd)`.
   - Borda do HUD atualiza estilo visual para informar o usuário.
4. **Encerramento:**
   - Ao fechar pelo System Tray ou atalho, salva coordenadas atuais em `config.json`.
   - Desregistra hotkey e finaliza NVML de forma limpa.

---

## 5. Estratégia de Testes e Validação
1. **Teste Unitário dos Leitores de Hardware:**
   - Testar leitura de GPU (validar detecção da RTX 3070 Ti, % de uso e temperatura).
   - Testar leitura de CPU e memória RAM via `psutil`.
   - Validar comportamento com e sem GPU NVIDIA disponível.
2. **Teste de Persistência de Configuração:**
   - Validar gravação e leitura do `config.json` com valores padrão seguros.
3. **Teste de Interop Win32:**
   - Validar que a alternância de `WS_EX_TRANSPARENT` adiciona e remove a flag sem corromper outros estilos de janela.
4. **Verificação em Tempo de Execução:**
   - Executar a aplicação, testar arrasto, testar atalho `F9`, confirmar que cliques passam através da janela em modo travado e verificar consumo de memória RAM (< 40MB).
