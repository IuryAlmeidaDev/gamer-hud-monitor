import pytest
from src.hardware.gpu_nvml import GpuNvmlReader
from src.hardware.cpu_sensors import CpuSensorReader
from src.hardware.collector import HardwareMetrics

def test_cpu_sensor_reader():
    reader = CpuSensorReader()
    cpu_pct, cpu_temp, ram_pct, ram_used, ram_total = reader.get_metrics()
    assert 0.0 <= cpu_pct <= 100.0
    assert 0.0 <= ram_pct <= 100.0
    assert ram_used > 0.0
    assert ram_total > 0.0
    if cpu_temp is not None:
        assert 0.0 <= cpu_temp <= 125.0

def test_gpu_nvml_reader():
    reader = GpuNvmlReader()
    gpu_pct, gpu_temp, vram_used, vram_total = reader.get_metrics()
    assert isinstance(gpu_pct, float)
    assert isinstance(gpu_temp, float)
    assert 0.0 <= gpu_pct <= 100.0
    # On real NVIDIA hardware, temp should be > 0.0
    if reader.is_available:
        assert gpu_temp > 0.0
        assert vram_total > 0.0

def test_hardware_metrics_dataclass():
    metrics = HardwareMetrics(
        cpu_usage=25.5,
        cpu_temp=55.0,
        gpu_usage=78.2,
        gpu_temp=65.0,
        ram_usage=45.0,
        ram_used_gb=14.4,
        ram_total_gb=32.0,
        vram_used_gb=4.2,
        vram_total_gb=8.0,
    )
    assert metrics.cpu_usage == 25.5
    assert metrics.gpu_temp == 65.0
