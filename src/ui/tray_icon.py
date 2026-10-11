from PyQt6.QtWidgets import QSystemTrayIcon, QMenu
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor, QAction
from PyQt6.QtCore import pyqtSignal, QObject

class TrayIconManager(QObject):
    """Gerencia o ícone e menu de contexto do HUD na bandeja do sistema (perto do relógio)."""
    toggle_lock_requested = pyqtSignal()
    reset_position_requested = pyqtSignal()
    quit_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(self._create_hud_icon())
        self.tray_icon.setToolTip("Gamer HUD Monitor (Pressione F9 para alternar modo)")

        self._build_menu()
        self.tray_icon.show()

    def _create_hud_icon(self) -> QIcon:
        """Cria um ícone moderno programático de 32x32 para a bandeja."""
        pixmap = QPixmap(32, 32)
        pixmap.fill(QColor(0, 0, 0, 0))

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Fundo arredondado escuro
        painter.setBrush(QColor(15, 23, 42))
        painter.setPen(QColor(0, 229, 255))
        painter.drawRoundedRect(2, 2, 28, 28, 6, 6)

        # Indicador central de status (verde)
        painter.setBrush(QColor(0, 230, 118))
        painter.setPen(QColor(0, 0, 0, 0))
        painter.drawEllipse(10, 10, 12, 12)

        painter.end()
        return QIcon(pixmap)

    def _build_menu(self) -> None:
        self.menu = QMenu()

        self.action_toggle_lock = QAction("Alternar Modo Jogo / Ajuste (F9)", self.menu)
        self.action_toggle_lock.triggered.connect(self.toggle_lock_requested.emit)
        self.menu.addAction(self.action_toggle_lock)

        self.action_reset_pos = QAction("Resetar Posição", self.menu)
        self.action_reset_pos.triggered.connect(self.reset_position_requested.emit)
        self.menu.addAction(self.action_reset_pos)

        self.menu.addSeparator()

        self.action_quit = QAction("Sair", self.menu)
        self.action_quit.triggered.connect(self.quit_requested.emit)
        self.menu.addAction(self.action_quit)

        self.tray_icon.setContextMenu(self.menu)

    def update_lock_state(self, locked: bool) -> None:
        mode_text = "Modo Jogo (Cliques passam direto)" if locked else "Modo Ajuste (Arrastável)"
        self.tray_icon.setToolTip(f"Gamer HUD Monitor - {mode_text}\n(Pressione F9 para alternar)")
