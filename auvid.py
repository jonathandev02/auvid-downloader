import os
import re
import sys
import threading
import tkinter as tk

import yt_dlp
from tkinter import filedialog, messagebox, ttk


#base path

if getattr(sys, "frozen", False):
    caminho_base = sys._MEIPASS
else:
    caminho_base = os.path.dirname(__file__)

caminho_ffmpeg = os.path.join(caminho_base, "ffmpeg.exe")
icone_path = os.path.join(caminho_base, "favicon.ico")

#theme

BG = "#0d0d0d"
SURFACE = "#161616"
BORDER = "#2a2a2a"
ACCENT = "#00e5ff"
ACCENT_2 = "#7c3aed"
TEXT = "#f0f0f0"
MUTED = "#606060"
SUCCESS = "#00c853"
ERROR = "#ff3d3d"

FONT_TITLE = ("Courier New", 22, "bold")
FONT_LABEL = ("Courier New", 10)
FONT_SMALL = ("Courier New", 9)
FONT_BUTTON = ("Courier New", 11, "bold")

#validation

def url_valida(url: str) -> bool:
    
    pattern = re.compile(
        r"^(https?://)?"
        r"([\w\-]+\.)+[\w\-]+"
        r"(/[\w\-._~:/?#\[\]@!$&'()*+,;=%]*)?"
        r"$"
    )
    return bool(pattern.match(url))


#app class

class AuVidApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.pasta_download = self._pasta_padrao()

        # Tkinter variables
        self.progress_var = tk.DoubleVar(value=0)
        self.status_var = tk.StringVar(value="Pronto para baixar.")

        self._build_ui()

   
    @staticmethod
    def _pasta_padrao() -> str:
        home = os.path.expanduser("~")
        downloads = os.path.join(home, "Downloads")
        return downloads if os.path.isdir(downloads) else home

    
    #thread-safe UI helpers
    
    def _set_progress(self, value: float):
        self.root.after(0, lambda: self.progress_var.set(value))

    def _set_status(self, text: str):
        self.root.after(0, lambda: self.status_var.set(text))

    def _set_bar_style(self, style: str):
        self.root.after(0, lambda: self.bar_widget.config(style=style))

    def _set_btn_state(self, state: str, text: str):
        self.root.after(
            0, lambda: self.btn_baixar.config(state=state, text=text)
        )


    #download progress hook
   
    def progress_hook(self, d: dict):
        if d["status"] == "downloading":
            pct_raw = d.get("_percent_str", "0%").strip()
            try:
                pct = float(pct_raw.replace("%", ""))
            except ValueError:
                pct = 0.0

            speed = d.get("_speed_str", "-").strip()
            eta = d.get("_eta_str", "-").strip()

           
            self.root.after(
                0,
                lambda p=pct, r=pct_raw, s=speed, e=eta: (
                    self.progress_var.set(p),
                    self.status_var.set(f"⬇ {r} • {s} • ETA {e}"),
                    self.bar_widget.config(
                        style="Accent.Horizontal.TProgressbar"
                    ),
                ),
            )

        elif d["status"] == "finished":
            self.root.after(
                0,
                lambda: (
                    self.progress_var.set(100),
                    self.status_var.set("✔ Processando arquivo..."),
                ),
            )

    
    #download logic
  
    def _executar_download(self, url: str, qualidade: str):
        fmt_map = {
            "Melhor qualidade": "bestvideo+bestaudio/best",
            "1080p": "bestvideo[height<=1080]+bestaudio/best[height<=1080]",
            "720p": "bestvideo[height<=720]+bestaudio/best[height<=720]",
            "480p": "bestvideo[height<=480]+bestaudio/best[height<=480]",
            "Só áudio (MP3)": "bestaudio/best",
        }

        ydl_opts = {
            "format": fmt_map.get(qualidade, "best"),
            "ffmpeg_location": caminho_ffmpeg,
            "outtmpl": os.path.join(
                self.pasta_download, "%(title)s.%(ext)s"
            ),
            "progress_hooks": [self.progress_hook],
            "quiet": True,
            "no_warnings": True,
        }

        if qualidade == "Só áudio (MP3)":
            ydl_opts["postprocessors"] = [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                }
            ]

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            self._set_progress(100)
            self._set_status("✔ Download concluído com sucesso!")
            self._set_bar_style("Success.Horizontal.TProgressbar")

            self.root.after(
                0,
                lambda: messagebox.showinfo(
                    "Sucesso",
                    "Download concluído!\nArquivo salvo na pasta selecionada.",
                ),
            )

        except Exception as e:
            self._set_progress(0)
            self._set_status("✖ Erro no download.")
            self._set_bar_style("Error.Horizontal.TProgressbar")

            self.root.after(
                0, lambda err=str(e): messagebox.showerror("Erro", err)
            )

        finally:
            self._set_btn_state("normal", "BAIXAR")

  
    #button callbacks
   
    def escolher_pasta(self):
        pasta = filedialog.askdirectory()
        if pasta:
            self.pasta_download = pasta
            self.status_var.set(f"📁 Pasta: {self.pasta_download}")

    def baixar_video(self):
        url = self.entrada.get().strip()

        if not url:
            messagebox.showerror("Erro", "Cole um link primeiro!")
            return

        if not url_valida(url):
            messagebox.showerror(
                "Erro", "O link não parece válido.\nVerifique e tente novamente."
            )
            return

        qualidade = self.combo_qualidade.get()

        self.progress_var.set(0)
        self.status_var.set("⏳ Iniciando download...")
        self.bar_widget.config(style="Accent.Horizontal.TProgressbar")
        self.btn_baixar.config(state="disabled", text="BAIXANDO...")

        threading.Thread(
            target=self._executar_download,
            args=(url, qualidade),
            daemon=True,
        ).start()

   
    #UI builder
   
    def _build_ui(self):
        root = self.root

       
        style = ttk.Style()
        style.theme_use("clam")

        style.configure(
            "Accent.Horizontal.TProgressbar",
            troughcolor=SURFACE,
            bordercolor=BORDER,
            background=ACCENT,
            lightcolor=ACCENT,
            darkcolor=ACCENT,
            thickness=6,
        )
        style.configure(
            "Success.Horizontal.TProgressbar",
            troughcolor=SURFACE,
            background=SUCCESS,
            lightcolor=SUCCESS,
            darkcolor=SUCCESS,
            thickness=6,
        )
        style.configure(
            "Error.Horizontal.TProgressbar",
            troughcolor=SURFACE,
            background=ERROR,
            lightcolor=ERROR,
            darkcolor=ERROR,
            thickness=6,
        )
        style.configure(
            "Dark.TCombobox",
            fieldbackground="#1e1e1e",
            background="#1e1e1e",
            foreground=TEXT,
            selectbackground=ACCENT_2,
            selectforeground=TEXT,
            bordercolor=BORDER,
            arrowcolor=ACCENT,
        )
        style.map(
            "Dark.TCombobox",
            fieldbackground=[("readonly", "#1e1e1e")],
            foreground=[("readonly", TEXT)],
        )

        header = tk.Frame(root, bg=BG)
        header.pack(fill="x", padx=30, pady=(28, 0))

        tk.Label(header, text="AU", font=FONT_TITLE, bg=BG, fg=ACCENT).pack(
            side="left"
        )
        tk.Label(header, text="VID", font=FONT_TITLE, bg=BG, fg=TEXT).pack(
            side="left"
        )
        tk.Label(
            header,
            text="Baixe vídeos da internet",
            font=FONT_SMALL,
            bg=BG,
            fg=MUTED,
        ).pack(side="left", padx=(12, 0), pady=(8, 0))

        tk.Frame(root, bg=BORDER, height=1).pack(
            fill="x", padx=30, pady=(12, 0)
        )

        
        card = tk.Frame(
            root,
            bg=SURFACE,
            bd=0,
            highlightthickness=1,
            highlightbackground=BORDER,
        )
        card.pack(fill="x", padx=30, pady=20)

        tk.Label(
            card,
            text="URL DO VÍDEO",
            font=FONT_SMALL,
            bg=SURFACE,
            fg=MUTED,
        ).pack(anchor="w", padx=20, pady=(18, 4))

        entry_frame = tk.Frame(card, bg=ACCENT, padx=1, pady=1)
        entry_frame.pack(fill="x", padx=20)

        self.entrada = tk.Entry(
            entry_frame,
            font=("Courier New", 11),
            bg="#1e1e1e",
            fg=TEXT,
            insertbackground=ACCENT,
            relief="flat",
            bd=6,
        )
        self.entrada.pack(fill="x")

        tk.Frame(card, bg=BORDER, height=1).pack(
            fill="x", padx=20, pady=12
        )

        tk.Label(
            card,
            text="Qualidade",
            font=FONT_SMALL,
            bg=SURFACE,
            fg=MUTED,
        ).pack(anchor="w", padx=20, pady=(0, 4))

        self.combo_qualidade = ttk.Combobox(
            card,
            values=[
                "Melhor qualidade",
                "1080p",
                "720p",
                "480p",
                "Só áudio (MP3)",
            ],
            state="readonly",
            font=("Courier New", 10),
            style="Dark.TCombobox",
        )
        self.combo_qualidade.current(0)
        self.combo_qualidade.pack(fill="x", padx=20, pady=(0, 18))

        #buttons
        self.btn_baixar = tk.Button(
            root,
            text="BAIXAR",
            font=FONT_BUTTON,
            bg=ACCENT,
            fg=BG,
            activebackground="#00b8cc",
            activeforeground=BG,
            relief="flat",
            bd=0,
            cursor="hand2",
            pady=10,
            command=self.baixar_video,
        )
        self.btn_baixar.pack(fill="x", padx=30)

        btn_pasta = tk.Button(
            root,
            text="ESCOLHER PASTA",
            font=FONT_SMALL,
            bg=ACCENT_2,
            fg=TEXT,
            activebackground=ACCENT,
            activeforeground=BG,
            relief="flat",
            bd=0,
            highlightthickness=0,
            cursor="hand2",
            pady=10,
            command=self.escolher_pasta,
        )
        btn_pasta.pack(fill="x", padx=30, pady=(5, 0))

        #progress bar and status
        self.bar_widget = ttk.Progressbar(
            root,
            variable=self.progress_var,
            maximum=100,
            style="Accent.Horizontal.TProgressbar",
        )
        self.bar_widget.pack(fill="x", padx=30, pady=(14, 4))

        tk.Label(
            root,
            textvariable=self.status_var,
            font=FONT_SMALL,
            bg=BG,
            fg=MUTED,
            anchor="w",
        ).pack(fill="x", padx=30)

        # Footer
        tk.Label(
            root,
            text="Powered by yt-dlp",
            font=FONT_SMALL,
            bg=BG,
            fg="#333333",
        ).pack(side="bottom", pady=8)


#entry point

def main():
    janela = tk.Tk()
    janela.title("AuVid")
    janela.geometry("800x600")
    janela.resizable(False, False)
    janela.configure(bg=BG)

    try:
        janela.iconbitmap(icone_path)
    except Exception:
        pass

    AuVidApp(janela)
    janela.mainloop()


if __name__ == "__main__":
    main()
