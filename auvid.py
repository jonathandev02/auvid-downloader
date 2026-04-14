import yt_dlp # O "import" É IMPORTAR FERRAMENTA O "yt_dlp" É A FERRAMENTA DE DOWNLOAD DE VIDEOS
# A "yr_dlp" É UMA BIBLIOTECA QUE SERVE PRA BAIXAR VIDEOS DO YOUTUBE, MUSICAS, PLAYLISTS, PEGA AUDIO TIPO MP3
#FUNCIONA COM VARIOS SITES, NÃO SÓ YOUTUBE

import tkinter as tk #O "tkinter" É A BIBLIOTECA PADRÃO DO PYTHON PRA CRIAR JANELAS, BOTÕES, TELAS..

# O "as" SERVE PRA CRIAR UM APELIDO (alias) PARA ALGO QUE VC IMPORTOU

#O "tk" É SO UM APELIDO, O "tk" ELE DEIXA O CODIGO MAIS LIMPO, POR EXEMPLO
"""
     SEM O APELIDO                        COM APELIDO
   (USAMOS tkinter)                     (USAMOS SO tk)                    
botao = tkinter.Button()               botao = tk.Button()            
janela = tkinter.Tk()                  janela = tk.Tk()            

"""
from tkinter import messagebox, ttk # O FROM USAMOS QUANDO QUEREMOS PEGA PARTES ESPECIFICAS DE UM MODULO COMO
#"tkinter", NÃO É QUE O IMPORT PEGA "TUDO PESADO" E O FROM PEGA "MENOS"
# A REAL DIFERENÇA É A ORGANIZAÇÃO E FORMA DE USAR O CODIGO 
#AQUI ESTAMOS PEGANDO PARTES ESPECIFICAS DO "tkinter"

'''
        'messagebox'
SERVE PRA MOSTRAR JANELINHAS TIPO:

º ERRO
º AVISO
º SCUCESSO

CODIGO DE EXEMPLO

messagebox.showinfo("Sucesso", "Download concluído!")

AQUI ELE GERA UMA JANELINHA DE SUCESSO, DOWNLOAD CNCLUIDO 

'''
'''
O "ttk" SÃO COMPONENTES MAIS BONITOS ESTILOS MODERNO 
EXEMPLO
º BOTÕES MELHORES
º BARRAS DE PROGRESSO
º COMBOBOX (LISTA DE OPÇÕES)
'''


from tkinter import filedialog
"""
O "filedialog" ABRE O EXPLORADOR DE AQQUIVOS DO WINDOWS
SERVE PRA!

º ESCOLHER ONDE SALVAR
º SELECIONAR ARQUIVOS

CODIGO DE EXEMPLO

pasta = filedialog.askdirectory()


"""

import threading
'''
O " threading " É UMA EXECUÇÃO EM PARALELO MUITO IMPORTANTE, PERMITE RODA TAREFAS SEM TRAVAR A INTERFACE

PROBLEMA SEM ISSO 

º VC CLICA EM 'BAIXAR'
º A TELA TRAVA ATE TERMINAR

COM O "threading"

º DOWNLOAD RODA EM SEGUNDO PLANO
º A INTERFACE CONTINUA FUNCIONANDO 
'''
import sys
'''
O 'sys' É ACESSO A COISAS DO SISTEMA DO PYTHON

SERVE PRA 
º FECHAR O PROGRAMA
º PEGAR ARGUMENTOS 
º CONTROLAR EXECUÇÃO

CODIGO DE EXEMPLO

sys.exit()
'''

import os 
'''
O 'os' TRABALHAR COM ARQUIVOS E PASTAS DO SISTEMA

SERVE PRA 
º CRIAR PASTA
º VERIFICAR SE EXISTE
º MONTAR CAMINHOS

CODIGO DE EXEMPLO

if not os.path.exists("downloads"):
    os.makedirs("downloads")

ESSE CODIGO SERVE PRA GARANTIR QUE A PASTA 'download' EXISTA ANTES DO SEU PROGRAMA USAR ELA 

O 'makedirs' CRIA A PASTA ( E ATE SUBPASTAS, SE PRECISAR)

PQ ISSO É IMPORTANTE
IMAGINA, VC TENTA SALVAR UM VIDEO ASSIM 
"downloads/video.mp4"
SE A PASTA NÃO EXISTIR O PYTHON DA ERRO
COM ESSE CODIGO VC EVITA ESSE PROBLEMA

if not os.path.exists("downloads"):
    os.makedirs("downloads")
'''

if getattr(sys, 'frozen', False):
    caminho_base = sys._MEIPASS
else:
    caminho_base = os.path.dirname(__file__)

caminho_ffmpeg = os.path.join(caminho_base, "ffmpeg.exe")


#PALETA DE CORES 
BG = "#0d0d0d" #FUNDO PRINCIPAL
surface = "#161616" #CARDS / PAINÉIS
border = "#2a2a2a" #BORDAS SUTIS
accent = "#00e5ff" #CIANO ELETRICO
accent2 = "#7c3aed" #ROXO PROFUNDO
text = "#f0f0f0" #TEXTO PRINCIAL
muted = "#606060" #TEXTO SECUNDARIO 
success = "#00c853"
error = "#ff3d3d"


font_title = ("courier new", 22, "bold")
font_label = ("courier new", 10)
font_small = ("courier new", 9)
font_btn = ("courier new", 11, "bold")


#ESTADO GLOBAL

progress_var = None
status_var = None
bar_widget = None
btn_baixar = None

pasta_download = os.getcwd()

#hook de progresso 

def progress_hook(d):
    if d['status'] == 'downloading':
        pct_raw = d.get('_percent_str', '0%').strip()
        try:
            pct = float(pct_raw.replace('%',''))
        except ValueError:
            pct = 0.0
        
        speed = d.get('_speed_str', '-').strip()
        eta = d.get('_eta_str',  '-').strip()
        progress_var.set(pct)
        status_var.set(f"⬇  {pct_raw}   •   {speed}   •   ETA {eta}")
        bar_widget.config(style="Accent.Horizontal.TProgressbar")

    elif d['status'] == 'finished' :
        progress_var.set(100)
        status_var.set('✔ Processando arquivo....')

#logica de download

def _executar_download(url, qualidade):
    fmt_map = {
        "Melhor qualidade": 'bestvideo+bestaudio/best',
        "1080p" : 'bestvideo[height<=1080]+bestaudio/best[height<=1080]',
        "720p" : 'bestvideo[height<=720]+bestaudio/best[height<=720]',
        "480p" : 'bestvideo[height<=480]+bestaudio/best[height<=480]',
        "Só áudio (MP3)": "bestaudio/best"
    }

    ydl_opts = {
        'format': fmt_map.get(qualidade, 'best'),
        'ffmpeg_location': caminho_ffmpeg,
        'outtmpl': os.path.join(pasta_download, '%(title)s.%(ext)s'),
        'progress_hooks': [progress_hook],
        'quiet': True,
        'no_warnings': True,

    }
    if qualidade == "Só áudio (MP3)":
        ydl_opts['postprocessors'] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
        }]
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        progress_var.set(100)
        status_var.set('✔ Download concluído com sucesso!')
        bar_widget.config(style='Success.Horizontal.TProgressbar')
        janela.after(0,lambda: messagebox.showinfo(
            'Sucesso', 'Download concluido!\nArquivo salvo na pasta atual.'))
    except Exception as e:
        progress_var.set(0)
        status_var.set('✖  Erro no download.')
        bar_widget.config(style='Error.Horizontal.TProgressbar')
        janela.after(0, lambda: messagebox.showerror('Erro', str(e)))

    finally:
        janela.after(0, lambda: btn_baixar.config(state='normal', text="BAIXAR"))

def escolher_pasta():
    global pasta_download
    pasta = filedialog.askdirectory()

    if pasta:
        pasta_download = pasta
        status_var.set(f"📁 Pasta: {pasta_download}")


def baixar_video():
    url = entrada.get().strip()
    if not url:
        messagebox.showerror('Erro','Cole um link primeiro! ')
        return

    qualidade = combo_qualidade.get()
    progress_var.set(0)
    status_var.set('⏳  Iniciando download…')
    bar_widget.config(style='Accent.Horizontal.TProgressbar')
    btn_baixar.config(state='disabled', text='BAIXANDO...')

    threading.Thread(
        target=_executar_download,
        args=(url, qualidade),
        daemon=True
    ).start()



#JANELA PRINCIPAL

janela = tk.Tk()
janela.title('AuVid')
icone_path = os.path.join(caminho_base, "favicon.ico")
janela.iconbitmap(icone_path)
janela.geometry('800x600')
janela.resizable(False, False)
janela.configure(bg=BG)


#VARIAVEIS TKINTER

progress_var = tk.DoubleVar(value=0)
status_var = tk.StringVar(value='Pronto para baixar.')


#ESTILOS TTK


style = ttk.Style()
style.theme_use('clam')


#BARRA PADRÃO (PROGRESSO)

style.configure(
    'Accent.Horizontal.TProgressbar',
    troughcolor=surface, bordercolor=border,
    background=accent, lightcolor=accent, darkcolor=accent,
    thickness=6

)

#BARRA DE SUCESSO
style.configure(
    'Success.Horizontal.TProgressbar',
    troughcolor=surface, background=success,
    lightcolor=success, darkcolor=success, thickness=6
)

#BARRA DE ERRO
style.configure(
    'Error.Horizontal.TProgressbar',
    troughcolor=surface, background=error,
    lightcolor=error, darkcolor=error, thickness=6,
)

#CABEÇALHO

header = tk.Frame(janela, bg=BG)
header.pack(fill='x', padx=30, pady=(28, 0))

tk.Label(
    header, text='AU', font=font_title,
    bg=BG, fg=accent
).pack(side='left')
tk.Label(
    header, text='VID', font=font_title,
    bg=BG, fg=text
).pack(side='left')

tk.Label(
    header, text="baixe qualquer video da internet",
    font=font_small, bg=BG, fg=muted
).pack(side='left', padx=(12, 0), pady=(8, 0))

#LINHA DECORATIVA

tk.Frame(janela, bg=border, height=1).pack(fill='x', padx=30,pady=(12, 0))


#CARD CENTRAL

card = tk.Frame(janela, bg=surface , bd=0, highlightthickness=1,
                highlightbackground=border)
card.pack(fill='x', padx=30, pady=20)



#LABEL URL

tk.Label(
    card, text='URL DO VÍDEO', font=font_small,
    bg=surface, fg=muted
).pack(anchor="w", padx=20, pady=(18, 4))



#FRAME DO CAMPO DE ENTRADA

entry_frame = tk.Frame(card, bg=accent, padx=1, pady=1)
entry_frame.pack(fill='x', padx=20)

entrada = tk.Entry(
    entry_frame,
    font=('Courier New', 11),
    bg='#1e1e1e', fg=text,
    insertbackground=accent,
    relief='flat', bd=6,
)

entrada.pack(fill='x')

#separador
tk.Frame(card, bg=border, height=1).pack(fill='x', padx=20, pady=12)


#LABEL QUALIDADE

tk.Label(
    card, text='Qualidade', font=font_small,
    bg=surface, fg=muted
).pack(anchor="w", padx=20, pady=(0, 4))



#COMBO QUALIDADE
style.configure(
    "Dark.TCombobox",
    fieldbackground="#1e1e1e",
    background="#1e1e1e",
    foreground=text,
    selectbackground=accent2,
    selectforeground=text,
    bordercolor=border,
    arrowcolor=accent,
)
style.map("Dark.TCombobox",
          fieldbackground=[('readonly', '#1e1e1e')],
          foreground=[('readonly', text)], 
)

combo_qualidade = ttk.Combobox(
    card,
    values=["Melhor qualidade", "1080p", "720p", "480p", "Só áudio (MP3)"],
    state="readonly",
    font=("Courier New", 10),
    style="Dark.TCombobox",
)

combo_qualidade.current(0)
combo_qualidade.pack(fill="x", padx=20, pady=(0, 18))

#BOTÂO BAIXAR
btn_baixar = tk.Button(
    janela,
    text="BAIXAR",
    font=font_btn,
    bg=accent, fg=BG,
    activebackground="#00b8cc",
    activeforeground=BG,
    relief='flat', bd=0,
    cursor='hand2',
    pady=10,
    command=baixar_video,
)
btn_baixar.pack(fill="x", padx=30)

btn_pasta = tk.Button(
    janela,
    text="ESCOLHER PASTA",
    font=font_small,
    bg=accent2,
    fg=text,
    activebackground=accent,
    activeforeground=BG,
    relief='flat',
    bd=0,
    highlightthickness=0,
    cursor='hand2',
    pady=10,
    command=escolher_pasta,
)
btn_pasta.pack(fill='x', padx=30, pady=(5, 0))

#barra de progresso

bar_widget = ttk.Progressbar(
    janela,
    variable=progress_var,
    maximum=100,
    style="Accent.Horizontal.TProgressbar",
)
bar_widget.pack(fill="x", padx=30, pady=(14, 4))

#STATUS

tk.Label(
    janela,
    textvariable=status_var,
    font=font_small,
    bg=BG, fg=muted,
    anchor="w",
).pack(fill="x", padx=30)

#RODAPÉ

tk.Label(
    janela,
    text="powered by yt-dlp",
    font=font_small,
    bg=BG, fg="#333333",
).pack(side="bottom", pady=8)





janela.mainloop()

              