# richl3rrrrr — Arduino Firmware Flasher

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://python.org)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS-lightgrey)]()
[![Discord](https://img.shields.io/badge/Discord-Join-5865F2)](https://discord.gg/MQ64FpRqaf)

> One-click GUI tool to compile & flash firmware to Arduino Leonardo / Micro / Uno with **USB descriptor spoofing** pre-configured.

---

## 📖 Bahasa

- [🇬🇧 English](#english)
- [🇮🇩 Bahasa Indonesia](#bahasa-indonesia)

---

## 🇬🇧 English

### Features

- ⚡ **Two flash modes:** Compile `.ino` source directly, or flash pre-compiled `.hex` binaries
- 🎮 **Gaming dark theme UI** — built with CustomTkinter
- 🔍 **Auto-detect Arduino** — finds COM ports automatically
- 🛡️ **USB spoofing pre-configured** — firmware appears as **Logitech G502 HERO** (not Arduino)
- 🖥️ **Cross-platform** — Windows & macOS
- 💬 **Built-in Discord link** — one-click to support server

### Quick Start

#### macOS
```bash
# 1. Install dependencies
brew install python@3.12 arduino-cli

# 2. Clone
git clone https://github.com/gnetid/Arduino-Richl3rrrrr.git
cd Arduino-Richl3rrrrr

# 3. Download firmware from Discord → put in HID_Arduino/
#    https://discord.gg/MQ64FpRqaf

# 4. Run
pip install customtkinter pyserial pillow
python flasher_gui.py
```

#### Windows
```bash
# 1. Install Python 3.10+ (check "Add to PATH")
# 2. Download arduino-cli and put arduino-cli.exe in tools/
#    https://github.com/arduino/arduino-cli/releases
# 3. Download firmware from Discord → put in HID_Arduino/
#    https://discord.gg/MQ64FpRqaf

# 4. Double-click run.bat
```

### Usage

1. Connect Arduino via USB
2. Launch the flasher
3. Choose **Source (.ino) → Auto-Compile** (default)
4. Select your board
5. Click **⚡ FLASH FIRMWARE**
6. Wait for compile + upload → Done

### Board Support

| Board | MCU | Spoofed VID:PID |
|---|---|---|
| Arduino Leonardo | ATmega32U4 | `046D:C084` (Logitech G502 HERO) |
| Arduino Micro | ATmega32U4 | `046D:C084` |
| Arduino Uno | ATmega328P | `046D:C084` |

### What's Inside

```
richl3rrrrr/
├── flasher_gui.py          # Main GUI application
├── run.bat                  # Windows 1-click launcher
├── HID_Arduino/             # Firmware source (auto-compile mode)
│   ├── HID_Arduino.ino      # USB-spoofed firmware
│   ├── hidcustom.h          # Mouse report parser
│   ├── ImprovedMouse.h      # HID mouse wrapper
│   └── ImprovedMouse.cpp
├── firmware/                # Drop pre-compiled .hex files here
└── tools/                   # Drop avrdude.exe / arduino-cli.exe here
```

### Troubleshooting

| Problem | Fix |
|---|---|
| **Compile failed** | Make sure the folder name matches the `.ino` filename |
| **COM port not found** | Click the ⟳ refresh button |
| **Upload timeout** | Press the RESET button on Arduino, then click FLASH immediately |
| **arduino-cli not found** | Install: `brew install arduino-cli` (Mac) or put `.exe` in `tools/` |
| **Missing libraries** | The flasher auto-installs them on first run |

---

## 🇮🇩 Bahasa Indonesia

### Fitur

- ⚡ **Dua mode flash:** Kompilasi source `.ino` langsung, atau flash file `.hex` jadi
- 🎮 **UI dark theme gaming** — dibangun dengan CustomTkinter
- 🔍 **Auto-deteksi Arduino** — otomatis mencari COM port
- 🛡️ **USB spoofing bawaan** — firmware muncul sebagai **Logitech G502 HERO** (bukan Arduino)
- 🖥️ **Cross-platform** — Windows & macOS
- 💬 **Link Discord built-in** — satu klik ke server support

### Mulai Cepat

#### macOS
```bash
# 1. Install dependensi
brew install python@3.12 arduino-cli

# 2. Clone
git clone https://github.com/gnetid/Arduino-Richl3rrrrr.git
cd Arduino-Richl3rrrrr

# 3. Download firmware dari Discord → taruh di HID_Arduino/
#    https://discord.gg/MQ64FpRqaf

# 4. Jalankan
pip install customtkinter pyserial pillow
python flasher_gui.py
```

#### Windows
```bash
# 1. Install Python 3.10+ (centang "Add to PATH")
# 2. Download arduino-cli dan taruh arduino-cli.exe di folder tools/
#    https://github.com/arduino/arduino-cli/releases
# 3. Download firmware dari Discord → taruh di HID_Arduino/
#    https://discord.gg/MQ64FpRqaf

# 4. Double-click run.bat
```

### Cara Pakai

1. Colok Arduino ke USB
2. Buka flasher
3. Pilih **Source (.ino) → Auto-Compile** (default)
4. Pilih board kamu
5. Klik **⚡ FLASH FIRMWARE**
6. Tunggu compile + upload → Selesai

### Dukungan Board

| Board | MCU | VID:PID Spoof |
|---|---|---|
| Arduino Leonardo | ATmega32U4 | `046D:C084` (Logitech G502 HERO) |
| Arduino Micro | ATmega32U4 | `046D:C084` |
| Arduino Uno | ATmega328P | `046D:C084` |

### Troubleshooting

| Masalah | Solusi |
|---|---|
| **Compile gagal** | Pastikan nama folder sama dengan nama file `.ino` |
| **COM port tidak muncul** | Klik tombol ⟳ untuk refresh |
| **Upload timeout** | Tekan tombol RESET di Arduino, langsung klik FLASH |
| **arduino-cli tidak ditemukan** | Install: `brew install arduino-cli` (Mac) atau taruh `.exe` di `tools/` |
| **Library kurang** | Flasher otomatis install library saat pertama kali |

---

## 📄 Credits

- Built with [CustomTkinter](https://customtkinter.tomschimansky.com/)
- Flashing powered by [Arduino CLI](https://arduino.github.io/arduino-cli/)
- USB Host Shield library by [felis](https://github.com/felis/USB_Host_Shield_2.0)
- Original HID firmware base by [SunOner](https://github.com/SunOner/HID_Arduino)

## ⚠️ Disclaimer

This tool is for educational purposes. Use responsibly and in compliance with applicable laws and platform terms of service.
