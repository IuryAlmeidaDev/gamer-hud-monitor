"""
Folha de estilos QSS para o Gamer HUD Monitor.
Design Dark Frosted Glass focado em máxima legibilidade em jogos e visual minimalista.
"""

def get_hud_stylesheet(locked: bool = True) -> str:
    border_color = "rgba(255, 255, 255, 0.12)" if locked else "rgba(0, 229, 255, 0.85)"
    border_glow = "none" if locked else "0 0 10px rgba(0, 229, 255, 0.4)"

    return f"""
    QWidget#HudContainer {{
        background-color: rgba(13, 17, 23, 0.82);
        border: 1.5px solid {border_color};
        border-radius: 12px;
    }}

    QLabel {{
        font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, 'Consolas', sans-serif;
        color: #ffffff;
    }}

    .badge-label {{
        font-size: 10px;
        font-weight: 800;
        letter-spacing: 1px;
        color: #8b949e;
    }}

    .metric-value {{
        font-family: 'Consolas', 'Segoe UI Variable Display', monospace;
        font-size: 13px;
        font-weight: 700;
        color: #f0f6fc;
    }}

    .temp-value {{
        font-family: 'Consolas', 'Segoe UI Variable Display', monospace;
        font-size: 12px;
        font-weight: 600;
    }}

    .status-good {{
        color: #00e676;
    }}

    .status-warm {{
        color: #ffab00;
    }}

    .status-hot {{
        color: #ff5252;
    }}

    .divider {{
        background-color: rgba(255, 255, 255, 0.08);
        width: 1px;
        max-width: 1px;
    }}

    .mode-tag {{
        font-size: 8px;
        font-weight: 700;
        padding: 1px 4px;
        border-radius: 4px;
        background-color: rgba(0, 229, 255, 0.2);
        color: #00e5ff;
    }}
    """
