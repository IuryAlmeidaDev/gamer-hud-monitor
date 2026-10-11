import time
from dataclasses import dataclass
from typing import Optional
from PyQt6.QtCore import QThread, pyqtSignal

from src.hardware.gpu_nvml import GpuNvmlReader
from src.hardware.cpu_sensors import CpuSensorReader

@dataclass
class HardwareMetrics:
    cpu_usage: float
    cpu_temp: Optional[float]
    gpu_usage: float
    gpu_temp: float
    ram_usage: float
    ram_used_gb: float
    ram_total_gb: float
    vram_used_gb: float
    vram_total_gb: float

class HardwareCollector(QThread):
    """
    Worker em thread separada para coletar métricas de hardware a cada intervalo
    sem impactar os 60 FPS da interface gráfica do HUD.
    """
    metrics_ready = pyqtSignal(HardwareMetrics)

    def __init__(self, interval_ms: int = 1000):
        super().__init__()
        self.interval_ms = interval_ms
        self.running = True
        self.gpu_reader = GpuNvmlReader()
        self.cpu_reader = CpuSensorReader()

    def run(self) -> None:
        while self.running:
            cpu_pct, cpu_temp, ram_pct, ram_used, ram_total = self.cpu_reader.get_metrics()
            gpu_pct, gpu_temp, vram_used, vram_total = self.gpu_reader.get_metrics()

            metrics = HardwareMetrics(
                cpu_usage=round(cpu_pct, 1),
                cpu_temp=cpu_temp,
                gpu_usage=round(gpu_pct, 1),
                gpu_temp=round(gpu_temp, 1),
                ram_usage=round(ram_pct, 1),
                ram_used_gb=ram_used,
                ram_total_gb=ram_total,
                vram_used_gb=vram_used,
                vram_total_gb=vram_total,
            )

            self.metrics_ready.emit(metrics)

            # Dorme pelo intervalo configurado em fatias para resposta rápida a parada
            sleep_slices = max(1, self.interval_ms // 100)
            for _ in range(sleep_slices):
                if not self.running:
                    break
                time.sleep(0.1)

    def stop(self) -> None:
        self.running = False
        self.wait(2000)
        self.gpu_reader.shutdown()
