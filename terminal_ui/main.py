import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QComboBox,
                             QGroupBox, QStatusBar, QGridLayout, QScrollArea, QTextEdit)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
import pyqtgraph as pg
import config
from styles import get_stylesheet, Colors
from serial_manager import SerialManager, get_available_ports
from data_logger import DataLogger
from signal_processor import process_all_modules, save_results_to_file
from gemini_api_handler import GeminiWorker, get_latest_analysis_json, create_prompt_from_json, get_all_analysis_json_files
from historical_analysis import create_prompt_from_files


class TerminalUI(QMainWindow):
    """Ana terminal arayüzü"""
    
    def __init__(self):
        super().__init__()
        self.serial_manager = None  # Seri port yöneticisi
        self.data_logger = DataLogger()  # Veri kaydedici
        self.modules_completed = {'A': False, 'B': False, 'C': False}  # Modül tamamlanma takibi
        self.gemini_worker = None  # Gemini API worker thread
        self.init_ui()
        
    def init_ui(self):
        """Arayüzü oluştur"""
        self.setWindowTitle("Biyodijital Motor Analiz Terminali")
        self.setMinimumSize(1200, 800)
        
        # Ekran boyutuna göre ayarla
        screen = self.screen().geometry()
        self.setGeometry(
            int(screen.width() * 0.05),
            int(screen.height() * 0.05),
            int(screen.width() * 0.9),
            int(screen.height() * 0.9)
        )
        
        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        central_widget = QWidget()
        scroll.setWidget(central_widget)
        self.setCentralWidget(scroll)
        
        # Ana layout - Yatay bölme (Sol: Modüller, Sağ: AI Analiz)
        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Sol taraf - Modül panelleri
        left_widget = QWidget()
        left_layout = QVBoxLayout()
        left_widget.setLayout(left_layout)
        
        # Kontrol paneli
        left_layout.addWidget(self.create_control_panel())
        
        # Modüller
        left_layout.addWidget(self.create_module_a())
        left_layout.addWidget(self.create_module_b())
        left_layout.addWidget(self.create_module_c())
        
        # Sağ taraf - AI Analiz paneli
        right_widget = self.create_ai_analysis_panel()
        
        # Layout'a ekle (70% sol, 30% sağ)
        main_layout.addWidget(left_widget, 7)
        main_layout.addWidget(right_widget, 3)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Hazır")
        
        # Dark theme
        self.setStyleSheet(get_stylesheet())
        
    def create_control_panel(self):
        """Kontrol paneli oluştur"""
        group = QGroupBox("Kontrol Paneli")
        layout = QVBoxLayout()
        
        # Bağlantı satırı
        conn_layout = QHBoxLayout()
        
        conn_layout.addWidget(QLabel("Seri Port:"))
        
        self.port_combo = QComboBox()
        ports = get_available_ports()
        if ports:
            self.port_combo.addItems(ports)
        else:
            self.port_combo.addItem("Port bulunamadı")
        conn_layout.addWidget(self.port_combo)
        
        self.connect_btn = QPushButton("Bağlan")
        self.connect_btn.clicked.connect(self.on_connect)
        conn_layout.addWidget(self.connect_btn)
        
        conn_layout.addStretch()
        
        self.status_label = QLabel("● Bağlı Değil")
        self.status_label.setStyleSheet("color: #d9534f; font-weight: bold;")
        conn_layout.addWidget(self.status_label)
        
        layout.addLayout(conn_layout)
        
        # Modül kontrolleri
        module_group = QGroupBox("Modül Kontrolleri")
        module_layout = QGridLayout()
        
        # Modül A
        module_layout.addWidget(QLabel("Modül A (Tremor):"), 0, 0)
        self.mod_a_start = QPushButton("Başlat (1)")
        self.mod_a_start.setObjectName("startButton")
        self.mod_a_start.clicked.connect(lambda: self.on_start_module('A'))
        module_layout.addWidget(self.mod_a_start, 0, 1)
        
        self.mod_a_stop = QPushButton("Durdur")
        self.mod_a_stop.setObjectName("stopButton")
        self.mod_a_stop.setEnabled(False)
        self.mod_a_stop.clicked.connect(lambda: self.on_stop_module('A'))
        module_layout.addWidget(self.mod_a_stop, 0, 2)
        
        self.mod_a_status = QLabel("● Durduruldu")
        self.mod_a_status.setStyleSheet("color: #999999;")
        module_layout.addWidget(self.mod_a_status, 0, 3)
        
        # Modül B
        module_layout.addWidget(QLabel("Modül B (Bradikinezi):"), 1, 0)
        self.mod_b_start = QPushButton("Başlat (2)")
        self.mod_b_start.setObjectName("startButton")
        self.mod_b_start.clicked.connect(lambda: self.on_start_module('B'))
        module_layout.addWidget(self.mod_b_start, 1, 1)
        
        self.mod_b_stop = QPushButton("Durdur")
        self.mod_b_stop.setObjectName("stopButton")
        self.mod_b_stop.setEnabled(False)
        self.mod_b_stop.clicked.connect(lambda: self.on_stop_module('B'))
        module_layout.addWidget(self.mod_b_stop, 1, 2)
        
        self.mod_b_status = QLabel("● Durduruldu")
        self.mod_b_status.setStyleSheet("color: #999999;")
        module_layout.addWidget(self.mod_b_status, 1, 3)
        
        # Modül C
        module_layout.addWidget(QLabel("Modül C (Koordinasyon):"), 2, 0)
        self.mod_c_start = QPushButton("Başlat (3)")
        self.mod_c_start.setObjectName("startButton")
        self.mod_c_start.clicked.connect(lambda: self.on_start_module('C'))
        module_layout.addWidget(self.mod_c_start, 2, 1)
        
        self.mod_c_stop = QPushButton("Durdur")
        self.mod_c_stop.setObjectName("stopButton")
        self.mod_c_stop.setEnabled(False)
        self.mod_c_stop.clicked.connect(lambda: self.on_stop_module('C'))
        module_layout.addWidget(self.mod_c_stop, 2, 2)
        
        self.mod_c_status = QLabel("● Durduruldu")
        self.mod_c_status.setStyleSheet("color: #999999;")
        module_layout.addWidget(self.mod_c_status, 2, 3)
        
        module_group.setLayout(module_layout)
        layout.addWidget(module_group)
        
        group.setLayout(layout)
        return group
    
    def create_ai_analysis_panel(self):
        """AI Analiz sonuçları paneli"""
        group = QGroupBox("AI Analiz Sonuçları")
        group.setMinimumWidth(400)
        layout = QVBoxLayout()
        
        # Kontrol butonları
        control_layout = QHBoxLayout()
        
        self.ai_run_btn = QPushButton("Son Analizi Çalıştır")
        self.ai_run_btn.setObjectName("startButton")
        self.ai_run_btn.clicked.connect(self.on_run_ai_analysis)
        control_layout.addWidget(self.ai_run_btn)
        
        self.ai_historical_btn = QPushButton("Geçmiş Analizleri İncele")
        self.ai_historical_btn.setObjectName("startButton")
        self.ai_historical_btn.clicked.connect(self.on_run_historical_analysis)
        control_layout.addWidget(self.ai_historical_btn)
        
        control_layout.addStretch()
        
        self.ai_status_label = QLabel("● Hazır")
        self.ai_status_label.setStyleSheet("color: #999999; font-weight: bold;")
        control_layout.addWidget(self.ai_status_label)
        
        layout.addLayout(control_layout)
        
        # Sonuç alanı - Scroll edilebilir metin
        self.ai_result_text = QTextEdit()
        self.ai_result_text.setReadOnly(True)
        self.ai_result_text.setPlaceholderText(
            "Gemini AI analiz sonuçları burada görünecek...\n\n"
            "Tüm modülleri tamamladıktan sonra analiz otomatik çalışacak."
        )
        
        # Monospace font - daha iyi okunabilirlik
        font = QFont("Consolas", 10)
        self.ai_result_text.setFont(font)
        
        layout.addWidget(self.ai_result_text)
        
        group.setLayout(layout)
        return group
        
    def create_module_a(self):
        """Modül A - Tremor"""
        group = QGroupBox("MODÜL A: Tremor Analizi (LDR Sensör)")
        group.setMinimumHeight(300)
        layout = QVBoxLayout()
        
        # Grafik
        self.mod_a_plot = pg.PlotWidget(title="LDR Sinyal")
        self.mod_a_plot.setBackground(Colors.BG_SECONDARY)
        self.mod_a_plot.setLabel('left', 'LDR Değeri')
        self.mod_a_plot.setLabel('bottom', 'Zaman (s)')
        self.mod_a_plot.showGrid(x=True, y=True, alpha=0.3)
        
        # Grafik eğrisi
        self.mod_a_curve = self.mod_a_plot.plot(
            pen=pg.mkPen(Colors.ACCENT, width=2)
        )
        
        # Veri bufferleri
        self.mod_a_time_data = []
        self.mod_a_ldr_data = []
        
        layout.addWidget(self.mod_a_plot)
        
        group.setLayout(layout)
        return group
        
    def create_module_b(self):
        """Modül B - Bradikinezi"""
        group = QGroupBox("MODÜL B: Bradikinezi Analizi (Mesafe Sensörü)")
        group.setMinimumHeight(300)
        layout = QVBoxLayout()
        
        # Grafik
        self.mod_b_plot = pg.PlotWidget(title="Mesafe Ölçümü")
        self.mod_b_plot.setBackground(Colors.BG_SECONDARY)
        self.mod_b_plot.setLabel('left', 'Mesafe (mm)')
        self.mod_b_plot.setLabel('bottom', 'Zaman (s)')
        self.mod_b_plot.showGrid(x=True, y=True, alpha=0.3)
        
        # Grafik eğrisi
        self.mod_b_curve = self.mod_b_plot.plot(
            pen=pg.mkPen('#00ff88', width=2)  # Yeşil renk
        )
        
        # Veri bufferleri
        self.mod_b_time_data = []
        self.mod_b_distance_data = []
        
        layout.addWidget(self.mod_b_plot)
        
        group.setLayout(layout)
        return group
        
    def create_module_c(self):
        """Modül C - Koordinasyon"""
        group = QGroupBox("MODÜL C: Koordinasyon Testi (Reaksiyon Zamanı)")
        group.setMinimumHeight(300)
        layout = QVBoxLayout()
        
        # İstatistikler
        stats_layout = QHBoxLayout()
        self.mod_c_total_label = QLabel("Toplam Basış: 0/20")
        self.mod_c_avg_label = QLabel("Ortalama: - ms")
        stats_layout.addWidget(self.mod_c_total_label)
        stats_layout.addWidget(self.mod_c_avg_label)
        stats_layout.addStretch()
        layout.addLayout(stats_layout)
        
        # Grafik
        self.mod_c_plot = pg.PlotWidget(title="Reaksiyon Zamanları")
        self.mod_c_plot.setBackground(Colors.BG_SECONDARY)
        self.mod_c_plot.setLabel('left', 'Reaksiyon Zamanı (ms)')
        self.mod_c_plot.setLabel('bottom', 'Deneme #')
        self.mod_c_plot.showGrid(x=True, y=True, alpha=0.3)
        
        # Grafik eğrisi - çubuk grafik gibi göster
        self.mod_c_curve = self.mod_c_plot.plot(
            pen=None,
            symbol='o',
            symbolSize=10,
            symbolBrush='#ffaa00'  # Turuncu renk
        )
        
        # Veri bufferleri
        self.mod_c_trial_data = []
        self.mod_c_reaction_data = []
        
        layout.addWidget(self.mod_c_plot)
        
        group.setLayout(layout)
        return group
        
    def on_connect(self):
        """Bağlan/Bağlantıyı kes"""
        if self.connect_btn.text() == "Bağlan":
            # Bağlan
            port = self.port_combo.currentText()
            
            if port == "Port bulunamadı":
                self.status_bar.showMessage("Geçerli bir port seçin!")
                return
                
            # Serial manager oluştur ve başlat
            self.serial_manager = SerialManager(port, config.BAUD_RATE)
            
            # Signalleri bağla
            self.serial_manager.status_changed.connect(self.on_serial_status)
            self.serial_manager.error_occurred.connect(self.on_serial_error)
            self.serial_manager.data_received.connect(self.on_data_received)
            
            # Thread'i başlat
            self.serial_manager.start()
            
            self.connect_btn.setText("Bağlantıyı Kes")
            self.status_label.setText("● Bağlanıyor...")
            self.status_label.setStyleSheet("color: #ffaa00; font-weight: bold;")
            
        else:
            # Bağlantıyı kes
            if self.serial_manager:
                self.serial_manager.disconnect()
                self.serial_manager.wait()  # Thread'in bitmesini bekle
                self.serial_manager = None
                
            self.connect_btn.setText("Bağlan")
            self.status_label.setText("● Bağlı Değil")
            self.status_label.setStyleSheet("color: #d9534f; font-weight: bold;")
            self.status_bar.showMessage("Bağlantı kesildi")
            
            # Modül butonlarını devre dışı bırak
            self.mod_a_start.setEnabled(False)
            self.mod_b_start.setEnabled(False)
            self.mod_c_start.setEnabled(False)
            
    def on_serial_status(self, connected, message):
        """Seri port durumu değişti"""
        self.status_bar.showMessage(message)
        if connected:
            self.status_label.setText("● Bağlı")
            self.status_label.setStyleSheet("color: #00a86b; font-weight: bold;")
            # Modül butonlarını aktif et
            self.mod_a_start.setEnabled(True)
            self.mod_b_start.setEnabled(True)
            self.mod_c_start.setEnabled(True)
        else:
            self.status_label.setText("● Bağlı Değil")
            self.status_label.setStyleSheet("color: #d9534f; font-weight: bold;")
            
    def on_serial_error(self, error_message):
        """Seri port hatası"""
        self.status_bar.showMessage(f"HATA: {error_message}")
        
    def on_data_received(self, data):
        """Arduino'dan veri geldi"""
        print(f"Arduino: {data}")
        
        # Test bitişini kontrol et
        # Arduino mesajları:
        # ">>> System 1 Finished (10 seconds elapsed) <<<"
        # ">>> System 2 Finished (10 seconds elapsed) <<<"
        # ">>> GAME OVER! Total 20 correct presses completed! <<<"
        
        if "System 1 Finished" in data or "FINISHED!" in data:
            # Modül A testi bitti
            self.auto_stop_module('A')
            return
        elif "System 2 Finished" in data:
            # Modül B testi bitti
            self.auto_stop_module('B')
            return
        elif "GAME OVER" in data:
            # Modül C testi bitti
            self.auto_stop_module('C')
            return
        
        # Veriyi parse et
        try:
            if '|' in data:
                parts = data.split('|')
                
                # MODÜL A: "1138 ms | 532 | 132" (3 parça)
                if len(parts) >= 3:
                    # İlk kısım: zaman (ms)
                    time_str = parts[0].strip().replace('ms', '').strip()
                    time_ms = float(time_str)
                    time_s = time_ms / 1000.0
                    
                    # İkinci kısım: LDR değeri
                    ldr_value = int(parts[1].strip())
                    
                    # Modül A grafiğine ekle
                    self.mod_a_time_data.append(time_s)
                    self.mod_a_ldr_data.append(ldr_value)
                    self.mod_a_curve.setData(self.mod_a_time_data, self.mod_a_ldr_data)
                    
                    # CSV'ye kaydet (sadece zaman ve LDR)
                    self.data_logger.log_module_a(time_s, ldr_value)
                
                # MODÜL B: "500 ms | 145.3 mm" (2 parça)
                elif len(parts) == 2 and 'mm' in parts[1]:
                    # İlk kısım: zaman (ms)
                    time_str = parts[0].strip().replace('ms', '').strip()
                    time_ms = float(time_str)
                    time_s = time_ms / 1000.0
                    
                    # İkinci kısım: mesafe (mm)
                    distance_str = parts[1].strip().replace('mm', '').strip()
                    distance = float(distance_str)
                    
                    # Modül B grafiğine ekle
                    self.mod_b_time_data.append(time_s)
                    self.mod_b_distance_data.append(distance)
                    self.mod_b_curve.setData(self.mod_b_time_data, self.mod_b_distance_data)
                    
                    # CSV'ye kaydet
                    self.data_logger.log_module_b(time_s, distance)
            
            # MODÜL C: "Correct! Reaction Time: 879 ms | Presses: 3/20"
            if 'Reaction Time:' in data and 'Presses:' in data:
                parts = data.split('|')
                if len(parts) >= 2:
                    # İlk kısım: "Correct! Reaction Time: 879 ms"
                    reaction_part = parts[0].strip()
                    if 'Reaction Time:' in reaction_part:
                        reaction_str = reaction_part.split('Reaction Time:')[1].strip()
                        reaction_time = float(reaction_str.replace('ms', '').strip())
                        
                        # İkinci kısım: "Presses: 3/20"
                        presses_part = parts[1].strip()
                        if 'Presses:' in presses_part:
                            presses_str = presses_part.split('Presses:')[1].strip()
                            trial_num = int(presses_str.split('/')[0].strip())
                            
                            # Modül C grafiğine ekle
                            self.mod_c_trial_data.append(trial_num)
                            self.mod_c_reaction_data.append(reaction_time)
                            self.mod_c_curve.setData(self.mod_c_trial_data, self.mod_c_reaction_data)
                            
                            # İstatistikleri güncelle
                            avg_reaction = sum(self.mod_c_reaction_data) / len(self.mod_c_reaction_data)
                            self.mod_c_total_label.setText(f"Toplam Basış: {trial_num}/20")
                            self.mod_c_avg_label.setText(f"Ortalama: {avg_reaction:.0f} ms")
                            
                            # CSV'ye kaydet
                            self.data_logger.log_module_c(trial_num, reaction_time)
                    
        except Exception as e:
            # Parse hatası - sadece devam et
            pass
    
    def auto_stop_module(self, module):
        """Test bittiğinde otomatik durdur"""
        files = self.data_logger.get_files()
        file_path = files.get(module, '')
        
        # Mark module as completed
        self.modules_completed[module] = True
        
        self.status_bar.showMessage(f"✓ Modül {module} tamamlandı! Veri kaydedildi: {file_path}")
        
        if module == 'A':
            self.mod_a_start.setEnabled(True)
            self.mod_a_stop.setEnabled(False)
            self.mod_a_status.setText("● Tamamlandı")
            self.mod_a_status.setStyleSheet("color: #00d4ff; font-weight: bold;")
        elif module == 'B':
            self.mod_b_start.setEnabled(True)
            self.mod_b_stop.setEnabled(False)
            self.mod_b_status.setText("● Tamamlandı")
            self.mod_b_status.setStyleSheet("color: #00d4ff; font-weight: bold;")
        elif module == 'C':
            self.mod_c_start.setEnabled(True)
            self.mod_c_stop.setEnabled(False)
            self.mod_c_status.setText("● Tamamlandı")
            self.mod_c_status.setStyleSheet("color: #00d4ff; font-weight: bold;")
        
        # Check if all modules are completed
        if all(self.modules_completed.values()):
            self.run_signal_processing()
    
    def run_signal_processing(self):
        """Tüm modüller tamamlandığında sinyal işleme analizi yap"""
        self.status_bar.showMessage(">> Sinyal işleme analizi başlatılıyor...")
        
        try:
            # Get CSV file paths
            files = self.data_logger.get_files()
            
            # Run analysis
            results = process_all_modules(
                files['A'],  # module_A CSV
                files['B'],  # module_B CSV  
                files['C']   # module_C CSV
            )
            
            # Save results to JSON
            saved_file = save_results_to_file(results)
            
            # Show success message
            self.status_bar.showMessage(f">> Analiz tamamlandı! Sonuçlar: {saved_file}")
            
            # Otomatik AI analizi başlat
            self.on_run_ai_analysis()
            
            # Reset completion tracking for next session
            self.modules_completed = {'A': False, 'B': False, 'C': False}
            
        except Exception as e:
            self.status_bar.showMessage(f"xx Analiz hatası: {str(e)}")
            
    def on_start_module(self, module):
        """Modül başlat - Arduino'ya komut gönder"""
        if not self.serial_manager:
            self.status_bar.showMessage("Önce Arduino'ya bağlanın!")
            return
            
        # Komut belirle
        command = None
        if module == 'A':
            command = '1'
        elif module == 'B':
            command = '2'
        elif module == 'C':
            command = '3'
            
        # Arduino'ya gönder
        if command and self.serial_manager.send_command(command):
            # Reset completion status
            self.modules_completed[module] = False
            
            self.status_bar.showMessage(f"Modül {module} başlatıldı - Komut '{command}' gönderildi")
            
            if module == 'A':
                # Veriyi temizle
                self.mod_a_time_data.clear()
                self.mod_a_ldr_data.clear()
                self.mod_a_curve.setData([], [])
                
                self.mod_a_start.setEnabled(False)
                self.mod_a_stop.setEnabled(True)
                self.mod_a_status.setText("● Çalışıyor")
                self.mod_a_status.setStyleSheet("color: #00a86b; font-weight: bold;")
            elif module == 'B':
                # Veriyi temizle
                self.mod_b_time_data.clear()
                self.mod_b_distance_data.clear()
                self.mod_b_curve.setData([], [])
                
                self.mod_b_start.setEnabled(False)
                self.mod_b_stop.setEnabled(True)
                self.mod_b_status.setText("● Çalışıyor")
                self.mod_b_status.setStyleSheet("color: #00a86b; font-weight: bold;")
            elif module == 'C':
                # Veriyi temizle
                self.mod_c_trial_data.clear()
                self.mod_c_reaction_data.clear()
                self.mod_c_curve.setData([], [])
                self.mod_c_total_label.setText("Toplam Basış: 0/20")
                self.mod_c_avg_label.setText("Ortalama: - ms")
                
                self.mod_c_start.setEnabled(False)
                self.mod_c_stop.setEnabled(True)
                self.mod_c_status.setText("● Çalışıyor")
                self.mod_c_status.setStyleSheet("color: #00a86b; font-weight: bold;")
            
    def on_stop_module(self, module):
        """Modül durdur"""
        self.status_bar.showMessage(f"Modül {module} durduruldu")
        
        if module == 'A':
            self.mod_a_start.setEnabled(True)
            self.mod_a_stop.setEnabled(False)
            self.mod_a_status.setText("● Durduruldu")
            self.mod_a_status.setStyleSheet("color: #999999;")
        elif module == 'B':
            self.mod_b_start.setEnabled(True)
            self.mod_b_stop.setEnabled(False)
            self.mod_b_status.setText("● Durduruldu")
            self.mod_b_status.setStyleSheet("color: #999999;")
        elif module == 'C':
            self.mod_c_start.setEnabled(True)
            self.mod_c_stop.setEnabled(False)
            self.mod_c_status.setText("● Durduruldu")
            self.mod_c_status.setStyleSheet("color: #999999;")
    
    def on_run_ai_analysis(self):
        """AI analizini çalıştır"""
        # En yeni JSON dosyasını bul
        json_file = get_latest_analysis_json()
        
        if not json_file:
            self.ai_status_label.setText("● Hata")
            self.ai_status_label.setStyleSheet("color: #d9534f; font-weight: bold;")
            self.ai_result_text.setText(
                "HATA: analysis_results klasöründe analiz sonucu bulunamadı.\n"
                "Önce tüm modülleri tamamlayın."
            )
            return
        
        # JSON'dan prompt oluştur
        try:
            prompt_text = create_prompt_from_json(json_file)
            if not prompt_text:
                raise Exception("Prompt oluşturulamadı")
        except Exception as e:
            self.ai_result_text.setText(f"Prompt oluşturma hatası: {str(e)}")
            return
        
        # UI'ı güncelle
        self.ai_status_label.setText("● Yükleniyor...")
        self.ai_status_label.setStyleSheet("color: #ffaa00; font-weight: bold;")
        self.ai_result_text.clear()
        self.ai_result_text.append(f"📄 Analiz dosyası: {os.path.basename(json_file)}\n")
        self.ai_result_text.append(f"📊 Prompt uzunluğu: {len(prompt_text)} karakter\n")
        self.ai_result_text.append("-" * 50 + "\n\n")
        self.ai_run_btn.setEnabled(False)
        
        # Worker thread oluştur ve başlat
        self.gemini_worker = GeminiWorker(prompt_text)
        self.gemini_worker.status_update.connect(self.on_ai_analysis_status)
        self.gemini_worker.chunk_received.connect(self.on_ai_analysis_chunk)
        self.gemini_worker.completed.connect(self.on_ai_analysis_complete)
        self.gemini_worker.error_occurred.connect(self.on_ai_analysis_error)
        self.gemini_worker.start()
    
    def on_ai_analysis_status(self, status_text):
        """AI analiz durumu güncellendi"""
        self.status_bar.showMessage(f"AI Analiz: {status_text}")
    
    def on_ai_analysis_chunk(self, text_chunk):
        """AI'dan chunk geldi - ekrana yaz"""
        self.ai_result_text.insertPlainText(text_chunk)
        # Auto-scroll to bottom
        scrollbar = self.ai_result_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def on_ai_analysis_complete(self):
        """AI analizi tamamlandı"""
        self.ai_status_label.setText("● Tamamlandı")
        self.ai_status_label.setStyleSheet("color: #00a86b; font-weight: bold;")
        self.ai_run_btn.setEnabled(True)
        self.ai_historical_btn.setEnabled(True)
        self.status_bar.showMessage("✓ AI Analizi tamamlandı!")
    
    def on_ai_analysis_error(self, error_text):
        """AI analizinde hata oluştu"""
        self.ai_status_label.setText("● Hata")
        self.ai_status_label.setStyleSheet("color: #d9534f; font-weight: bold;")
        self.ai_result_text.append(f"\n\n❌ {error_text}")
        self.ai_run_btn.setEnabled(True)
        self.ai_historical_btn.setEnabled(True)
        self.status_bar.showMessage("AI Analiz hatası!")
    
    def on_run_historical_analysis(self):
        """Geçmiş tüm analizleri toplu olarak çalıştır"""
        # Tüm JSON dosyalarını bul
        json_files = get_all_analysis_json_files()
        
        if not json_files:
            self.ai_status_label.setText("● Hata")
            self.ai_status_label.setStyleSheet("color: #d9534f; font-weight: bold;")
            self.ai_result_text.setText(
                "HATA: Geçmiş analiz bulunamadı.\n"
                "En az bir test tamamlayın."
            )
            return
        
        # Toplu prompt oluştur
        try:
            prompt_text = create_prompt_from_files(json_files)
            if not prompt_text:
                raise Exception("Prompt oluşturulamadı")
        except Exception as e:
            self.ai_result_text.setText(f"Prompt oluşturma hatası: {str(e)}")
            return
        
        # UI'ı güncelle
        self.ai_status_label.setText("● Yükleniyor...")
        self.ai_status_label.setStyleSheet("color: #ffaa00; font-weight: bold;")
        self.ai_result_text.clear()
        self.ai_result_text.append(f"📄 Toplam {len(json_files)} analiz bulundu\n")
        self.ai_result_text.append(f"📊 Prompt uzunluğu: {len(prompt_text)} karakter\n")
        self.ai_result_text.append("-" * 50 + "\n\n")
        self.ai_run_btn.setEnabled(False)
        self.ai_historical_btn.setEnabled(False)
        
        # Worker thread oluştur ve başlat
        self.gemini_worker = GeminiWorker(prompt_text)
        self.gemini_worker.status_update.connect(self.on_ai_analysis_status)
        self.gemini_worker.chunk_received.connect(self.on_ai_analysis_chunk)
        self.gemini_worker.completed.connect(self.on_ai_analysis_complete)
        self.gemini_worker.error_occurred.connect(self.on_ai_analysis_error)
        self.gemini_worker.start()


def main():
    app = QApplication(sys.argv)
    window = TerminalUI()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
