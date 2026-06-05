# ---------------------------------------------------------
# PdfSynk - Ferramenta Oficial HubSynk
# Versão: V.1.2
# Desenvolvido por: saulomgg (https://github.com/saulomgg)
#
# Este software faz parte do ecossistema HubSynk.
# Apoie o projeto, acesse meu portfólio e ajude a manter
# o desenvolvimento e atualizações constantes!
# ---------------------------------------------------------

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import sys
import webbrowser
from pathlib import Path
from pypdf import PdfReader, PdfWriter
from utils.constants import *
from utils.helpers import open_url
from core.pdf_logic import PdfProcessor

class PdfSynkApp:
    def __init__(self, root):
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry("900x850")
        self.root.configure(bg=BG_DARK)
        
        # Variáveis de estado
        self.current_file_path = None
        self.pdf_reader = None
        self.page_count = 0
        self.merge_files = []
        self.img_to_pdf_files = []
        
        # Configurar ícone
        self.set_window_icon()
        
        # UI
        self.setup_ui()

    def set_window_icon(self):
        try:
            if getattr(sys, 'frozen', False):
                base_path = sys._MEIPASS
            else:
                base_path = os.path.abspath(".")
            icon_path = os.path.join(base_path, "assets", "logo.png")
            if os.path.exists(icon_path):
                img = tk.PhotoImage(file=icon_path)
                self.root.iconphoto(True, img)
            if os.name == 'nt':
                import ctypes
                myappid = 'hubsynk.pdfsynk.editor.1.2'
                ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        except: pass

    def setup_ui(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TNotebook", background=BG_DARK, borderwidth=0)
        style.configure("TNotebook.Tab", background=BG_MEDIUM, foreground=FG_LIGHT, padding=[10, 5])
        style.map("TNotebook.Tab", background=[("selected", COLOR_PRIMARY)])
        style.configure("TFrame", background=BG_MEDIUM)
        style.configure("Accent.TButton", background=COLOR_PRIMARY, foreground=FG_LIGHT, font=("Arial", 10, "bold"))
        style.map("Accent.TButton", background=[("active", "#1976D2")])
        style.configure("TLabel", background=BG_MEDIUM, foreground=FG_LIGHT)
        style.configure("Treeview", background=BG_CARD, foreground=FG_LIGHT, fieldbackground=BG_CARD)
        style.map('Treeview', background=[('selected', COLOR_SUCCESS)])

        main_frame = tk.Frame(self.root, bg=BG_DARK, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Cabeçalho com Logo e Título
        header_frame = tk.Frame(main_frame, bg=BG_DARK)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        title_label = tk.Label(header_frame, text="📄 PdfSynk", font=("Arial", 28, "bold"), bg=BG_DARK, fg=COLOR_PRIMARY)
        title_label.pack(side=tk.LEFT)
        
        subtitle_label = tk.Label(header_frame, text=" - Editor Profissional", font=("Arial", 14, "italic"), bg=BG_DARK, fg=FG_SECONDARY)
        subtitle_label.pack(side=tk.LEFT, padx=10, pady=(10, 0))

        self.file_info_var = tk.StringVar(value=NO_FILE_SELECTED)
        tk.Label(main_frame, textvariable=self.file_info_var, font=("Arial", 10), bg=BG_DARK, fg=FG_SECONDARY).pack(pady=(0, 10))

        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        self.setup_extraction_tab()
        self.setup_merge_tab()
        self.setup_advanced_tab()
        self.setup_security_tab()

        self.setup_footer(main_frame)

    def setup_extraction_tab(self):
        frame = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(frame, text="Extração/Divisão")
        ttk.Button(frame, text="📁 Carregar PDF", command=self.load_pdf, style="Accent.TButton").pack(pady=10)
        options_frame = ttk.Frame(frame)
        options_frame.pack(fill=tk.X, pady=10)
        ttk.Label(options_frame, text="Páginas (Ex: 1, 3-5):", font=("Arial", 10, "bold")).pack(anchor=tk.W)
        self.extraction_input_var = tk.StringVar()
        ttk.Entry(options_frame, textvariable=self.extraction_input_var).pack(fill=tk.X, pady=5)
        self.extraction_mode_var = tk.StringVar(value="single")
        ttk.Radiobutton(options_frame, text="Único PDF (Junção)", variable=self.extraction_mode_var, value="single").pack(anchor=tk.W)
        ttk.Radiobutton(options_frame, text="PDFs Separados (Divisão)", variable=self.extraction_mode_var, value="multiple").pack(anchor=tk.W)
        ttk.Button(frame, text="🚀 Processar", command=self.process_extraction, style="Accent.TButton").pack(pady=20)

    def setup_merge_tab(self):
        frame = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(frame, text="Junção")
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill=tk.X, pady=10)
        ttk.Button(btn_frame, text="➕ Adicionar", command=self.add_merge_files, style="Accent.TButton").pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="🗑️ Remover", command=self.remove_merge_file).pack(side=tk.LEFT, padx=5)
        self.merge_tree = ttk.Treeview(frame, columns=("path",), show="headings", height=8)
        self.merge_tree.heading("path", text="Arquivo")
        self.merge_tree.pack(fill=tk.BOTH, expand=True, pady=10)
        ttk.Button(frame, text="🔗 Juntar PDFs", command=self.process_merge, style="Accent.TButton").pack(pady=20)

    def setup_advanced_tab(self):
        frame = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(frame, text="Avançado")
        adv_nb = ttk.Notebook(frame)
        adv_nb.pack(fill=tk.BOTH, expand=True)
        
        # Rotação
        rot_f = ttk.Frame(adv_nb, padding=10)
        adv_nb.add(rot_f, text="Rotação")
        ttk.Label(rot_f, text="Páginas (Vazio=Todas):").pack(anchor=tk.W)
        self.rotation_pages_var = tk.StringVar()
        ttk.Entry(rot_f, textvariable=self.rotation_pages_var).pack(fill=tk.X, pady=5)
        ttk.Label(rot_f, text="Ângulo:").pack(anchor=tk.W)
        self.rotation_angle_var = tk.StringVar(value="90")
        ttk.Combobox(rot_f, textvariable=self.rotation_angle_var, values=["90", "180", "270"], state="readonly").pack(anchor=tk.W, pady=5)
        ttk.Button(rot_f, text="🔄 Rotacionar", command=self.process_rotation, style="Accent.TButton").pack(pady=10)

        # Marca D'água
        wat_f = ttk.Frame(adv_nb, padding=10)
        adv_nb.add(wat_f, text="Marca D'água")
        ttk.Label(wat_f, text="Selecione um PDF de 1 página para usar como marca:").pack(anchor=tk.W)
        ttk.Button(wat_f, text="💧 Aplicar Marca", command=self.process_watermark, style="Accent.TButton").pack(pady=10)

        # Imagem para PDF
        img_f = ttk.Frame(adv_nb, padding=10)
        adv_nb.add(img_f, text="Imagem -> PDF")
        ttk.Button(img_f, text="➕ Adicionar Imagens", command=self.add_img_files).pack(pady=5)
        self.img_tree = ttk.Treeview(img_f, columns=("path",), show="headings", height=5)
        self.img_tree.heading("path", text="Imagem")
        self.img_tree.pack(fill=tk.BOTH, expand=True)
        ttk.Button(img_f, text="🖼️ Converter", command=self.process_img_to_pdf, style="Accent.TButton").pack(pady=10)

        # Compactação (NOVA FUNÇÃO PROFISSIONAL)
        comp_f = ttk.Frame(adv_nb, padding=10)
        adv_nb.add(comp_f, text="Compactar")
        ttk.Label(comp_f, text="Reduz o tamanho do arquivo PDF otimizando imagens e conteúdo.", wraplength=400).pack(pady=10)
        ttk.Button(comp_f, text="📉 Compactar PDF", command=self.process_compression, style="Accent.TButton").pack(pady=10)

    def setup_security_tab(self):
        frame = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(frame, text="Segurança")
        sec_nb = ttk.Notebook(frame)
        sec_nb.pack(fill=tk.BOTH, expand=True)

        # Proteção
        prot_f = ttk.Frame(sec_nb, padding=10)
        sec_nb.add(prot_f, text="Proteger")
        ttk.Label(prot_f, text="Senha de Abertura:").pack(anchor=tk.W)
        self.pass_var = tk.StringVar()
        ttk.Entry(prot_f, textvariable=self.pass_var, show="*").pack(fill=tk.X, pady=5)
        ttk.Button(prot_f, text="🔒 Proteger", command=self.process_protect, style="Accent.TButton").pack(pady=10)

        # Metadados
        meta_f = ttk.Frame(sec_nb, padding=10)
        sec_nb.add(meta_f, text="Metadados")
        self.meta_vars = {k: tk.StringVar() for k in ["Title", "Author", "Subject", "Keywords"]}
        for k, v in self.meta_vars.items():
            ttk.Label(meta_f, text=f"{k}:").pack(anchor=tk.W)
            ttk.Entry(meta_f, textvariable=v).pack(fill=tk.X, pady=2)
        ttk.Button(meta_f, text="📝 Atualizar", command=self.process_metadata, style="Accent.TButton").pack(pady=10)

    def setup_footer(self, parent):
        footer = tk.Frame(parent, bg=BG_DARK)
        footer.pack(fill=tk.X, side=tk.BOTTOM, pady=(20, 0))
        
        info_frame = tk.Frame(footer, bg=BG_DARK)
        info_frame.pack(fill=tk.X)
        
        tk.Label(info_frame, text="Desenvolvido profissionalmente por saulomgg |", font=("Arial", 10, "bold"), bg=BG_DARK, fg="#999999").pack(side=tk.LEFT)
        
        github_link = tk.Label(info_frame, text="GitHub", font=("Arial", 10, "bold", "underline"), bg=BG_DARK, fg=COLOR_PRIMARY, cursor="hand2")
        github_link.pack(side=tk.LEFT, padx=5)
        github_link.bind("<Button-1>", lambda e: open_url("https://github.com/saulomgg"))
        
        # Botões de Ajuda e Suporte (Padrão VideoSynk)
        btn_frame = tk.Frame(footer, bg=BG_DARK)
        btn_frame.pack(fill=tk.X, pady=(10, 0))
        
        tk.Button(btn_frame, text="ℹ️ Sobre", command=self.open_about, font=("Arial", 9, "bold"), bg="#444444", fg="white", bd=0, padx=10, pady=3, cursor="hand2").pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="🎁 Suporte / Doação", command=self.open_support, font=("Arial", 9, "bold"), bg=COLOR_ACCENT, fg=BG_DARK, bd=0, padx=10, pady=3, cursor="hand2").pack(side=tk.LEFT, padx=5)

    def open_about(self):
        about_win = tk.Toplevel(self.root)
        about_win.title("Sobre PdfSynk - HubSynk")
        about_win.geometry("550x500")
        about_win.resizable(False, False)
        about_win.configure(bg="#1e1e1e")
        about_win.transient(self.root)
        about_win.grab_set()
        
        try:
            from PIL import Image, ImageTk
            if getattr(sys, 'frozen', False):
                base_path = sys._MEIPASS
            else:
                base_path = os.path.abspath(".")
            logo_path = os.path.join(base_path, "assets", "logo.png")
            if os.path.exists(logo_path):
                pil_img = Image.open(logo_path)
                pil_img = pil_img.resize((120, 120), Image.Resampling.LANCZOS)
                img = ImageTk.PhotoImage(pil_img)
                logo_label = tk.Label(about_win, image=img, bg="#1e1e1e")
                logo_label.image = img
                logo_label.pack(pady=10)
        except Exception as e:
            print(f"Erro ao carregar logo: {e}")

        tk.Label(about_win, text="🔷 HUBSYNK ECOSYSTEM", font=("Consolas", 14, "bold"), bg="#1e1e1e", fg=COLOR_PRIMARY).pack(pady=(10, 10))
        tk.Label(about_win, text="PdfSynk v1.2", font=("Segoe UI", 16, "bold"), bg="#1e1e1e", fg="white").pack(pady=5)
        
        desc_text = (
            "Esta é uma ferramenta oficial do ecossistema HubSynk.\n\n"
            "O HubSynk foi criado para centralizar e automatizar tarefas "
            "do dia a dia, garantindo segurança e produtividade.\n\n"
            "O desenvolvimento e atualizações constantes dependem da "
            "interação da comunidade. Apoie o projeto!"
        )
        tk.Label(about_win, text=desc_text, font=("Segoe UI", 10), bg="#1e1e1e", fg="#cccccc", wraplength=450, justify="center").pack(pady=15)
        
        links_frame = tk.Frame(about_win, bg="#1e1e1e")
        links_frame.pack(pady=10)
        
        def create_link_btn(text, url, color=COLOR_PRIMARY):
            btn = tk.Button(links_frame, text=text, font=("Segoe UI", 10, "bold", "underline"), bg="#1e1e1e", fg=color,
                         activebackground="#1e1e1e", activeforeground="white", bd=0, cursor="hand2",
                         command=lambda: webbrowser.open_new(url))
            btn.pack(pady=3)

        create_link_btn("🔗 Link do HubSynk", "https://github.com/saulomgg/HubSynk")
        create_link_btn("📂 Link do GitHub / Portfólio", "https://github.com/saulomgg")
        
        tk.Label(about_win, text="O desenvolvimento e atualização do programa depende da sua interação e apoio!", 
                 font=("Segoe UI", 9, "italic"), bg="#1e1e1e", fg=COLOR_ACCENT, wraplength=400).pack(pady=10)
        
        tk.Button(about_win, text="Fechar", command=about_win.destroy, bg="#333333", fg="white", 
               relief="flat", padx=20, pady=5, cursor="hand2").pack(pady=15)

    def open_support(self):
        webbrowser.open("https://github.com/saulomgg/HubSynk/releases")

    def load_pdf(self):
        path = filedialog.askopenfilename(filetypes=[("PDF", "*.pdf")])
        if path:
            try:
                self.current_file_path = path
                self.pdf_reader = PdfReader(path)
                self.page_count = len(self.pdf_reader.pages)
                self.file_info_var.set(f"Arquivo: {Path(path).name} | Páginas: {self.page_count}")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao carregar PDF: {e}")

    def process_extraction(self):
        if not self.pdf_reader: return
        indices = PdfProcessor.parse_page_selection(self.extraction_input_var.get(), self.page_count)
        if not indices: return
        if self.extraction_mode_var.get() == "single":
            writer = PdfProcessor.extract_pages(self.pdf_reader, indices)
            save_path = filedialog.asksaveasfilename(defaultextension=".pdf")
            if save_path:
                with open(save_path, "wb") as f: writer.write(f)
                messagebox.showinfo("Sucesso", "PDF Extraído!")
        else:
            base_path = filedialog.askdirectory()
            if base_path:
                for idx in indices:
                    writer = PdfProcessor.extract_pages(self.pdf_reader, [idx])
                    out_name = f"{Path(self.current_file_path).stem}_p{idx+1}.pdf"
                    with open(Path(base_path)/out_name, "wb") as f: writer.write(f)
                messagebox.showinfo("Sucesso", "Páginas Divisíveis Salvas!")

    def add_merge_files(self):
        paths = filedialog.askopenfilenames(filetypes=[("PDF", "*.pdf")])
        for p in paths:
            self.merge_files.append(p)
            self.merge_tree.insert("", "end", values=(p,))

    def remove_merge_file(self):
        selected = self.merge_tree.focus()
        if selected:
            idx = self.merge_tree.index(selected)
            del self.merge_files[idx]
            self.merge_tree.delete(selected)

    def process_merge(self):
        if not self.merge_files: return
        writer = PdfProcessor.merge_pdfs(self.merge_files)
        save_path = filedialog.asksaveasfilename(defaultextension=".pdf")
        if save_path:
            with open(save_path, "wb") as f: writer.write(f)
            messagebox.showinfo("Sucesso", "PDFs Agrupados!")

    def process_rotation(self):
        if not self.pdf_reader: return
        indices = PdfProcessor.parse_page_selection(self.rotation_pages_var.get(), self.page_count)
        if not indices: indices = list(range(self.page_count))
        writer = PdfProcessor.rotate_pages(self.pdf_reader, indices, int(self.rotation_angle_var.get()))
        save_path = filedialog.asksaveasfilename(defaultextension=".pdf")
        if save_path:
            with open(save_path, "wb") as f: writer.write(f)
            messagebox.showinfo("Sucesso", "PDF Rotacionado!")

    def process_watermark(self):
        if not self.pdf_reader: return
        w_path = filedialog.askopenfilename(filetypes=[("PDF", "*.pdf")], title="Selecione a Marca D'água (1 pág)")
        if w_path:
            w_reader = PdfReader(w_path)
            writer = PdfProcessor.apply_watermark(self.pdf_reader, w_reader, list(range(self.page_count)))
            save_path = filedialog.asksaveasfilename(defaultextension=".pdf")
            if save_path:
                with open(save_path, "wb") as f: writer.write(f)
                messagebox.showinfo("Sucesso", "Marca D'água Aplicada!")

    def add_img_files(self):
        paths = filedialog.askopenfilenames(filetypes=[("Imagens", "*.jpg *.png *.jpeg")])
        for p in paths:
            self.img_to_pdf_files.append(p)
            self.img_tree.insert("", "end", values=(p,))

    def process_img_to_pdf(self):
        if not self.img_to_pdf_files: return
        pdf_data = PdfProcessor.images_to_pdf(self.img_to_pdf_files)
        save_path = filedialog.asksaveasfilename(defaultextension=".pdf")
        if save_path:
            with open(save_path, "wb") as f: f.write(pdf_data)
            messagebox.showinfo("Sucesso", "Imagens Convertidas!")

    def process_protect(self):
        if not self.pdf_reader or not self.pass_var.get(): return
        writer = PdfProcessor.protect_pdf(self.pdf_reader, self.pass_var.get())
        save_path = filedialog.asksaveasfilename(defaultextension=".pdf")
        if save_path:
            with open(save_path, "wb") as f: writer.write(f)
            messagebox.showinfo("Sucesso", "PDF Protegido!")

    def process_metadata(self):
        if not self.pdf_reader: return
        meta = {k: v.get() for k, v in self.meta_vars.items()}
        writer = PdfProcessor.update_metadata(self.pdf_reader, meta)
        save_path = filedialog.asksaveasfilename(defaultextension=".pdf")
        if save_path:
            with open(save_path, "wb") as f: writer.write(f)
            messagebox.showinfo("Sucesso", "Metadados Atualizados!")

    def process_compression(self):
        if not self.pdf_reader: return
        writer = PdfProcessor.compress_pdf(self.pdf_reader)
        save_path = filedialog.asksaveasfilename(defaultextension=".pdf", initialfile="PdfSynk_Compressed.pdf")
        if save_path:
            with open(save_path, "wb") as f: writer.write(f)
            messagebox.showinfo("Sucesso", "PDF Compactado com Sucesso!")
