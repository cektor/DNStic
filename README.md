<a href="#">
    <img src="https://raw.githubusercontent.com/pedromxavier/flag-badges/main/badges/TR.svg" alt="made in TR">
</a>

# DNStic
Dynamic DNS Tool with Interface for Linux It is a tool that allows Linux users to change their DNS settings easily and quickly. Thanks to its user-friendly graphical interface, you can add, manage and apply different DNS addresses.

<h1 align="center">DNStic Logo</h1>

<p align="center">
  <img src="dnsticlo.png" alt="DNStic Logo" width="150" height="150">
</p>


----------------------

# Linux Screenshot
![Linux(pardus)](screenshot/dnstic_linux.gif)  

--------------------
Install Git Clone and Python3

Github Package Must Be Installed On Your Device.

git
```bash
sudo apt install git -y
```

Python3
```bash
sudo apt install python3 -y 

```

pip
```bash
sudo apt install python3-pip

```

# Required Libraries

Required Libraries for Debian/Ubuntu
```bash
sudo apt-get install python3-pyqt5
sudo apt-get install qttools5-dev-tools
sudo apt install network-manager
sudo apt install systemd
```


PyQt5
```bash
pip install PyQt5
```
PyQt5-sip
```bash
pip install PyQt5 PyQt5-sip
```

PyQt5-tools
```bash
pip install PyQt5-tools
```
----------------------------------


# Installation
Install DNStic

```bash
sudo git clone https://github.com/cektor/DNStic.git
```
```bash
cd DNStic
```

```bash
python3 dnstic.py

```

# To compile

NOTE: For Compilation Process pyinstaller must be installed. To Install If Not Installed.

pip install pyinstaller 

Linux Terminal 
```bash
pytohn3 -m pyinstaller --onefile --windowed dnstic.py
```

MacOS VSCode Terminal 
```bash
pyinstaller --onefile --noconsole dnstic.py
```

# To install directly on Linux

Linux (based debian) Terminal: Linux (debian based distributions) To install directly from Terminal.
```bash
wget -O Setup_Linux64.deb https://github.com/cektor/DNStic/releases/download/1.00/Setup_Linux64.deb && sudo apt install ./Setup_Linux64.deb && sudo apt-get install -f -y
```


Release Page: https://github.com/cektor/DNStic/releases/tag/1.00

----------------------------------
