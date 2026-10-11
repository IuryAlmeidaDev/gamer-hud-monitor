# 🎮 Gamer HUD Monitor

<div align="center">

![Python](https://img.shields.io/badge/Python-3.12-blue?style=for-the-badge&logo=python)
![PyQt6](https://img.shields.io/badge/GUI-PyQt6-41CD52?style=for-the-badge&logo=qt)
![NVIDIA](https://img.shields.io/badge/GPU-NVML%20RTX%20Supported-76B900?style=for-the-badge&logo=nvidia)
![Platform](https://img.shields.io/badge/OS-Windows%2010%2F11-0078D6?style=for-the-badge&logo=windows)
![Anti-Cheat Safe](https://img.shields.io/badge/Anti--Cheat-100%25%20Safe-brightgreen?style=for-the-badge)

**Mini monitor de hardware ultra-discreto, translúcido e elegante para desktop Windows, projetado para você acompanhar o desempenho em tempo real sem sair ou perder foco em qualquer jogo.**

</div>

---

## ✨ Recursos

- ⚡ **Zero Impacto no Jogo:** Consumo irrisório (< 35 MB de RAM e < 0.2% de CPU).
- 🎯 **Modo Click-Through Real (Win32 API):** Pressione `F9` para ativar o **Modo Jogo**. Seus cliques passam 100% direto através do widget. Atire, mire e jogue sem cliques acidentais!
- 🕹️ **Anti-Cheat Safe (100% Seguro):** Não injeta DLLs nem interfere no executável dos jogos (compatível com Vanguard, Easy Anti-Cheat, BattlEye, Ricochet).
- 🧊 **Estética Dark Frosted Glass:** Cápsula translúcida moderna com cantos arredondados e fontes de largura fixa que não oscilam.
- 🟢 **Código de Cores Térmicas Inteligente:**
  - 🟢 **Verde:** Temperatura / carga normal (< 72°C).
  - 🟡 **Âmbar:** Carga elevada (72°C a 82°C).
  - 🔴 **Vermelho Coral:** Alerta térmico (> 83°C).
- 💾 **Persistência Automática:** Arraste para qualquer canto da sua tela e o HUD lembrará a posição na próxima vez que abrir.
- 🔔 **Bandeja do Sistema (Tray Icon):** Ícone silencioso ao lado do relógio do Windows com menu de contexto para travar, destravar, resetar posição e sair.

---

## 🖥️ Métricas Monitoradas

| Hardware | Métrica | Tecnologia |
| :--- | :--- | :--- |
| **GPU** | Uso (%) e Temperatura (°C) | NVIDIA NVML (`pynvml` / `nvidia-ml-py`) |
| **CPU** | Uso (%) e Temperatura (°C) | `psutil` com detecção de sensores térmicos |
| **RAM** | Uso Percentual (%) | `psutil` |

---

## 🚀 Como Executar

### 1. Clonar o repositório
```bash
git clone https://github.com/IuryAlmeidaDev/gamer-hud-monitor.git
cd gamer-hud-monitor
```

### 2. Instalar dependências
```bash
pip install -r requirements.txt
```

### 3. Iniciar o HUD
```bash
python src/main.py
```

---

## ⌨️ Atalhos e Controles

- **`F9`**: Alterna instantaneamente entre:
  - **Modo Ajuste:** Borda ciano acesa. Você pode clicar e arrastar o HUD com o mouse para qualquer posição do seu monitor.
  - **Modo Jogo (Travado):** Borda sutil. A janela torna-se transparente ao mouse (`WS_EX_TRANSPARENT`), permitindo que todos os cliques e miras passem direto para o jogo.
- **Clique Direito no Ícone da Bandeja:** Menu rápido para alternar modo, resetar posição central e fechar o aplicativo.

---

## 🧪 Executando os Testes

Para rodar a suíte completa de testes automatizados:
```bash
python -m pytest tests/ -v
```

---

## 📄 Licença

Distribuído sob a licença MIT. Consulte `LICENSE` para obter mais informações.
