import logging
from typing import Tuple

logger = logging.getLogger(__name__)

class GpuNvmlReader:
    """Leitor de métricas de GPU NVIDIA via NVML (nvidia-ml-py / pynvml)."""

    def __init__(self, device_index: int = 0):
        self.device_index = device_index
        self.is_available = False
        self.handle = None
        self._init_nvml()

    def _init_nvml(self) -> None:
        try:
            import pynvml
            self.pynvml = pynvml
            self.pynvml.nvmlInit()
            device_count = self.pynvml.nvmlDeviceGetCount()
            if device_count > self.device_index:
                self.handle = self.pynvml.nvmlDeviceGetHandleByIndex(self.device_index)
                self.is_available = True
                device_name = self.pynvml.nvmlDeviceGetName(self.handle)
                if isinstance(device_name, bytes):
                    device_name = device_name.decode("utf-8")
                logger.info(f"NVML inicializado com sucesso para GPU: {device_name}")
        except Exception as e:
            logger.warning(f"NVML não disponível ou falha ao inicializar: {e}")
            self.is_available = False

    def get_metrics(self) -> Tuple[float, float, float, float]:
        """
        Retorna (gpu_usage_pct, gpu_temp_c, vram_used_gb, vram_total_gb).
        """
        if not self.is_available or self.handle is None:
            return 0.0, 0.0, 0.0, 0.0

        try:
            # Taxa de utilização da GPU
            rates = self.pynvml.nvmlDeviceGetUtilizationRates(self.handle)
            gpu_usage = float(rates.gpu)

            # Temperatura da GPU em Celsius
            temp = float(self.pynvml.nvmlDeviceGetTemperature(
                self.handle, self.pynvml.NVML_TEMPERATURE_GPU
            ))

            # Memória VRAM
            mem_info = self.pynvml.nvmlDeviceGetMemoryInfo(self.handle)
            vram_used_gb = round(mem_info.used / (1024 ** 3), 2)
            vram_total_gb = round(mem_info.total / (1024 ** 3), 2)

            return gpu_usage, temp, vram_used_gb, vram_total_gb
        except Exception as e:
            logger.debug(f"Erro ao ler métricas NVML: {e}")
            return 0.0, 0.0, 0.0, 0.0

    def shutdown(self) -> None:
        if self.is_available and hasattr(self, "pynvml"):
            try:
                self.pynvml.nvmlShutdown()
            except Exception:
                pass
            self.is_available = False
