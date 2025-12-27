"""
Dark Mode Stil - Basitleştirilmiş
"""

def get_stylesheet():
    """Dark mode QSS stylesheet"""
    return """
    /* Ana Arka Plan */
    QMainWindow, QWidget {
        background-color: #1a1a1a;
        color: #e0e0e0;
        font-family: 'Segoe UI', Arial;
        font-size: 10pt;
    }
    
    /* Group Box */
    QGroupBox {
        background-color: #2d2d2d;
        border: 1px solid #404040;
        border-radius: 8px;
        margin-top: 12px;
        padding: 15px;
        font-weight: bold;
        color: #00d4ff;
    }
    
    QGroupBox::title {
        subcontrol-origin: margin;
        left: 10px;
        padding: 0 5px;
    }
    
    /* Buttons */
    QPushButton {
        background-color: #3d3d3d;
        border: 1px solid #555555;
        border-radius: 5px;
        padding: 8px 15px;
        color: #e0e0e0;
        font-weight: bold;
    }
    
    QPushButton:hover {
        background-color: #4d4d4d;
        border: 1px solid #00d4ff;
    }
    
    QPushButton:pressed {
        background-color: #2d2d2d;
    }
    
    QPushButton:disabled {
        background-color: #2a2a2a;
        color: #666666;
        border: 1px solid #333333;
    }
    
    QPushButton#startButton {
        background-color: #00a86b;
        border: 1px solid #00c97a;
    }
    
    QPushButton#startButton:hover {
        background-color: #00c97a;
    }
    
    QPushButton#stopButton {
        background-color: #d9534f;
        border: 1px solid #e74c3c;
    }
    
    QPushButton#stopButton:hover {
        background-color: #e74c3c;
    }
    
    /* ComboBox */
    QComboBox {
        background-color: #3d3d3d;
        border: 1px solid #555555;
        border-radius: 5px;
        padding: 5px 10px;
        color: #e0e0e0;
    }
    
    QComboBox:hover {
        border: 1px solid #00d4ff;
    }
    
    QComboBox::drop-down {
        border: none;
        padding-right: 10px;
    }
    
    /* Labels */
    QLabel {
        color: #e0e0e0;
        background: transparent;
    }
    
    /* Status Bar */
    QStatusBar {
        background-color: #252525;
        color: #b0b0b0;
        border-top: 1px solid #404040;
    }
    
    /* Scroll Area */
    QScrollArea {
        border: none;
        background-color: #1a1a1a;
    }
    
    /* Scroll Bar */
    QScrollBar:vertical {
        background-color: #2d2d2d;
        width: 12px;
        border-radius: 6px;
    }
    
    QScrollBar::handle:vertical {
        background-color: #555555;
        border-radius: 6px;
        min-height: 20px;
    }
    
    QScrollBar::handle:vertical:hover {
        background-color: #00d4ff;
    }
    """

# Renkler
class Colors:
    BG_PRIMARY = "#1a1a1a"
    BG_SECONDARY = "#2d2d2d"
    TEXT = "#e0e0e0"
    ACCENT = "#00d4ff"
    SUCCESS = "#00a86b"
    DANGER = "#d9534f"
