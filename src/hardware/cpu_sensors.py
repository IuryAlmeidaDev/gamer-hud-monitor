import logging
import psutil
from typing import Optional, Tuple

logger = logging.getLogger(__name__)

class CpuSensorReader:
    """Leitor de métricas de CPU e Memória RAM usando psutil e sondas de temperatura."""

    def __init__(self):
        # Primeira chamada para calibrar o psutil.cpu_percent
        psutil.cpu_percent(interval=None)

    def get_metrics(self) -> Tuple[float, Optional[float], float, float, float]:
        """
        Retorna (cpu_usage_pct, cpu_temp_c, ram_usage_pct, ram_used_gb, ram_total_gb).
        """
        # CPU %
        cpu_pct = float(psutil.cpu_percent(interval=None))

        # RAM
        mem = psutil.virtual_memory()
        ram_pct = float(mem.percent)
        ram_used_gb = round(mem.used / (1024 ** 3), 2)
        ram_total_gb = round(mem.total / (1024 ** 3), 2)

        # CPU Temp (tenta ler com fallback seguro)
        cpu_temp = self._read_cpu_temperature()

        return cpu_pct, cpu_temp, ram_pct, ram_used_gb, ram_total_gb

    def _read_cpu_temperature(self) -> Optional[float]:
        """
        Tenta sondar a temperatura da CPU de maneira não-bloqueante e segura.
        Retorna None se os sensores da placa-mãe exigirem permissões especiais ou não estiverem ativos.
        """
        try:
            # Em Linux/alguns Windows com suporte nativo
            if hasattr(psutil, "sensors_temperatures"):
                temps = psutil.sensors_temperatures()
                if temps:
                    for name in ["coretemp", "k10temp", "cpu_thermal", "acpitz", "zenpower"]:
                        if name in temps and len(temps[name]) > 0:
                            return round(float(temps[name][0].current), 1)
                    # Pega qualquer sensor disponível
                    for sensor_list in temps.values():
                        if sensor_list:
                            return round(float(sensor_list[0].current), 1)
        except Exception:
            pass

        return None
