# Gamer HUD Monitor Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Construir um mini monitor de hardware translúcido para desktop Windows (CPU, GPU e RAM em tempo real) com modo "click-through" ativado por atalho global (`F9`) para visualização contínua durante jogos.

**Architecture:** Arquitetura orientada a componentes em Python 3.12 com interface gráfica PyQt6 (frameless, translucent HUD). Um worker em background coleta métricas via NVML (RTX 3070 Ti) e psutil (CPU/RAM). Interoperação nativa com a Win32 API (`ctypes`) gerencia estilos estendidos de janela (`WS_EX_TRANSPARENT`) e registro global de hotkey. Persistência de coordenadas em `config.json` e controle via System Tray.

**Tech Stack:** Python 3.12, PyQt6, pynvml (nvidia-ml-py), psutil, ctypes (Win32 API), pytest.

**Spec:** `docs/superpowers/specs/2026-10-10-gamer-hud-monitor-design.md`

## Global Constraints
- Sistema Operacional: Windows 10/11.
- Consumo de recursos: ultra-leve (< 40MB RAM, < 0.2% CPU).
- Anti-cheat safe: zero injeção de DLL ou hooks gráficos nos jogos; apenas janela overlay com estilos estendidos Win32.
- Layout: visual Dark Frosted Glass com 3 colunas compactas e código de cores térmicas (verde, âmbar, vermelho).
- Atalho padrão: tecla `F9` para alternar Modo Jogo (click-through) e Modo Ajuste (arrastar).

---

### Task 1: Estrutura do Projeto, Dependências e ConfigManager

**Files:**
- Create: `requirements.txt`
- Create: `.gitignore`
- Create: `src/__init__.py`
- Create: `src/config.py`
- Create: `tests/__init__.py`
- Create: `tests/test_config.py`

**Interfaces:**
- Consumes: `json`, `os`, `pathlib`
- Produces: `ConfigManager` class com métodos `load() -> dict`, `save(data: dict) -> None`, `get(key: str, default) -> Any`, `set(key: str, value) -> None`

- [ ] **Step 1: Escrever teste de unidade para o ConfigManager**

```python
# tests/test_config.py
import json
import os
import pytest
from src.config import ConfigManager

def test_config_defaults(tmp_path):
    config_file = tmp_path / "config.json"
    cfg = ConfigManager(str(config_file))
    data = cfg.load()
    assert data["x"] == 100
    assert data["y"] == 100
    assert data["hotkey"] == "F9"
    assert data["update_interval_ms"] == 1000
    assert data["locked"] is True

def test_config_save_and_update(tmp_path):
    config_file = tmp_path / "config.json"
    cfg = ConfigManager(str(config_file))
    cfg.set("x", 450)
    cfg.set("y", 220)
    cfg.save()
    
    cfg2 = ConfigManager(str(config_file))
    assert cfg2.get("x") == 450
    assert cfg2.get("y") == 220
```

- [ ] **Step 2: Executar teste para verificar falha esperada**

Run: `pytest tests/test_config.py -v`
Expected: FAIL (módulo `src.config` não encontrado)

- [ ] **Step 3: Implementar `requirements.txt`, `.gitignore` e `src/config.py`**

```text
# requirements.txt
PyQt6>=6.6.0
nvidia-ml-py>=12.535.133
psutil>=5.9.0
pytest>=8.0.0
```

```python
# src/config.py
import json
import os
from pathlib import Path
from typing import Any, Dict

DEFAULT_CONFIG: Dict[str, Any] = {
    "x": 100,
    "y": 100,
    "hotkey": "F9",
    "update_interval_ms": 1000,
    "locked": True,
    "opacity": 0.85,
}

class ConfigManager:
    def __init__(self, file_path: str = "config.json"):
        self.file_path = Path(file_path)
        self.config: Dict[str, Any] = {}
        self.load()

    def load(self) -> Dict[str, Any]:
        if not self.file_path.exists():
            self.config = DEFAULT_CONFIG.copy()
            self.save()
            return self.config
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                loaded = json.load(f)
                self.config = {**DEFAULT_CONFIG, **loaded}
        except Exception:
            self.config = DEFAULT_CONFIG.copy()
        return self.config

    def save(self, data: Dict[str, Any] = None) -> None:
        if data is not None:
            self.config.update(data)
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(self.config, f, indent=4)

    def get(self, key: str, default: Any = None) -> Any:
        return self.config.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self.config[key] = value
```

- [ ] **Step 4: Instalar dependências e rodar teste para verificar aprovação**

Run: `pip install -r requirements.txt; pytest tests/test_config.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add requirements.txt .gitignore src/ tests/
git commit -m "feat: add project setup, dependencies, and ConfigManager"
```

---

### Task 2: Coleta de Métricas de Hardware (GPU NVML, CPU e RAM)

**Files:**
- Create: `src/hardware/__init__.py`
- Create: `src/hardware/gpu_nvml.py`
- Create: `src/hardware/cpu_sensors.py`
- Create: `src/hardware/collector.py`
- Create: `tests/test_hardware.py`

**Interfaces:**
- Consumes: `pynvml`, `psutil`, `PyQt6.QtCore.QThread`, `PyQt6.QtCore.pyqtSignal`
- Produces: 
  - `dataclass HardwareMetrics(cpu_usage: float, cpu_temp: float | None, gpu_usage: float, gpu_temp: float, ram_usage: float, ram_used_gb: float, ram_total_gb: float)`
  - `GpuNvmlReader` class com `get_metrics() -> tuple[float, float, float, float]`
  - `CpuSensorReader` class com `get_metrics() -> tuple[float, float | None, float, float, float]`
  - `HardwareCollector(QThread)` emitindo sinal `metrics_ready(HardwareMetrics)`

- [ ] **Step 1: Escrever teste de unidade para os leitores de hardware**

```python
# tests/test_hardware.py
from src.hardware.gpu_nvml import GpuNvmlReader
from src.hardware.cpu_sensors import CpuSensorReader

def test_cpu_sensor_reader():
    reader = CpuSensorReader()
    cpu_pct, cpu_temp, ram_pct, ram_used, ram_total = reader.get_metrics()
    assert 0.0 <= cpu_pct <= 100.0
    assert 0.0 <= ram_pct <= 100.0
    assert ram_used > 0.0
    assert ram_total > 0.0

def test_gpu_nvml_reader():
    reader = GpuNvmlReader()
    gpu_pct, gpu_temp, vram_used, vram_total = reader.get_metrics()
    assert isinstance(gpu_pct, float)
    assert isinstance(gpu_temp, float)
```

- [ ] **Step 2: Executar teste para verificar falha esperada**

Run: `pytest tests/test_hardware.py -v`
Expected: FAIL

- [ ] **Step 3: Implementar leitores de GPU, CPU e o Worker QThread**

Implementar `src/hardware/gpu_nvml.py` com suporte ao NVML oficial da NVIDIA e fallback gracioso caso NVML não esteja inicializado.
Implementar `src/hardware/cpu_sensors.py` com `psutil` e verificação segura de temperatura.
Implementar `src/hardware/collector.py` integrando tudo em `HardwareMetrics` e emitindo `metrics_ready` a cada intervalo configurado.

- [ ] **Step 4: Executar testes de hardware**

Run: `pytest tests/test_hardware.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/hardware/ tests/test_hardware.py
git commit -m "feat: add real-time hardware metrics collectors for GPU, CPU, and RAM"
```

---

### Task 3: Win32 API Interop (Click-Through e Global Hotkey F9)

**Files:**
- Create: `src/win32/__init__.py`
- Create: `src/win32/window_effects.py`
- Create: `src/win32/hotkey_manager.py`
- Create: `tests/test_win32.py`

**Interfaces:**
- Consumes: `ctypes`, `ctypes.wintypes`, `PyQt6.QtCore.QThread`, `PyQt6.QtCore.pyqtSignal`
- Produces:
  - `set_click_through(hwnd: int, enable: bool) -> None`
  - `set_tool_window(hwnd: int) -> None`
  - `GlobalHotkeyListener(hotkey_key: str)` emitindo sinal `hotkey_triggered()`

- [ ] **Step 1: Escrever teste de unidade para manipulação de flags Win32**

```python
# tests/test_win32.py
from src.win32.window_effects import get_window_extended_style

def test_get_window_extended_style_invalid_hwnd():
    # Deve retornar 0 ou lidar de forma segura com hwnd inexistente
    style = get_window_extended_style(0)
    assert isinstance(style, int)
```

- [ ] **Step 2: Executar teste para verificar falha esperada**

Run: `pytest tests/test_win32.py -v`
Expected: FAIL

- [ ] **Step 3: Implementar `src/win32/window_effects.py` e `src/win32/hotkey_manager.py`**

Implementar chamadas `GetWindowLongPtrW`, `SetWindowLongPtrW`, flags `WS_EX_TRANSPARENT`, `WS_EX_LAYERED`, `WS_EX_TOOLWINDOW`, `WS_EX_TOPMOST`.
Implementar classe `GlobalHotkeyListener(QThread)` com `user32.RegisterHotKey` (ID_HOTKEY, VK_F9 / 0x78) em loop de mensagens `GetMessageW` / `TranslateMessage` / `DispatchMessageW`.

- [ ] **Step 4: Executar testes Win32**

Run: `pytest tests/test_win32.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/win32/ tests/test_win32.py
git commit -m "feat: add win32 click-through extended styles and global hotkey listener"
```

---

### Task 4: UI Dark Frosted Glass e Overlay Window (PyQt6)

**Files:**
- Create: `src/ui/__init__.py`
- Create: `src/ui/styles.py`
- Create: `src/ui/overlay_window.py`
- Create: `src/ui/tray_icon.py`

**Interfaces:**
- Consumes: `PyQt6.QtWidgets`, `PyQt6.QtCore`, `PyQt6.QtGui`, `src.hardware.collector.HardwareMetrics`, `src.win32.window_effects`
- Produces:
  - `GamerHudWindow` widget com 3 colunas de métricas, suporte a arrastar no modo ajuste e alternância para click-through
  - `TrayIconManager` para gerenciar ícone na barra de tarefas

- [ ] **Step 1: Implementar `src/ui/styles.py` com design Dark Frosted Glass**

Definir paleta de cores moderna:
- Fundo escuro translúcido com gradiente suave e borda de 1px.
- Classes CSS `.metric-value`, `.metric-label`, `.status-good`, `.status-warm`, `.status-hot`.
- Estilo diferenciado para estado `[locked="false"]` (borda ciano sutil de ajuste).

- [ ] **Step 2: Implementar `src/ui/overlay_window.py`**

- Janela sem borda (`Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool`).
- Background translúcido (`WA_TranslucentBackground`).
- `mousePressEvent` e `mouseMoveEvent` para movimentação livre no modo ajuste.
- Método `set_locked(locked: bool)` que chama `set_click_through(hwnd, locked)` e atualiza o estilo visual e cursor.
- Método `update_metrics(metrics: HardwareMetrics)` que atualiza os valores e aplica as classes de cor com base nos limites térmicos.

- [ ] **Step 3: Implementar `src/ui/tray_icon.py`**

- Criação de ícone e menu de contexto com opções:
  - Alternar Modo Jogo / Ajuste (F9)
  - Resetar Posição
  - Sair

- [ ] **Step 4: Escrever teste de fumaça (smoke test) da UI**

Verificar instanciação do `GamerHudWindow` em ambiente headless/offscreen sem erros.

- [ ] **Step 5: Commit**

```bash
git add src/ui/
git commit -m "feat: add frosted glass HUD overlay window, styles, and system tray icon"
```

---

### Task 5: Integração Principal (Main Application) e Documentação

**Files:**
- Create: `src/main.py`
- Create: `README.md`

**Interfaces:**
- Conecta `ConfigManager`, `HardwareCollector`, `GlobalHotkeyListener`, `GamerHudWindow` e `TrayIconManager`.
- Salva coordenadas `(x, y)` no `config.json` ao encerrar ou movimentar.

- [ ] **Step 1: Implementar `src/main.py`**

Montar o ciclo de vida completo:
- Inicializa `QApplication`.
- Carrega configurações de `config.json`.
- Instancia `GamerHudWindow` e posiciona nas coordenadas salvas.
- Conecta sinal do `HardwareCollector` ao método `update_metrics` da janela.
- Conecta sinal do `GlobalHotkeyListener` ao toggle de modo travado/destravado.
- Conecta menu do Tray Icon aos controles da janela.
- Tratamento de encerramento gracioso (libera NVML, desregistra hotkey, salva posições).

- [ ] **Step 2: Criar `README.md` profissional**

Documentação com visual moderno, badges, instruções de instalação (`pip install -r requirements.txt`), como usar o atalho `F9`, modo jogo, e arquitetura de segurança contra anti-cheat.

- [ ] **Step 3: Executar a suíte completa de testes**

Run: `pytest tests/ -v`
Expected: Todos os testes passando (100% PASS).

- [ ] **Step 4: Testar execução interativa da aplicação**

Executar `python src/main.py` em segundo plano ou teste verificado para validar inicialização e ausência de exceções.

- [ ] **Step 5: Commit**

```bash
git add src/main.py README.md
git commit -m "feat: wire main application lifecycle, signal handlers, and documentation"
```

---

### Task 6: Criação e Publicação do Repositório no GitHub

**Files:**
- Repositório remoto no GitHub (`https://github.com/IuryAlmeidaDev/gamer-hud-monitor`)

- [ ] **Step 1: Criar repositório público/privado via GitHub CLI**

Run: `gh repo create gamer-hud-monitor --public --source=. --remote=origin --push`

- [ ] **Step 2: Verificar status remoto**

Run: `git remote -v; git status`
Expected: Branch `main` sincronizada com `origin/main`.
