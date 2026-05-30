#!/usr/bin/env python3
"""richl3rrrrr Arduino Flasher — Gaming-themed one-click firmware tool"""
import customtkinter as ctk
from tkinter import filedialog, messagebox
import subprocess
import sys
from pathlib import Path
from threading import Thread, Lock

BASE_DIR = Path(__file__).parent.resolve()
TOOLS_DIR = BASE_DIR / "tools"
FIRMWARE_DIR = BASE_DIR / "firmware"
DEFAULT_SOURCE = str(BASE_DIR / "HID_Arduino") if (BASE_DIR / "HID_Arduino").exists() else ""

NEON = "#00FF88"
BG = "#0A0A0F"
CARD = "#12121A"
ACCENT = "#1A1A2E"
TEXT = "#E0E0E0"
DIM = "#666680"
PURPLE = "#7C3AED"

BOARDS = {
    "Arduino Leonardo": {"mcu": "atmega32u4", "prog": "avr109", "baud": "57600", "fqbn": "arduino:avr:leonardo"},
    "Arduino Micro":    {"mcu": "atmega32u4", "prog": "avr109", "baud": "57600", "fqbn": "arduino:avr:micro"},
    "Arduino Uno":      {"mcu": "atmega328p", "prog": "arduino", "baud": "115200", "fqbn": "arduino:avr:uno"},
}

MODE_SOURCE = "Source (.ino) → Auto-Compile"
MODE_HEX    = "Pre-compiled (.hex)"


def find_arduino_cli():
    for c in [TOOLS_DIR / "arduino-cli.exe", TOOLS_DIR / "arduino-cli",
              Path("/opt/homebrew/bin/arduino-cli"), Path("/usr/local/bin/arduino-cli")]:
        if c.exists():
            return str(c)
    return "arduino-cli"


def find_avrdude():
    for c in [TOOLS_DIR / "avrdude.exe", TOOLS_DIR / "avrdude",
              Path("/opt/homebrew/bin/avrdude"), Path("/usr/local/bin/avrdude")]:
        if c.exists():
            return str(c)
    return "avrdude"


def detect_serial_ports():
    try:
        import serial.tools.list_ports
        return [p.device for p in serial.tools.list_ports.comports()]
    except ImportError:
        return []


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("richl3rrrrr")
        self.geometry("600x620")
        self.minsize(480, 500)
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        self.source_path = ctk.StringVar(value=DEFAULT_SOURCE)
        self.hex_path = ctk.StringVar()
        self.com_port = ctk.StringVar()
        self.board_type = ctk.StringVar(value="Arduino Leonardo")
        self.flash_mode = ctk.StringVar(value=MODE_SOURCE)
        self.status_text = ctk.StringVar(value="● Ready — Connect Arduino to begin")
        self.flashing = False
        self.log_lock = Lock()

        self._build()
        self._auto_detect()
        self.on_mode_change()

    def _build(self):
        self.configure(fg_color=BG)

        top = ctk.CTkFrame(self, fg_color=CARD, corner_radius=0, height=56)
        top.pack(fill="x")
        top.pack_propagate(False)
        ctk.CTkLabel(top, text="richl3rrrrr", font=ctk.CTkFont(size=22, weight="bold"),
                     text_color=NEON).pack(side="left", padx=20, pady=12)
        ctk.CTkLabel(top, text="Firmware Flasher", font=ctk.CTkFont(size=12),
                     text_color=DIM).pack(side="left", pady=14)
        self.discord_label = ctk.CTkLabel(top, text="💬 Discord", font=ctk.CTkFont(size=12, underline=True),
                     text_color="#5865F2", cursor="hand2")
        self.discord_label.pack(side="right", padx=20, pady=16)
        self.discord_label.bind("<Button-1>", lambda e: self._open_discord())
        self.discord_label.bind("<Enter>", lambda e: self.discord_label.configure(text_color="#7983F5"))
        self.discord_label.bind("<Leave>", lambda e: self.discord_label.configure(text_color="#5865F2"))

        content = ctk.CTkScrollableFrame(self, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=16, pady=(12, 8))

        ctk.CTkLabel(content, text="Flash Mode", font=ctk.CTkFont(size=12, weight="bold"),
                     text_color=TEXT).pack(anchor="w", pady=(4, 2))
        mf = ctk.CTkFrame(content, fg_color=CARD, corner_radius=10)
        mf.pack(fill="x", pady=(0, 8))
        ctk.CTkSegmentedButton(
            mf, values=[MODE_SOURCE, MODE_HEX], variable=self.flash_mode,
            command=self.on_mode_change, selected_color=PURPLE,
            selected_hover_color="#8B5CF6", unselected_color=ACCENT,
            unselected_hover_color="#2A2A3E",
        ).pack(fill="x", padx=12, pady=12)

        self.source_card = ctk.CTkFrame(content, fg_color=CARD, corner_radius=10)
        ctk.CTkLabel(self.source_card, text="Firmware Source (.ino folder)",
                     font=ctk.CTkFont(size=11, weight="bold"), text_color=TEXT).pack(anchor="w", padx=14, pady=(12, 2))
        sr = ctk.CTkFrame(self.source_card, fg_color="transparent")
        sr.pack(fill="x", padx=14, pady=(4, 12))
        ctk.CTkEntry(sr, textvariable=self.source_path, fg_color=ACCENT, border_color="#2A2A3E",
                     height=34).pack(side="left", fill="x", expand=True)
        ctk.CTkButton(sr, text="Browse", width=70, height=34, fg_color=ACCENT,
                      hover_color="#2A2A3E", command=self._browse_source).pack(side="left", padx=(8, 0))

        self.hex_card = ctk.CTkFrame(content, fg_color=CARD, corner_radius=10)
        ctk.CTkLabel(self.hex_card, text="Pre-compiled Firmware (.hex / .bin)",
                     font=ctk.CTkFont(size=11, weight="bold"), text_color=TEXT).pack(anchor="w", padx=14, pady=(12, 2))
        hr = ctk.CTkFrame(self.hex_card, fg_color="transparent")
        hr.pack(fill="x", padx=14, pady=(4, 4))
        ctk.CTkEntry(hr, textvariable=self.hex_path, fg_color=ACCENT, border_color="#2A2A3E",
                     height=34).pack(side="left", fill="x", expand=True)
        ctk.CTkButton(hr, text="Browse", width=70, height=34, fg_color=ACCENT,
                      hover_color="#2A2A3E", command=self._browse_hex).pack(side="left", padx=(8, 0))

        self.presets_frame = ctk.CTkFrame(self.hex_card, fg_color="transparent")
        self.presets_frame.pack(fill="x", padx=14, pady=(0, 10))
        self._refresh_presets()

        row = ctk.CTkFrame(content, fg_color="transparent")
        row.pack(fill="x", pady=8)
        l = ctk.CTkFrame(row, fg_color="transparent")
        l.pack(side="left", fill="x", expand=True, padx=(0, 4))
        r = ctk.CTkFrame(row, fg_color="transparent")
        r.pack(side="left", fill="x", expand=True, padx=(4, 0))

        ctk.CTkLabel(l, text="Board", font=ctk.CTkFont(size=11, weight="bold"),
                     text_color=TEXT).pack(anchor="w")
        self.board_cb = ctk.CTkComboBox(l, values=list(BOARDS.keys()),
                                        variable=self.board_type, fg_color=ACCENT,
                                        border_color="#2A2A3E", button_color=PURPLE,
                                        button_hover_color="#8B5CF6", dropdown_fg_color=CARD, height=34)
        self.board_cb.pack(fill="x")

        ctk.CTkLabel(r, text="COM Port", font=ctk.CTkFont(size=11, weight="bold"),
                     text_color=TEXT).pack(anchor="w")
        pr = ctk.CTkFrame(r, fg_color="transparent")
        pr.pack(fill="x")
        self.port_cb = ctk.CTkComboBox(pr, values=[], variable=self.com_port,
                                       fg_color=ACCENT, border_color="#2A2A3E",
                                       button_color=PURPLE, button_hover_color="#8B5CF6",
                                       dropdown_fg_color=CARD, height=34)
        self.port_cb.pack(side="left", fill="x", expand=True)
        ctk.CTkButton(pr, text="⟳", width=34, height=34, fg_color=ACCENT,
                      hover_color="#2A2A3E", command=self._scan_ports).pack(side="left", padx=(6, 0))

        self.progress = ctk.CTkProgressBar(content, fg_color=ACCENT, progress_color=NEON,
                                           height=4, corner_radius=2)
        self.progress.configure(mode="indeterminate")

        self.flash_btn = ctk.CTkButton(content, text="⚡  FLASH FIRMWARE",
                                       font=ctk.CTkFont(size=15, weight="bold"),
                                       fg_color=PURPLE, hover_color="#8B5CF6",
                                       height=48, corner_radius=10, command=self._flash)
        self.flash_btn.pack(fill="x", pady=(10, 6))

        self.log = ctk.CTkTextbox(content, font=ctk.CTkFont(family="JetBrains Mono", size=11),
                                  fg_color="#0D0D14", border_color="#1E1E2E",
                                  border_width=1, corner_radius=8, height=180)
        self.log.pack(fill="both", expand=True, pady=(2, 4))
        self.log.configure(state="disabled")

        bar = ctk.CTkFrame(self, fg_color=CARD, corner_radius=0, height=32)
        bar.pack(fill="x", side="bottom")
        bar.pack_propagate(False)
        ctk.CTkLabel(bar, textvariable=self.status_text, text_color=DIM,
                     font=ctk.CTkFont(size=10)).pack(side="left", padx=16, pady=6)
        ctk.CTkLabel(bar, text="v1.0", text_color="#333340",
                     font=ctk.CTkFont(size=10)).pack(side="right", padx=16, pady=6)

        self.protocol("WM_DELETE_WINDOW", lambda: self.destroy())

    def _open_discord(self):
        import subprocess as sp
        url = "https://discord.gg/MQ64FpRqaf"
        if sys.platform == "darwin":
            sp.Popen(["open", url])
        elif sys.platform == "win32":
            sp.Popen(["cmd", "/c", "start", url])
        else:
            sp.Popen(["xdg-open", url])

    def on_mode_change(self, *_):
        if self.flash_mode.get() == MODE_SOURCE:
            self.source_card.pack(fill="x", padx=0, pady=(0, 8))
            self.hex_card.pack_forget()
        else:
            self.hex_card.pack(fill="x", padx=0, pady=(0, 8))
            self.source_card.pack_forget()
            self._refresh_presets()

    def _auto_detect(self):
        self._scan_ports()
        self._refresh_presets()

    def _refresh_presets(self):
        for w in self.presets_frame.winfo_children():
            w.destroy()
        if FIRMWARE_DIR.exists():
            presets = sorted(FIRMWARE_DIR.glob("*"))
            if presets:
                for p in presets:
                    ctk.CTkButton(self.presets_frame, text=p.name, width=160,
                                  fg_color="#1A1A2E", hover_color="#2A2A3E",
                                  border_color=NEON, border_width=1, text_color=NEON,
                                  command=lambda px=p: self.hex_path.set(str(px))
                                  ).pack(side="left", padx=2)

    def _scan_ports(self):
        ports = detect_serial_ports()
        self.port_cb.configure(values=ports)
        if ports:
            self.port_cb.set(ports[0])

    def _browse_source(self):
        p = filedialog.askdirectory(title="Select .ino source folder")
        if p:
            self.source_path.set(p)

    def _browse_hex(self):
        p = filedialog.askopenfilename(filetypes=[("Firmware", "*.hex *.bin"), ("All", "*.*")])
        if p:
            self.hex_path.set(p)

    def _log(self, msg):
        with self.log_lock:
            self.log.configure(state="normal")
            self.log.insert("end", msg + "\n")
            self.log.see("end")
            self.log.configure(state="disabled")
        self.update_idletasks()

    def _flash(self):
        if self.flashing:
            return
        port = self.com_port.get()
        board = BOARDS.get(self.board_type.get())
        mode = self.flash_mode.get()
        if not port:
            messagebox.showerror("Error", "No COM port. Plug in device and click Refresh.")
            return

        self.flashing = True
        self.flash_btn.configure(text="FLASHING…", state="disabled", fg_color="#2A2A3E")
        self.progress.pack(fill="x", padx=0, pady=(0, 6), before=self.flash_btn)
        self.progress.start()
        self.status_text.set("● Flashing…")

        self._log("▌" + "━" * 40)
        if mode == MODE_SOURCE:
            src = self.source_path.get()
            if not src:
                messagebox.showerror("Error", "No source folder selected.")
                self._on_done(False)
                return
            self._log(f"▌ Source → Compile + Upload")
            self._log(f"▌ {self.board_type.get()}  |  {port}")
            Thread(target=self._compile_flash, args=(port, board, src), daemon=True).start()
        else:
            h = self.hex_path.get()
            if not h:
                messagebox.showerror("Error", "No firmware file selected.")
                self._on_done(False)
                return
            self._log(f"▌ HEX → Direct Flash")
            self._log(f"▌ {self.board_type.get()}  |  {port}  |  {Path(h).name}")
            Thread(target=self._hex_flash, args=(port, h, board), daemon=True).start()

    def _compile_flash(self, port, board, source_dir):
        cli = find_arduino_cli()
        fqbn = board.get("fqbn", "arduino:avr:leonardo")
        try:
            self._log("▌ Installing AVR core + USB Host Shield lib…")
            subprocess.run([cli, "core", "install", "arduino:avr"], capture_output=True, timeout=40)
            subprocess.run([cli, "lib", "install", '"USB Host Shield Library 2.0"'], capture_output=True, timeout=20)
            self._log("▌ Compiling…")
            r = subprocess.run([cli, "compile", "--fqbn", fqbn, source_dir],
                               capture_output=True, text=True, timeout=300)
            lines = [l for l in r.stdout.splitlines() if l.strip()][-6:]
            lines += [l for l in r.stderr.splitlines() if l.strip()][-3:]
            for l in lines:
                self._log(f"  {l}")
            if r.returncode != 0:
                self._log("✗ Compile failed.")
                self.after(0, lambda: self._on_done(False))
                return
            self._log("▌ Uploading…")
            r2 = subprocess.run([cli, "upload", "-p", port, "--fqbn", fqbn, source_dir],
                                capture_output=True, text=True, timeout=60)
            for l in [l for l in r2.stdout.splitlines() + r2.stderr.splitlines() if l.strip()][-5:]:
                self._log(f"  {l}")
            ok = r2.returncode == 0
            self._log("▌" + "━" * 40)
            self._log("✓  FLASH SUCCESSFUL!" if ok else f"✗ Upload failed (code {r2.returncode})")
            self.after(0, lambda: self._on_done(ok))
        except subprocess.TimeoutExpired:
            self._log("✗ Timeout — try pressing RESET on the board")
            self.after(0, lambda: self._on_done(False))
        except FileNotFoundError:
            self._log("✗ arduino-cli not found — install: brew install arduino-cli")
            self.after(0, lambda: self._on_done(False))

    def _hex_flash(self, port, hex_file, board):
        avrdude = find_avrdude()
        conf = TOOLS_DIR / "avrdude.conf"
        cmd = [avrdude, "-v", "-p", board["mcu"], "-c", board["prog"],
               "-P", port, "-b", board.get("baud", "57600"),
               "-U", f"flash:w:{hex_file}:i"]
        if conf.exists():
            cmd[1:1] = ["-C", str(conf)]
        self._log(f"$ {' '.join(cmd)}")
        try:
            p = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            for l in [l for l in p.stdout.splitlines() + p.stderr.splitlines() if l.strip()][-6:]:
                self._log(f"  {l}")
            ok = p.returncode == 0
            self._log("✓  FLASH SUCCESSFUL!" if ok else f"✗ Failed (code {p.returncode})")
            self.after(0, lambda: self._on_done(ok))
        except subprocess.TimeoutExpired:
            self._log("✗ Timeout")
            self.after(0, lambda: self._on_done(False))
        except FileNotFoundError:
            self._log("✗ avrdude not found — put avrdude.exe in tools/")
            self.after(0, lambda: self._on_done(False))

    def _on_done(self, ok):
        self.flashing = False
        self.progress.stop()
        self.progress.pack_forget()
        self.flash_btn.configure(text="⚡  FLASH FIRMWARE", state="normal",
                                 fg_color=PURPLE, hover_color="#8B5CF6")
        self.status_text.set("✓ Flash Complete" if ok else "✗ Flash Failed")
        self._scan_ports()


if __name__ == "__main__":
    App().mainloop()
