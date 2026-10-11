from typing import Callable, Optional
from PyQt6.QtCore import Qt, QPoint, pyqtSignal
from PyQt6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QFrame,
    QGraphicsDropShadowEffect,
)
from PyQt6.QtGui import QColor, QCursor

from src.hardware.collector import HardwareMetrics
from src.ui.styles import get_hud_stylesheet
from src.win32.window_effects import set_click_through, set_tool_window

class GamerHudWindow(QWidget):
    """
    Janela flutuante minimalista, translúcida e sempre no topo.
    Permite alternar entre modo de arrasto (ajuste) e modo click-through (jogo).
    """
    position_changed = pyqtSignal(int, int)
    lock_state_changed = pyqtSignal(bool)

    def __init__(self, x: int = 100, y: int = 100, locked: bool = True):
        super().__init__()
        self.locked = locked
        self._drag_start_pos: Optional[QPoint] = None

        self._setup_window_flags()
        self._build_ui()
        self.apply_style()

        self.move(x, y)

    def _setup_window_flags(self) -> None:
        # Janela sem bordas, sempre no topo e fora do Alt+Tab (Tool)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, True)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)

    def _build_ui(self) -> None:
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(6, 6, 6, 6)
        main_layout.setSpacing(0)

        # Container principal com cantos arredondados e fundo frosted
        self.container = QWidget()
        self.container.setObjectName("HudContainer")
        container_layout = QHBoxLayout(self.container)
        container_layout.setContentsMargins(14, 8, 14, 8)
        container_layout.setSpacing(12)

        # Sombra sutil para destacar sobre qualquer jogo
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(18)
        shadow.setColor(QColor(0, 0, 0, 180))
        shadow.setOffset(0, 4)
        self.container.setGraphicsEffect(shadow)

        # Coluna CPU
        cpu_box = QVBoxLayout()
        cpu_box.setSpacing(2)
        self.lbl_cpu_badge = QLabel("CPU")
        self.lbl_cpu_badge.setProperty("class", "badge-label")
        self.lbl_cpu_val = QLabel("0% --°C")
        self.lbl_cpu_val.setProperty("class", "metric-value")
        cpu_box.addWidget(self.lbl_cpu_badge, alignment=Qt.AlignmentFlag.AlignCenter)
        cpu_box.addWidget(self.lbl_cpu_val, alignment=Qt.AlignmentFlag.AlignCenter)
        container_layout.addLayout(cpu_box)

        # Divisor 1
        div1 = QFrame()
        div1.setProperty("class", "divider")
        div1.setFrameShape(QFrame.Shape.VLine)
        container_layout.addWidget(div1)

        # Coluna GPU
        gpu_box = QVBoxLayout()
        gpu_box.setSpacing(2)
        self.lbl_gpu_badge = QLabel("GPU")
        self.lbl_gpu_badge.setProperty("class", "badge-label")
        self.lbl_gpu_val = QLabel("0% --°C")
        self.lbl_gpu_val.setProperty("class", "metric-value")
        gpu_box.addWidget(self.lbl_gpu_badge, alignment=Qt.AlignmentFlag.AlignCenter)
        gpu_box.addWidget(self.lbl_gpu_val, alignment=Qt.AlignmentFlag.AlignCenter)
        container_layout.addLayout(gpu_box)

        # Divisor 2
        div2 = QFrame()
        div2.setProperty("class", "divider")
        div2.setFrameShape(QFrame.Shape.VLine)
        container_layout.addWidget(div2)

        # Coluna RAM
        ram_box = QVBoxLayout()
        ram_box.setSpacing(2)
        self.lbl_ram_badge = QLabel("RAM")
        self.lbl_ram_badge.setProperty("class", "badge-label")
        self.lbl_ram_val = QLabel("0%")
        self.lbl_ram_val.setProperty("class", "metric-value")
        ram_box.addWidget(self.lbl_ram_badge, alignment=Qt.AlignmentFlag.AlignCenter)
        ram_box.addWidget(self.lbl_ram_val, alignment=Qt.AlignmentFlag.AlignCenter)
        container_layout.addLayout(ram_box)

        main_layout.addWidget(self.container)

    def apply_style(self) -> None:
        self.setStyleSheet(get_hud_stylesheet(self.locked))
        if self.locked:
            self.setCursor(QCursor(Qt.CursorShape.ArrowCursor))
        else:
            self.setCursor(QCursor(Qt.CursorShape.SizeAllCursor))

    def showEvent(self, event) -> None:
        super().showEvent(event)
        # Aplica estilos estendidos do Windows após criação da janela nativa
        hwnd = int(self.winId())
        set_tool_window(hwnd)
        set_click_through(hwnd, self.locked)

    def set_locked(self, locked: bool) -> None:
        self.locked = locked
        hwnd = int(self.winId())
        set_click_through(hwnd, self.locked)
        self.apply_style()
        self.lock_state_changed.emit(self.locked)

    def toggle_lock(self) -> bool:
        self.set_locked(not self.locked)
        return self.locked

    def update_metrics(self, m: HardwareMetrics) -> None:
        # Formata CPU
        cpu_temp_str = f" {int(m.cpu_temp)}°C" if m.cpu_temp is not None else ""
        self.lbl_cpu_val.setText(f"{int(m.cpu_usage)}%{cpu_temp_str}")
        self._apply_thermal_color(self.lbl_cpu_val, m.cpu_temp if m.cpu_temp else m.cpu_usage)

        # Formata GPU
        gpu_temp_str = f" {int(m.gpu_temp)}°C" if m.gpu_temp > 0 else ""
        self.lbl_gpu_val.setText(f"{int(m.gpu_usage)}%{gpu_temp_str}")
        self._apply_thermal_color(self.lbl_gpu_val, m.gpu_temp if m.gpu_temp > 0 else m.gpu_usage)

        # Formata RAM
        self.lbl_ram_val.setText(f"{int(m.ram_usage)}%")
        self._apply_thermal_color(self.lbl_ram_val, m.ram_usage)

    def _apply_thermal_color(self, label: QLabel, value: float) -> None:
        """Aplica verde, laranja ou vermelho conforme a temperatura ou uso."""
        if value >= 83.0:
            color = "#ff5252" # Crítico / Alerta
        elif value >= 72.0:
            color = "#ffab00" # Carga alta / Atenção
        else:
            color = "#00e676" # Normal / Saudável
        label.setStyleSheet(f"color: {color};")

    # Controles de arrastar quando destravado (Modo Ajuste)
    def mousePressEvent(self, event) -> None:
        if not self.locked and event.button() == Qt.MouseButton.LeftButton:
            self._drag_start_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event) -> None:
        if not self.locked and self._drag_start_pos is not None:
            new_pos = event.globalPosition().toPoint() - self._drag_start_pos
            self.move(new_pos)
            self.position_changed.emit(new_pos.x(), new_pos.y())
            event.accept()

    def mouseReleaseEvent(self, event) -> None:
        self._drag_start_pos = None
        event.accept()
