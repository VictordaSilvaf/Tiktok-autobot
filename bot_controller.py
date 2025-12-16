#!/usr/bin/env python3
# bot_controller.py - Controlador do Bot de Automação TikTok

import datetime
import sys
import json
import os
import time
import threading
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
from pathlib import Path

# Import our bot functionality
from test import PROXY_RAW, extract_and_save_cookies, SB, fake
from test import COMMENTS

class TikTokBotGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Bot de Automação TikTok")
        self.root.geometry("800x600")
        self.root.minsize(800, 600)
        
        # Set style
        self.style = ttk.Style()
        self.style.configure("TButton", padding=6, relief="flat", background="#2a9d8f")
        self.style.configure("TNotebook", background="#264653")
        self.style.configure("TNotebook.Tab", padding=[12, 8], font=('Helvetica', 10))
        
        # Create notebook (tabs)
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create tab frames
        self.tab_main = ttk.Frame(self.notebook)
        self.tab_settings = ttk.Frame(self.notebook)
        self.tab_proxy = ttk.Frame(self.notebook)
        self.tab_comments = ttk.Frame(self.notebook)
        
        # Add frames to notebook
        self.notebook.add(self.tab_main, text="Principal")
        self.notebook.add(self.tab_settings, text="Configurações")
        self.notebook.add(self.tab_proxy, text="Proxies")
        self.notebook.add(self.tab_comments, text="Comentários")
        
        # Variables
        self.urls = []
        self.comments = []
        self.proxies = PROXY_RAW
        self.cookies_path = Path(r"C:\Users\Shahzeb\Desktop\Python\tiktok_bot\saved_cookies\cookies.JSON")
        self.running = False
        self.thread = None
        
        # Initialize each tab
        self.init_main_tab()
        self.init_settings_tab()
        self.init_proxy_tab()
        self.init_comments_tab()
        
        # Load saved settings
        self.load_settings()
        
    def init_main_tab(self):
        """Setup the main tab with URL input and controls"""
        frame = ttk.Frame(self.tab_main, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # URL input section
        url_frame = ttk.LabelFrame(frame, text="URLs dos Vídeos", padding="10")
        url_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Text widget for URLs
        self.url_text = scrolledtext.ScrolledText(url_frame, height=10)
        self.url_text.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # URL buttons
        url_btn_frame = ttk.Frame(url_frame)
        url_btn_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(url_btn_frame, text="Carregar URLs do Arquivo", command=self.load_urls).pack(side=tk.LEFT, padx=5)
        ttk.Button(url_btn_frame, text="Limpar URLs", command=self.clear_urls).pack(side=tk.LEFT, padx=5)
        
        # Status frame
        status_frame = ttk.LabelFrame(frame, text="Status", padding="10")
        status_frame.pack(fill=tk.BOTH, pady=10)
        
        self.status_text = scrolledtext.ScrolledText(status_frame, height=8)
        self.status_text.pack(fill=tk.BOTH, expand=True, pady=5)
        self.status_text.config(state=tk.DISABLED)
        
        # Control buttons
        control_frame = ttk.Frame(frame)
        control_frame.pack(fill=tk.X, pady=10)
        
        self.start_btn = ttk.Button(control_frame, text="Iniciar Bot", command=self.start_bot)
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_btn = ttk.Button(control_frame, text="Parar Bot", command=self.stop_bot, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        # Progress information
        self.progress_var = tk.StringVar(value="Pronto")
        self.progress_frame = ttk.Frame(frame)
        self.progress_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(self.progress_frame, text="Status:").pack(side=tk.LEFT, padx=5)
        ttk.Label(self.progress_frame, textvariable=self.progress_var).pack(side=tk.LEFT, padx=5)
        
        self.progress = ttk.Progressbar(frame, orient=tk.HORIZONTAL, length=100, mode='determinate')
        self.progress.pack(fill=tk.X, pady=5)
        
    def init_settings_tab(self):
        """Setup the settings tab"""
        frame = ttk.Frame(self.tab_settings, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Cookies section
        cookie_frame = ttk.LabelFrame(frame, text="Gerenciamento de Cookies", padding="10")
        cookie_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(cookie_frame, text="Arquivo de Cookie:").grid(row=0, column=0, sticky=tk.W, pady=5)
        
        cookie_path_frame = ttk.Frame(cookie_frame)
        cookie_path_frame.grid(row=0, column=1, sticky=tk.W, pady=5)
        
        self.cookie_path_var = tk.StringVar(value=str(self.cookies_path))
        ttk.Entry(cookie_path_frame, textvariable=self.cookie_path_var, width=40).pack(side=tk.LEFT, padx=5)
        ttk.Button(cookie_path_frame, text="Procurar", command=self.browse_cookie_file).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(cookie_frame, text="Extrair Novos Cookies", command=self.extract_cookies).grid(row=1, column=0, pady=10)
        ttk.Button(cookie_frame, text="Corrigir Formato de Cookie", command=self.fix_cookies).grid(row=1, column=1, pady=10)
        
        # Delay settings
        delay_frame = ttk.LabelFrame(frame, text="Configurações de Tempo", padding="10")
        delay_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(delay_frame, text="Atraso Mínimo (segundos):").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.min_delay_var = tk.DoubleVar(value=2.0)
        ttk.Spinbox(delay_frame, from_=0.5, to=10.0, increment=0.5, textvariable=self.min_delay_var, width=5).grid(row=0, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(delay_frame, text="Atraso Máximo (segundos):").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.max_delay_var = tk.DoubleVar(value=4.0)
        ttk.Spinbox(delay_frame, from_=1.0, to=15.0, increment=0.5, textvariable=self.max_delay_var, width=5).grid(row=1, column=1, sticky=tk.W, pady=5)
        
        # Operation settings
        op_frame = ttk.LabelFrame(frame, text="Configurações de Operação", padding="10")
        op_frame.pack(fill=tk.X, pady=10)
        
        # Checkboxes for actions
        self.like_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(op_frame, text="Curtir Vídeos", variable=self.like_var).grid(row=0, column=0, sticky=tk.W, pady=5)
        
        self.comment_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(op_frame, text="Postar Comentários", variable=self.comment_var).grid(row=0, column=1, sticky=tk.W, pady=5)
        
        self.share_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(op_frame, text="Compartilhar Vídeos", variable=self.share_var).grid(row=1, column=0, sticky=tk.W, pady=5)
        
        self.save_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(op_frame, text="Salvar Vídeos", variable=self.save_var).grid(row=1, column=1, sticky=tk.W, pady=5)
        
        # Save button
        ttk.Button(frame, text="Salvar Configurações", command=self.save_settings).pack(pady=10)
        
    def init_proxy_tab(self):
        """Setup the proxy tab"""
        frame = ttk.Frame(self.tab_proxy, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Proxy list
        proxy_frame = ttk.LabelFrame(frame, text="Lista de Proxies", padding="10")
        proxy_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Text widget for proxies
        self.proxy_text = scrolledtext.ScrolledText(proxy_frame)
        self.proxy_text.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Load initial proxies
        self.proxy_text.insert(tk.END, "\n".join(self.proxies))
        
        # Buttons
        btn_frame = ttk.Frame(proxy_frame)
        btn_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(btn_frame, text="Adicionar Proxy", command=self.add_proxy).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Remover Selecionado", command=self.remove_proxy).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Testar Proxies", command=self.test_proxies).pack(side=tk.LEFT, padx=5)
        
        # Format description
        ttk.Label(frame, text="Formato: IP,PORTA,USUÁRIO,SENHA - um proxy por linha").pack(pady=5)
        
    def init_comments_tab(self):
        """Setup the comments tab"""
        frame = ttk.Frame(self.tab_comments, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Comments list
        comments_frame = ttk.LabelFrame(frame, text="Modelos de Comentários", padding="10")
        comments_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Text widget for comments
        self.comments_text = scrolledtext.ScrolledText(comments_frame)
        self.comments_text.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Load default comments
        from test import COMMENTS
        self.comments_text.insert(tk.END, "\n".join(COMMENTS))
        
        # Buttons
        btn_frame = ttk.Frame(comments_frame)
        btn_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(btn_frame, text="Adicionar Comentário", command=self.add_comment).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Remover Selecionado", command=self.remove_comment).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Carregar do Arquivo", command=self.load_comments).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Salvar no Arquivo", command=self.save_comments).pack(side=tk.LEFT, padx=5)
        
    # ============== Action Methods ==============
    
    def log(self, message):
        """Adiciona mensagem ao log de status com timestamp."""
        
        # Captura a hora atual (ex: [14:01:44])
        timestamp = datetime.datetime.now().strftime("[%H:%M:%S]")
        
        # Formata a mensagem completa
        formatted_message = f"{timestamp} {message}\n"
        
        self.status_text.config(state=tk.NORMAL)
        self.status_text.insert(tk.END, formatted_message) # Insere a nova mensagem formatada
        self.status_text.see(tk.END)
        self.status_text.config(state=tk.DISABLED)
        self.root.update_idletasks()
    
    def browse_cookie_file(self):
        """Open file dialog to select cookie file"""
        filepath = filedialog.askopenfilename(
            title="Selecionar Arquivo de Cookie",
            filetypes=[("Arquivos JSON", "*.json"), ("Todos os Arquivos", "*.*")]
        )
        if filepath:
            self.cookie_path_var.set(filepath)
            self.cookies_path = Path(filepath)
    
    def load_urls(self):
        """Load URLs from a file"""
        filepath = filedialog.askopenfilename(
            title="Selecionar Lista de URLs",
            filetypes=[("Arquivos de Texto", "*.txt"), ("Todos os Arquivos", "*.*")]
        )
        if filepath:
            try:
                with open(filepath, 'r', encoding='utf-8') as file:
                    urls = [line.strip() for line in file if line.strip()]
                    self.url_text.delete(1.0, tk.END)
                    self.url_text.insert(tk.END, "\n".join(urls))
                self.log(f"{len(urls)} URLs carregadas do arquivo")
            except Exception as e:
                messagebox.showerror("Erro", f"Falha ao carregar URLs: {e}")
    
    def clear_urls(self):
        """Clear all URLs from the text box"""
        self.url_text.delete(1.0, tk.END)
    
    def extract_cookies(self):
        """Extract cookies from TikTok in a new browser session"""
        def extract_thread():
            try:
                self.log("Abrindo navegador para extrair cookies...")
                with SB(
                    uc=True,
                    incognito=False,
                    agent=fake.chrome(),
                    headless=False,
                ) as sb:
                    sb.open("https://www.tiktok.com/login")
                    self.log("Faça login no TikTok manualmente...")
                    self.log("A janela se fechará automaticamente após login bem-sucedido")
                    
                    # Wait for manual login
                    max_wait = 120  # 2 minutes
                    start_time = time.time()
                    logged_in = False
                    
                    while time.time() - start_time < max_wait:
                        # Check login status every 3 seconds
                        if sb.is_element_visible("//div[@data-e2e='top-avatar']") or \
                           sb.is_element_visible("//div[contains(text(),'Upload')]"):
                            logged_in = True
                            break
                        time.sleep(3)
                    
                    if logged_in:
                        self.log("Login detectado! Extraindo cookies...")
                        success = extract_and_save_cookies(sb, self.cookies_path)
                        if success:
                            self.log(f"✅ Cookies salvos em {self.cookies_path}")
                        else:
                            self.log("❌ Falha ao salvar cookies")
                    else:
                        self.log("⚠️ Tempo limite de login excedido ou login não detectado")
            
            except Exception as e:
                self.log(f"❌ Erro ao extrair cookies: {e}")
        
        # Run in thread to prevent UI freeze
        thread = threading.Thread(target=extract_thread)
        thread.daemon = True
        thread.start()
    
    def fix_cookies(self):
        """Fix cookie format issues"""
        try:
            if not self.cookies_path.exists():
                messagebox.showerror("Erro", f"Arquivo de cookie não encontrado: {self.cookies_path}")
                return
                
            with open(self.cookies_path, 'r', encoding='utf-8') as f:
                try:
                    cookies = json.load(f)
                except json.JSONDecodeError:
                    messagebox.showerror("Erro", "JSON inválido no arquivo de cookie")
                    return
            
            # Fix cookies
            required_fields = {"name", "value", "domain"}
            fixed_cookies = []
            
            for cookie in cookies:
                if not all(field in cookie for field in required_fields):
                    continue
                
                fixed_cookie = {
                    "name": cookie["name"],
                    "value": cookie["value"],
                    "domain": cookie["domain"],
                    "path": cookie.get("path", "/"),
                    "secure": cookie.get("secure", False),
                    "httpOnly": cookie.get("httpOnly", False)
                }
                
                if "expirationDate" in cookie:
                    fixed_cookie["expirationDate"] = cookie["expirationDate"]
                
                fixed_cookies.append(fixed_cookie)
            
            # Save fixed cookies
            backup_path = self.cookies_path.with_suffix(".backup.json")
            os.rename(self.cookies_path, backup_path)
            
            with open(self.cookies_path, 'w', encoding='utf-8') as f:
                json.dump(fixed_cookies, f, indent=2)
            
            self.log(f"✅ {len(fixed_cookies)} cookies corrigidos")
            self.log(f"Arquivo original salvo em: {backup_path}")
            
            messagebox.showinfo("Sucesso", f"{len(fixed_cookies)} cookies corrigidos")
        
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao corrigir cookies: {e}")
    
    def add_proxy(self):
        """Add a new proxy to the list"""
        from tkinter.simpledialog import askstring
        proxy = askstring("Adicionar Proxy", "Digite o proxy no formato: IP,PORTA,USUÁRIO,SENHA")
        if proxy:
            self.proxy_text.insert(tk.END, f"\n{proxy}")
    
    def remove_proxy(self):
        """Remove selected proxy"""
        try:
            selected = self.proxy_text.get(tk.SEL_FIRST, tk.SEL_LAST)
            if selected:
                content = self.proxy_text.get(1.0, tk.END)
                new_content = content.replace(selected, "")
                self.proxy_text.delete(1.0, tk.END)
                self.proxy_text.insert(tk.END, new_content)
        except tk.TclError:
            messagebox.showinfo("Informação", "Nenhum texto selecionado")
    
    def test_proxies(self):
        """Test if proxies are working"""
        def test_thread():
            proxies = self.proxy_text.get(1.0, tk.END).strip().split('\n')
            self.log(f"Testando {len(proxies)} proxies...")
            
            for i, proxy_str in enumerate(proxies):
                if not proxy_str.strip():
                    continue
                    
                try:
                    parts = proxy_str.split(',')
                    if len(parts) != 4:
                        self.log(f"⚠️ Formato inválido: {proxy_str}")
                        continue
                        
                    host, port, user, pwd = parts
                    proxy = f"{user}:{pwd}@{host}:{port}"
                    
                    self.log(f"Testando proxy {i+1}/{len(proxies)}: {host}")
                    
                    # Test with a quick browser session
                    with SB(
                        uc=True,
                        incognito=True,
                        agent=fake.chrome(),
                        proxy=proxy,
                        headless=True,
                        block_images=True
                    ) as sb:
                        sb.open("https://api.ipify.org")
                        ip = sb.get_text("body")
                        self.log(f"✅ Proxy {host} funcionando: {ip}")
                
                except Exception as e:
                    self.log(f"❌ Proxy {proxy_str} falhou: {e}")
        
        # Run in thread to prevent UI freeze
        thread = threading.Thread(target=test_thread)
        thread.daemon = True
        thread.start()
    
    def add_comment(self):
        """Add a new comment template"""
        from tkinter.simpledialog import askstring
        comment = askstring("Adicionar Comentário", "Digite o modelo de comentário:")
        if comment:
            self.comments_text.insert(tk.END, f"\n{comment}")
    
    def remove_comment(self):
        """Remove selected comment"""
        try:
            selected = self.comments_text.get(tk.SEL_FIRST, tk.SEL_LAST)
            if selected:
                content = self.comments_text.get(1.0, tk.END)
                new_content = content.replace(selected, "")
                self.comments_text.delete(1.0, tk.END)
                self.comments_text.insert(tk.END, new_content)
        except tk.TclError:
            messagebox.showinfo("Informação", "Nenhum texto selecionado")
    
    def load_comments(self):
        """Load comments from a file"""
        filepath = filedialog.askopenfilename(
            title="Selecionar Arquivo de Comentários",
            filetypes=[("Arquivos de Texto", "*.txt"), ("Todos os Arquivos", "*.*")]
        )
        if filepath:
            try:
                with open(filepath, 'r', encoding='utf-8') as file:
                    comments = file.read()
                    self.comments_text.delete(1.0, tk.END)
                    self.comments_text.insert(tk.END, comments)
                self.log(f"Comentários carregados do arquivo")
            except Exception as e:
                messagebox.showerror("Erro", f"Falha ao carregar comentários: {e}")
    
    def save_comments(self):
        """Save comments to a file"""
        filepath = filedialog.asksaveasfilename(
            title="Salvar Comentários",
            defaultextension=".txt",
            filetypes=[("Arquivos de Texto", "*.txt"), ("Todos os Arquivos", "*.*")]
        )
        if filepath:
            try:
                with open(filepath, 'w', encoding='utf-8') as file:
                    comments = self.comments_text.get(1.0, tk.END)
                    file.write(comments)
                self.log(f"Comentários salvos em {filepath}")
            except Exception as e:
                messagebox.showerror("Erro", f"Falha ao salvar comentários: {e}")
    
    def save_settings(self):
        """Save current settings to a file"""
        try:
            settings = {
                "cookies_path": str(self.cookies_path),
                "min_delay": self.min_delay_var.get(),
                "max_delay": self.max_delay_var.get(),
                "like": self.like_var.get(),
                "comment": self.comment_var.get(),
                "share": self.share_var.get(),
                "save": self.save_var.get(),
                "proxies": self.proxy_text.get(1.0, tk.END).strip().split('\n'),
                "comments": self.comments_text.get(1.0, tk.END).strip().split('\n')
            }
            
            with open("bot_settings.json", 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2)
                
            messagebox.showinfo("Sucesso", "Configurações salvas com sucesso")
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao salvar configurações: {e}")
    
    def load_settings(self):
        """Load settings from file"""
        try:
            if not os.path.exists("bot_settings.json"):
                return
                
            with open("bot_settings.json", 'r', encoding='utf-8') as f:
                settings = json.load(f)
                
            if "cookies_path" in settings:
                self.cookies_path = Path(settings["cookies_path"])
                self.cookie_path_var.set(str(self.cookies_path))
                
            if "min_delay" in settings:
                self.min_delay_var.set(settings["min_delay"])
                
            if "max_delay" in settings:
                self.max_delay_var.set(settings["max_delay"])
                
            if "like" in settings:
                self.like_var.set(settings["like"])
                
            if "comment" in settings:
                self.comment_var.set(settings["comment"])
                
            if "share" in settings:
                self.share_var.set(settings["share"])
                
            if "save" in settings:
                self.save_var.set(settings["save"])
                
            if "proxies" in settings:
                self.proxies = settings["proxies"]
                self.proxy_text.delete(1.0, tk.END)
                self.proxy_text.insert(tk.END, "\n".join(self.proxies))
                
            if "comments" in settings:
                self.comments = settings["comments"]
                self.comments_text.delete(1.0, tk.END)
                self.comments_text.insert(tk.END, "\n".join(self.comments))
                
            self.log("Configurações carregadas com sucesso")
        except Exception as e:
            self.log(f"Falha ao carregar configurações: {e}")
    
    def start_bot(self):
        """Start the bot process"""
        # Get URLs
        urls = [url.strip() for url in self.url_text.get(1.0, tk.END).split('\n') if url.strip()]
        if not urls:
            messagebox.showerror("Erro", "Nenhuma URL fornecida")
            return
        
        # Get comments
        comments = [c.strip() for c in self.comments_text.get(1.0, tk.END).split('\n') if c.strip()]
        if not comments:
            messagebox.showwarning("Aviso", "Nenhum comentário fornecido. O bot continuará sem comentar.")
        
        # Get proxies
        proxies = [p.strip() for p in self.proxy_text.get(1.0, tk.END).split('\n') if p.strip()]
        if not proxies:
            if not messagebox.askyesno("Aviso", "Nenhum proxy especificado. Executar sem proxies?"):
                return
        
        # Update global variables in test.py
        import test
        if comments:
            test.COMMENTS = comments
        if proxies:
            test.PROXY_RAW = proxies
        
        # Update delay settings
        test.DELAY = (self.min_delay_var.get(), self.max_delay_var.get())
        
        # Update cookie file path
        test.COOKIE_FILE = self.cookies_path
        
        # Disable start button, enable stop button
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        
        # Set progress variables
        self.progress_var.set("Executando")
        self.progress["maximum"] = len(urls)
        self.progress["value"] = 0
        
        self.running = True
        
        # Log start
        self.log(f"Iniciando bot com {len(urls)} URLs")
        self.log(f"Usando {len(proxies)} proxies")
        self.log(f"Usando intervalo de atraso: {test.DELAY[0]}-{test.DELAY[1]} segundos")
        
        # Run in separate thread
        self.thread = threading.Thread(target=self.bot_thread, args=(urls,))
        self.thread.daemon = True
        self.thread.start()
    
    def bot_thread(self, urls):
        """Execute bot in separate thread"""
        try:
            remaining = urls[:]
            processed = 0
            
            # Import necessary functions
            from test import run_all
            
            # Process URLs in batches to allow stopping
            batch_size = min(5, len(urls))
            
            while remaining and self.running:
                batch = remaining[:batch_size]
                
                # Log current batch
                self.log(f"Processando lote de {len(batch)} URLs...")
                
                try:
                    run_all(batch)
                except Exception as e:
                    self.log(f"Erro durante a execução: {e}")
                
                # Update progress
                processed += len(batch)
                remaining = remaining[batch_size:]
                
                # Update UI in main thread
                self.root.after(0, lambda: self.update_progress(processed, len(urls)))
                
                # Check if we should continue
                if not self.running:
                    self.log("Bot parado pelo usuário")
                    break
            
            # Completed all URLs
            if not remaining and self.running:
                self.log("✅ Bot concluiu o processamento de todas as URLs")
                self.root.after(0, self.bot_finished)
            
        except Exception as e:
            self.log(f"❌ Erro fatal: {e}")
            self.root.after(0, lambda: self.handle_error(str(e)))
    
    def update_progress(self, processed, total):
        """Update progress UI elements"""
        self.progress["value"] = processed
        self.progress_var.set(f"Processados: {processed}/{total}")
    
    def bot_finished(self):
        """Handle bot completion"""
        self.running = False
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.progress_var.set("Concluído")
        messagebox.showinfo("Concluído", "O bot terminou de processar todas as URLs")
    
    def handle_error(self, error_msg):
        """Handle bot errors"""
        self.running = False
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.progress_var.set("Erro")
        messagebox.showerror("Erro", f"O bot encontrou um erro: {error_msg}")
    
    def stop_bot(self):
        """Stop the bot process"""
        if messagebox.askyesno("Confirmar", "Tem certeza de que deseja parar o bot?"):
            self.log("Parando bot...")
            self.running = False
            self.stop_btn.config(state=tk.DISABLED)

if __name__ == "__main__":
    root = tk.Tk()
    app = TikTokBotGUI(root)
    root.mainloop()
