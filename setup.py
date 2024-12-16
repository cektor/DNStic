from setuptools import setup, find_packages

setup(
    name="dnstic",  # Paket adı
    version="1.0",  # Paket sürümü
    description="Dynamic DNS Tool with Interface for Linux",  # Paket açıklaması
    author="Fatih Önder",  # Paket sahibi adı
    author_email="fatih@algyazilim.com",  # Paket sahibi e-posta adresi
    url="https://github.com/cektor/DNStic",  # Paket deposu URL'si
    packages=find_packages(),  # Otomatik olarak tüm alt paketleri bulur
    install_requires=[
        'PyQt5>=5.15.0',  # PyQt5 bağımlılığı (versiyon sınırı belirtilmiş)
    ],
    package_data={
        'dnstic': ['*.png', '*.desktop'],  # 'dnsmgr' paketine dahil dosyalar
    },
    data_files=[
        ('share/applications', ['dnstic.desktop']),  # Uygulama menüsüne .desktop dosyasını ekler
        ('share/icons/hicolor/48x48/apps', ['dnsticlo.png']),  # Simgeyi uygun yere ekler
    ],
    entry_points={
        'gui_scripts': [
            'dnstic=dnstic:main',  # `dnstic` modülündeki `main` fonksiyonu çalıştırılır
        ]
    },
)
