import sys
import os
import subprocess
import json
from PyQt5.QtGui import QPixmap, QIcon, QFont
from PyQt5.QtCore import Qt, QSettings, QStandardPaths
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, 
    QLineEdit, QLabel, QComboBox, QHBoxLayout, 
    QTableWidget, QTableWidgetItem, QMessageBox, QHeaderView, QSizePolicy, QDialog, QHBoxLayout
)
def run_as_root(command):
    subprocess.run(["sudo"] + command)

# Örnek kullanım
run_as_root(["chmod", "777", "/usr/bin/dnstic.py"])
if os.getuid() == 0:
    os.environ["XDG_RUNTIME_DIR"] = "/tmp/runtime-root"
    QStandardPaths.setTestModeEnabled(True)  # Qt'nin test modu için geçerli yolu kullanmasını sağla

def get_icon_path():
    """Simge dosyasının yolunu döndürür."""
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, "dnsticlo.png")
    elif os.path.exists("/usr/share/icons/hicolor/48x48/apps/dnsticlo.png"):
        return "/usr/share/icons/hicolor/48x48/apps/dnsticlo.png"
    return None

ICON_PATH = get_icon_path()
    
def get_resource_path(filename):
    """Uygun kaynak dosya yolunu döndürür."""
    if hasattr(sys, "_MEIPASS"):
        # PyInstaller ile paketlendiğinde
        return os.path.join(sys._MEIPASS, filename)
    
    # Farklı olası konumlar
    possible_paths = [
        os.path.join(os.path.dirname(__file__), filename),
        f"/usr/share/icons/hicolor/48x48/apps/{filename}",
        os.path.expanduser(f"~/.local/share/icons/{filename}"),
        filename
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
    
    return filename  # Son çare olarak orijinal dosya adını döndür


class DnsChanger(QWidget):
    def __init__(self):
        super().__init__()
        
        # QSettings için ayarlama
        self.settings = QSettings("DNSticApps", "DNStic")
        
        # Logo yolu
        self.logo_path = get_resource_path("dnsticlo.png")
        
        # Pencere ayarları
        self.setWindowIcon(QIcon(self.logo_path))
        self.setWindowTitle("DNStic")
        self.setGeometry(100, 100, 650, 600)
        self.setMinimumSize(400, 300)  # Doğru nesneye minimum boyut ayarı
        
        # Dark theme ve stil
        self.setStyleSheet("""
            QWidget { 
                background-color: #2e2e2e; 
                color: white; 
                font-size: 14px; 
            }
            QLineEdit, QComboBox, QTableWidget {
                background-color: #404040;
                color: white;
                border: 1px solid #505050;
                padding: 5px;
                border-radius: 4px;
            }
            QPushButton {
                background-color: #3a3a3a;
                color: white;
                border: 1px solid #505050;
                padding: 8px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #4a4a4a;
            }
        """)
        
        # Ana layout
        main_layout = QVBoxLayout()        
        # Logo kısmı - Merkezlenmiş ve boyutlandırılmış
        logo_container = QVBoxLayout()
        self.logo_label = QLabel(self)
        pixmap = QPixmap(self.logo_path)
        scaled_pixmap = pixmap.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.logo_label.setPixmap(scaled_pixmap)
        self.logo_label.setAlignment(Qt.AlignCenter)
        logo_container.addWidget(self.logo_label)
        logo_container.setAlignment(Qt.AlignCenter)
        
        # Başlık etiketi
        title_label = QLabel("Dynamic DNS Tool with Interface for Linux")
        title_label.setAlignment(Qt.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        logo_container.addWidget(title_label)
        
        # Logo konteynerini ana layouta ekle
        main_layout.addLayout(logo_container)
        
        # DNS Listesi
        self.dns_table = QTableWidget(self)
        self.dns_table.setRowCount(0)
        self.dns_table.setColumnCount(2)
        self.dns_table.setHorizontalHeaderLabels(["DNS Adı", "IP Adresi"])
        self.dns_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        main_layout.addWidget(self.dns_table)
        
        # Silme butonu
        self.delete_button = QPushButton("Seçili DNS'i Sil", self)
        self.delete_button.clicked.connect(self.delete_dns)
        main_layout.addWidget(self.delete_button)

        # DNS Ekleme
        dns_input_layout = QHBoxLayout()
        
        self.dns_name_input = QLineEdit(self)
        self.dns_name_input.setPlaceholderText("DNS Adı")
        
        self.dns_ip_input = QLineEdit(self)
        self.dns_ip_input.setPlaceholderText("DNS IP Adresi")

        add_button = QPushButton("DNS Ekle", self)
        add_button.clicked.connect(self.add_dns)
        
        dns_input_layout.addWidget(self.dns_name_input)
        dns_input_layout.addWidget(self.dns_ip_input)
        dns_input_layout.addWidget(add_button)

        main_layout.addLayout(dns_input_layout)
        
        # DNS Seçim
        self.dns_selector = QComboBox(self)
        self.dns_selector.addItem("DNS Seçin")
        main_layout.addWidget(self.dns_selector)
        
        # DNS Uygula
        apply_button = QPushButton("DNS Uygula", self)
        apply_button.clicked.connect(self.apply_dns)
        main_layout.addWidget(apply_button)
        
        # Hakkında butonu - Ana layouta ekle
        about_button = QPushButton("Hakkında")
        about_button.clicked.connect(self.show_about_dialog)
        main_layout.addWidget(about_button)
        
        
                
        self.setLayout(main_layout)

        # Kayıtlı DNS'leri yükle
        self.load_saved_dns()

    def validate_ip(self, ip):
        # IP formatı kontrolü
        parts = ip.split('.')
        if len(parts) != 4:
            return False
        
        try:
            return all(
                0 <= int(part) <= 255 and 
                str(int(part)) == part  # Önde sıfır olmaması için
                for part in parts
            )
        except ValueError:
            return False
        
    def add_dns(self):
        dns_name = self.dns_name_input.text().strip()
        dns_ip = self.dns_ip_input.text().strip()
        
        # IP formatı kontrolü
        if not self.validate_ip(dns_ip):
            self.show_error_message("Geçersiz IP adresi formatı!")
            return
        
        if dns_name and dns_ip:
            # DNS zaten listede mi kontrol et
            for row in range(self.dns_table.rowCount()):
                if (self.dns_table.item(row, 0).text() == dns_name or 
                    self.dns_table.item(row, 1).text() == dns_ip):
                    self.show_error_message("Bu DNS zaten listede mevcut!")
                    return

            row_position = self.dns_table.rowCount()
            self.dns_table.insertRow(row_position)
            self.dns_table.setItem(row_position, 0, QTableWidgetItem(dns_name))
            self.dns_table.setItem(row_position, 1, QTableWidgetItem(dns_ip))

            self.dns_selector.addItem(f"{dns_name} ({dns_ip})")
            
            # DNS'i kaydet
            self.save_dns()
            
            # Clear inputs
            self.dns_name_input.clear()
            self.dns_ip_input.clear()

    def delete_dns(self):
        # Seçili satırı sil
        current_row = self.dns_table.currentRow()
        if current_row >= 0:
            dns_name = self.dns_table.item(current_row, 0).text()
            dns_ip = self.dns_table.item(current_row, 1).text()
            
            # DNS Selector'dan da çıkar
            index = self.dns_selector.findText(f"{dns_name} ({dns_ip})")
            if index != -1:
                self.dns_selector.removeItem(index)
            
            # Tablodan sil
            self.dns_table.removeRow(current_row)
            
            # Kayıtlı DNS'leri güncelle
            self.save_dns()

    def save_dns(self):
        # Tüm DNS'leri kaydet
        dns_list = []
        for row in range(self.dns_table.rowCount()):
            dns_name = self.dns_table.item(row, 0).text()
            dns_ip = self.dns_table.item(row, 1).text()
            dns_list.append({"name": dns_name, "ip": dns_ip})
        
        # QSettings ile kaydet
        self.settings.setValue("dns_list", json.dumps(dns_list))

    def load_saved_dns(self):
        # Kayıtlı DNS'leri yükle
        saved_dns = self.settings.value("dns_list")
        
        # Bazı yaygın DNS sunucuları
        default_dns = [
            {"name": "Google DNS", "ip": "8.8.8.8"},
            {"name": "Cloudflare DNS", "ip": "1.1.1.1"},
            {"name": "OpenDNS", "ip": "208.67.222.222"},
            {"name": "Quad9 DNS", "ip": "9.9.9.9"}
        ]
        
        # Eğer kayıtlı DNS yoksa, varsayılan DNS'leri ekle
        if not saved_dns:
            dns_list = default_dns
        else:
            try:
                dns_list = json.loads(saved_dns)
            except json.JSONDecodeError:
                dns_list = default_dns

        # DNS'leri tabloya ekle
        for dns in dns_list:
            row_position = self.dns_table.rowCount()
            self.dns_table.insertRow(row_position)
            self.dns_table.setItem(row_position, 0, QTableWidgetItem(dns["name"]))
            self.dns_table.setItem(row_position, 1, QTableWidgetItem(dns["ip"]))
            self.dns_selector.addItem(f"{dns['name']} ({dns['ip']})")

    def get_network_connections(self):
        # NetworkManager ve system-connections için birden fazla olası yol
        connection_paths = [
            "/etc/NetworkManager/system-connections/",
            "/run/NetworkManager/system-connections/",
            os.path.expanduser("~/.config/NetworkManager/system-connections/")
        ]
        
        connections = []
        for path in connection_paths:
            if os.path.exists(path):
                try:
                    for file_name in os.listdir(path):
                        full_path = os.path.join(path, file_name)
                        if os.path.isfile(full_path):
                            connections.append(full_path)
                except Exception as e:
                    print(f"Bağlantı dosyaları taranırken hata: {e}")
        
        return connections

    def resolve_dns_method(self, dns_ip):
        # Farklı DNS değiştirme metodları
        methods = [
            self.change_dns_networkmanager,
            self.change_dns_resolvconf,
            self.change_dns_systemd_resolved
        ]
        
        for method in methods:
            try:
                result = method(dns_ip)
                if result:
                    return True
            except Exception as e:
                print(f"DNS değiştirilirken hata oluştu: {e}")
        
        return False

    def change_dns_networkmanager(self, dns_ip):
        connections = self.get_network_connections()
        
        if not connections:
            return False

        for connection_file in connections:
            try:
                with open(connection_file, 'r') as f:
                    lines = f.readlines()

                new_lines = []
                inside_ipv4 = False
                dns_replaced = False

                for line in lines:
                    if line.strip() == "[ipv4]":
                        inside_ipv4 = True
                        new_lines.append(line)
                        continue

                    if inside_ipv4 and line.strip().startswith("dns="):
                        new_lines.append(f"dns={dns_ip};\n")
                        dns_replaced = True
                        inside_ipv4 = False
                        continue

                    if inside_ipv4 and line.strip().startswith("method=") and not dns_replaced:
                        new_lines.append(f"dns={dns_ip};\n")
                        dns_replaced = True
                        new_lines.append(line)
                        inside_ipv4 = False
                        continue

                    new_lines.append(line)

                with open(connection_file, 'w') as f:
                    f.writelines(new_lines)

            except Exception as e:
                print(f"NetworkManager dosyası güncellenirken hata: {e}")

        # NetworkManager'ı yeniden başlat
        try:
            subprocess.run(["sudo", "systemctl", "restart", "NetworkManager"], check=True)
            return True
        except Exception as e:
            print(f"NetworkManager yeniden başlatılamadı: {e}")
            return False

    def change_dns_resolvconf(self, dns_ip):
        try:
            # resolv.conf dosyasını güncelle
            with open("/etc/resolv.conf", "w") as f:
                f.write(f"nameserver {dns_ip}\n")
            
            return True
        except Exception as e:
            print(f"resolv.conf güncellenirken hata: {e}")
            return False

    def change_dns_systemd_resolved(self, dns_ip):
        try:
            # systemd-resolved için DNS ayarla
            subprocess.run(["sudo", "systemd-resolve", "--set-dns", dns_ip], check=True)
            subprocess.run(["sudo", "systemctl", "restart", "systemd-resolved"], check=True)
            return True
        except Exception as e:
            print(f"systemd-resolved güncellenirken hata: {e}")
            return False

    def apply_dns(self):
        selected_dns = self.dns_selector.currentText()

        if selected_dns != "DNS Seçin":
            dns_ip = selected_dns.split('(')[-1].strip(')')
            
            try:
                # DNS değiştirme metodunu çağır
                if self.resolve_dns_method(dns_ip):
                    self.show_success_message(f"DNS başarıyla {dns_ip} olarak değiştirildi.")
                else:
                    self.show_error_message("DNS değiştirilemedi. Lütfen manuel olarak kontrol edin.")
            
            except Exception as e:
                self.show_error_message(f"DNS uygulama sırasında hata: {e}")
        else:
            self.show_error_message("Lütfen geçerli bir DNS seçin.")

    def show_error_message(self, message):
        error_dialog = QMessageBox()
        error_dialog.setIcon(QMessageBox.Critical)
        error_dialog.setText(message)
        error_dialog.setWindowTitle("Hata")
        error_dialog.exec_()

    def show_success_message(self, message):
        success_dialog = QMessageBox()
        success_dialog.setIcon(QMessageBox.Information)
        success_dialog.setText(message)
        success_dialog.setWindowTitle("Başarılı")
        success_dialog.exec_()
        
    def show_about_dialog(self):
        dialog = AboutDialog()
        dialog.exec_()
        
class AboutDialog(QDialog):
    def __init__(self):
        super().__init__()
        
        # Dialog başlığı
        self.setWindowTitle("Hakkında")
        self.setFixedSize(350, 400)

        # Layout
        layout = QVBoxLayout()

        # Uygulama hakkında bilgi
        about_label = QLabel("""<h2>DNStic</h2>
            <p>Dynamic DNS Tool with Interface for Linux (Linux için Arayüzlü Dinamik DNS Aracı)</p>
            <p>Linux kullanıcılarının DNS ayarlarını kolay ve hızlı bir şekilde değiştirmelerine olanak tanıyan bir araçtır. Kullanıcı dostu grafik arayüzü sayesinde, farklı DNS adreslerini ekleyebilir, yönetebilir ve uygulayabilirsiniz.</p>
            <p><b>Geliştirici:</b> ALG Yazılım Inc.©</p>
            <p>www.algyazilim.com | info@algyazilim.com</p>
            </br>
            <p>Fatih ÖNDER (CekToR) | fatih@algyazilim.com</p>
            <p><b>GitHub:</b> https://github.com/cektor</p>
            </br>
            </br>
            <p><b>ALG Yazılım</b> Pardus'a Göç'ü Destekler.</p>
            </br>
            <p><b>Sürüm:</b> 1.0</p>
        """)
        about_label.setWordWrap(True)  # WordWrap özelliği eklendi
        layout.addWidget(about_label)   

        # Layout'u dialog'a ayarla
        self.setLayout(layout)      

def main():
    try:
        # Sudo izni kontrolü
        subprocess.run(["sudo", "-n", "true"], check=True)
    except subprocess.CalledProcessError:
        print("Bu uygulama sudo izni gerektirir. Lütfen sudo ile çalıştırın.")
        return

    app = QApplication(sys.argv)
    if ICON_PATH:
        app.setWindowIcon(QIcon(ICON_PATH))
    window = DnsChanger()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()