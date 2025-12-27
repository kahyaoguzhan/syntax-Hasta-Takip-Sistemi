"""
Seri Port Yöneticisi - Basit
Sadece Arduino ile iletişim, karmaşık işlemler yok
"""

import serial
import serial.tools.list_ports
from PyQt6.QtCore import QThread, pyqtSignal
import time


class SerialManager(QThread):
    """Arduino seri port bağlantısı"""
    
    # Signals - UI'a veri göndermek için
    data_received = pyqtSignal(str)  # Ham veri
    status_changed = pyqtSignal(bool, str)  # Bağlantı durumu
    error_occurred = pyqtSignal(str)  # Hata mesajları
    
    def __init__(self, port, baud_rate=9600):
        super().__init__()
        self.port = port
        self.baud_rate = baud_rate
        self.serial_conn = None
        self.running = False
        
    def connect(self):
        """Seri porta bağlan"""
        try:
            self.serial_conn = serial.Serial(
                port=self.port,
                baudrate=self.baud_rate,
                timeout=1.0
            )
            time.sleep(0.5)  # Arduino sıfırlanmasını bekle
            self.status_changed.emit(True, f"{self.port} bağlandı")
            return True
        except Exception as e:
            self.error_occurred.emit(f"Bağlantı hatası: {str(e)}")
            return False
            
    def disconnect(self):
        """Bağlantıyı kes"""
        self.running = False
        if self.serial_conn and self.serial_conn.is_open:
            self.serial_conn.close()
            self.status_changed.emit(False, "Bağlantı kesildi")
            
    def send_command(self, command):
        """
        Arduino'ya komut gönder
        command: "1", "2" veya "3"
        """
        if self.serial_conn and self.serial_conn.is_open:
            try:
                self.serial_conn.write(f"{command}\n".encode('utf-8'))
                self.status_changed.emit(True, f"Komut '{command}' gönderildi")
                return True
            except Exception as e:
                self.error_occurred.emit(f"Komut gönderme hatası: {str(e)}")
                return False
        else:
            self.error_occurred.emit("Bağlantı yok!")
            return False
            
    def run(self):
        """Thread ana döngüsü - veri okuma"""
        self.running = True
        
        if not self.connect():
            return
            
        while self.running:
            try:
                if self.serial_conn and self.serial_conn.is_open:
                    if self.serial_conn.in_waiting > 0:
                        # Veri var, oku
                        data = self.serial_conn.readline().decode('utf-8').strip()
                        if data:
                            self.data_received.emit(data)
                            
                time.sleep(0.01)  # CPU yükünü azalt
                
            except Exception as e:
                self.error_occurred.emit(f"Okuma hatası: {str(e)}")
                time.sleep(0.1)


def get_available_ports():
    """Mevcut seri portları listele"""
    ports = serial.tools.list_ports.comports()
    return [port.device for port in ports]
