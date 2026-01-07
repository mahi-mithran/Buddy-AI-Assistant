"""
Buddy AI Assistant - Complete Working Version
"""

import tkinter as tk
from tkinter import scrolledtext, messagebox, filedialog, simpledialog
import datetime
import threading
import base64
from pathlib import Path
import requests
import json
import sys
import time
from collections import deque

if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

try:
    import speech_recognition as sr
    SR_AVAILABLE = True
except ImportError:
    SR_AVAILABLE = False

try:
    import pyttsx3
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False

try:
    import pywhatkit
    PYWHATKIT_AVAILABLE = True
except ImportError:
    PYWHATKIT_AVAILABLE = False

try:
    import wikipedia
    WIKI_AVAILABLE = True
except ImportError:
    WIKI_AVAILABLE = False

try:
    import pyjokes
    JOKES_AVAILABLE = True
except ImportError:
    JOKES_AVAILABLE = False

try:
    from google import genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

try:
    import PyPDF2
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


class AIAssistant:
    def __init__(self, root):
        self.root = root
        self.root.title("Buddy AI Assistant")
        self.root.geometry("1200x850")
        self.root.minsize(900, 600)
        
        self.bg_gradient = "#f8fafc"
        self.primary_color = "#4f46e5"
        self.secondary_color = "#7c3aed"
        self.accent_color = "#ec4899"
        self.success_color = "#10b981"
        self.warning_color = "#f59e0b"
        self.error_color = "#ef4444"
        self.text_bg = "#ffffff"
        self.text_fg = "#1e293b"
        self.sidebar_bg = "#ffffff"
        self.border_color = "#e2e8f0"
        self.root.configure(bg=self.bg_gradient)
        
        # Variables
        self.listener = sr.Recognizer() if SR_AVAILABLE else None
        self.uploaded_files = []
        self.file_contents = {}
        self.current_topic = "General Chat"
        self.chat_history = {}
        self.is_listening = False
        self.request_times = deque(maxlen=10)
        self.current_ai_model = tk.StringVar(value="gemini")
        
        self.ai_models = {
            "gemini": "Google Gemini",
            "groq": "Groq Llama 3.3",
            "huggingface": "HuggingFace Flan-T5"
        }
        
        self.connection_status = {
            "gemini": "unchecked",
            "groq": "unchecked",
            "huggingface": "unchecked"
        }
        
        # TTS
        if TTS_AVAILABLE:
            try:
                self.engine = pyttsx3.init()
                self.engine.setProperty("rate", 175)
                self.tts_var = tk.BooleanVar(value=True)
            except:
                self.engine = None
                self.tts_var = tk.BooleanVar(value=False)
        else:
            self.engine = None
            self.tts_var = tk.BooleanVar(value=False)
        
        self.init_ai_clients()
        self.setup_ui()
        self.create_menu_bar()
        self.load_history()
        self.root.after(300000, self.auto_save_history)
        self.root.after(1000, self.show_startup_diagnostics)
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def init_ai_clients(self):
        # Gemini
        self.gemini = None
        self.gemini_enabled = False
        self.gemini_api_key = "Type your api key"
        
        if GEMINI_AVAILABLE:
            try:
                self.gemini = genai.Client(api_key=self.gemini_api_key)
                self.gemini_enabled = True
                self.connection_status["gemini"] = "configured"
            except Exception as e:
                self.connection_status["gemini"] = f"error: {e}"
        else:
            self.connection_status["gemini"] = "library not installed"
        
        # Groq
        self.groq_api_key = "Type your api key"
        self.connection_status["groq"] = "configured"
        
        # HuggingFace
        self.hf_api_key = "Type your api key"
        self.connection_status["huggingface"] = "configured"

    def show_startup_diagnostics(self):
        diagnostics = []
        diagnostics.append(f"Python: {sys.version.split()[0]}")
        
        libs = {
            "google-genai": GEMINI_AVAILABLE,
            "PyPDF2": PDF_AVAILABLE,
            "PIL": PIL_AVAILABLE,
            "speech_recognition": SR_AVAILABLE,
            "pyttsx3": TTS_AVAILABLE,
        }
        
        for lib, available in libs.items():
            status = "[OK]" if available else "[MISSING]"
            diagnostics.append(f"{status} {lib}")
        
        diagnostics.append("\nAI Models:")
        for model, status in self.connection_status.items():
            if status == "configured":
                diagnostics.append(f"[OK] {self.ai_models[model]}")
            else:
                diagnostics.append(f"[ERR] {self.ai_models[model]} - {status}")
        
        self.add_message("system", "System Diagnostics:\n" + "\n".join(diagnostics))

    def test_api_connection(self, model):
        self.add_message("system", f"Testing {self.ai_models[model]}...")
        
        def test_thread():
            try:
                if model == "gemini":
                    result = self.test_gemini_connection()
                elif model == "groq":
                    result = self.test_groq_connection()
                elif model == "huggingface":
                    result = self.test_hf_connection()
                else:
                    result = ("error", "Unknown model")
                
                status, message = result
                if status == "success":
                    self.add_message("system", f"[OK] {self.ai_models[model]}: {message}")
                    self.connection_status[model] = "working"
                else:
                    self.add_message("system", f"[ERR] {self.ai_models[model]}: {message}")
            except Exception as e:
                self.add_message("system", f"[ERR] Test failed: {e}")
        
        threading.Thread(target=test_thread, daemon=True).start()

    def test_gemini_connection(self):
        if not GEMINI_AVAILABLE:
            return ("error", "google-genai not installed")
        try:
            response = self.gemini.models.generate_content(
                model="gemini-2.0-flash-exp",
                contents="Say 'ok' only"
            )
            return ("success", "Connected")
        except Exception as e:
            return ("error", str(e)[:50])

    def test_groq_connection(self):
        try:
            url = "https://api.groq.com/openai/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.groq_api_key}",
                "Content-Type": "application/json"
            }
            data = {
                "model": "llama-3.3-70b-versatile",
                "messages": [{"role": "user", "content": "Say ok"}],
                "max_tokens": 10
            }
            response = requests.post(url, headers=headers, json=data, timeout=15)
            response.raise_for_status()
            return ("success", "Connected")
        except Exception as e:
            return ("error", str(e)[:50])

    def test_hf_connection(self):
        try:
            url = "https://api-inference.huggingface.co/models/google/flan-t5-large"
            headers = {"Authorization": f"Bearer {self.hf_api_key}"}
            data = {"inputs": "Say ok"}
            response = requests.post(url, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            return ("success", "Connected")
        except Exception as e:
            return ("error", str(e)[:50])

    def read_file_content(self, file_path):
        try:
            file_ext = Path(file_path).suffix.lower()
            file_size = Path(file_path).stat().st_size
            
            if file_size > 5 * 1024 * 1024:
                return f"[File too large: {file_size / (1024*1024):.1f}MB]"
            
            if file_ext in ['.txt', '.md', '.py', '.js', '.java', '.cpp', '.json', '.csv']:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    return f.read(50000)
            elif file_ext == '.pdf' and PDF_AVAILABLE:
                with open(file_path, 'rb') as f:
                    pdf = PyPDF2.PdfReader(f)
                    text = ""
                    for i in range(min(5, len(pdf.pages))):
                        text += pdf.pages[i].extract_text()
                    return text[:50000]
            elif file_ext in ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp']:
                return f"[Image: {Path(file_path).name}]"
            else:
                return f"[File: {Path(file_path).name}]"
        except Exception as e:
            return f"[Error: {e}]"

    def upload_files(self):
        files = filedialog.askopenfilenames(title="Select Files")
        if files:
            self.uploaded_files = list(files)
            self.file_contents = {}
            for file_path in self.uploaded_files:
                content = self.read_file_content(file_path)
                self.file_contents[file_path] = content
            self.file_label.config(text=f"Files: {len(files)} attached")
            self.add_message("file", f"Attached {len(files)} file(s)")

    def show_file_preview(self):
        if not self.file_contents:
            return
        preview_window = tk.Toplevel(self.root)
        preview_window.title("File Preview")
        preview_window.geometry("700x500")
        preview_text = scrolledtext.ScrolledText(preview_window, wrap=tk.WORD)
        preview_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        for file_path, content in self.file_contents.items():
            preview_text.insert(tk.END, f"\n{'='*60}\n{Path(file_path).name}\n{'='*60}\n{content[:500]}\n")
        preview_text.config(state=tk.DISABLED)

    def clear_files(self):
        self.uploaded_files = []
        self.file_contents = {}
        self.file_label.config(text="No files")
        self.add_message("system", "Files cleared")

    def get_file_context(self):
        if not self.file_contents:
            return ""
        context = "\n\n=== FILES ===\n"
        for file_path, content in self.file_contents.items():
            context += f"\nFile: {Path(file_path).name}\n{content}\n"
        return context + "\n=== END FILES ===\n"

    def setup_ui(self):
        # Header
        header = tk.Frame(self.root, bg=self.primary_color, height=70)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        tk.Label(header, text="Buddy AI Assistant", font=("Segoe UI", 18, "bold"),
                bg=self.primary_color, fg="white").pack(pady=12)
        
        # Main
        main = tk.Frame(self.root, bg=self.bg_gradient)
        main.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)
        
        self.setup_sidebar(main)
        self.setup_chat_area(main)

    def setup_sidebar(self, parent):
        sidebar = tk.Frame(parent, bg=self.sidebar_bg, width=260)
        sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 12))
        sidebar.pack_propagate(False)
        
        tk.Label(sidebar, text="AI Model", font=("Segoe UI", 13, "bold"),
                bg=self.sidebar_bg).pack(pady=12, padx=12, anchor=tk.W)
        
        model_frame = tk.Frame(sidebar, bg=self.sidebar_bg)
        model_frame.pack(fill=tk.X, padx=12)
        
        for key, name in self.ai_models.items():
            tk.Radiobutton(model_frame, text=name, variable=self.current_ai_model,
                          value=key, bg=self.sidebar_bg, command=self.on_model_change).pack(anchor=tk.W)
        
        tk.Button(model_frame, text="Test Connection",
                 command=lambda: self.test_api_connection(self.current_ai_model.get()),
                 bg=self.warning_color, fg="white", relief=tk.FLAT).pack(fill=tk.X, pady=8)
        
        tk.Frame(sidebar, bg=self.border_color, height=1).pack(fill=tk.X, padx=12, pady=12)
        tk.Label(sidebar, text="Topics", font=("Segoe UI", 13, "bold"),
                bg=self.sidebar_bg).pack(padx=12, anchor=tk.W)
        
        topics_frame = tk.Frame(sidebar, bg=self.sidebar_bg)
        topics_frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=5)
        
        self.topics_listbox = tk.Listbox(topics_frame, font=("Segoe UI", 10),
                                         bg=self.text_bg, selectbackground=self.primary_color)
        self.topics_listbox.pack(fill=tk.BOTH, expand=True)
        
        for topic in ["General Chat", "Programming", "Creative", "Science"]:
            self.topics_listbox.insert(tk.END, topic)
            self.chat_history[topic] = []
        
        self.topics_listbox.select_set(0)
        self.topics_listbox.bind('<<ListboxSelect>>', self.on_topic_select)
        
        btn_frame = tk.Frame(sidebar, bg=self.sidebar_bg)
        btn_frame.pack(fill=tk.X, padx=12, pady=12)
        tk.Button(btn_frame, text="+ New", command=self.add_new_topic,
                 bg=self.primary_color, fg="white", relief=tk.FLAT).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)
        tk.Button(btn_frame, text="Delete", command=self.delete_topic,
                 bg=self.error_color, fg="white", relief=tk.FLAT).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)

    def setup_chat_area(self, parent):
        chat = tk.Frame(parent, bg=self.bg_gradient)
        chat.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Topic header
        header = tk.Frame(chat, bg=self.text_bg)
        header.pack(fill=tk.X, pady=(0, 8))
        self.topic_label = tk.Label(header, text="General Chat", font=("Segoe UI", 12, "bold"),
                                    bg=self.text_bg, fg=self.primary_color, padx=16, pady=10)
        self.topic_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.ai_indicator = tk.Label(header, text="Gemini", bg=self.text_bg, padx=16)
        self.ai_indicator.pack(side=tk.RIGHT)
        
        # Chat display
        self.chat_display = scrolledtext.ScrolledText(chat, wrap=tk.WORD, font=("Segoe UI", 10),
                                                      bg=self.text_bg, fg=self.text_fg, padx=16, pady=12,
                                                      height=15)
        self.chat_display.pack(fill=tk.BOTH, expand=True, pady=(0, 8))
        self.chat_display.config(state=tk.DISABLED)
        
        self.chat_display.tag_config("user", foreground=self.primary_color, font=("Segoe UI", 10, "bold"))
        self.chat_display.tag_config("buddy", foreground=self.secondary_color)
        self.chat_display.tag_config("system", foreground="#64748b", font=("Segoe UI", 9, "italic"))
        self.chat_display.tag_config("file", foreground=self.success_color)
        self.chat_display.tag_config("error", foreground=self.error_color)
        self.chat_display.tag_config("warning", foreground=self.warning_color)
        
        # Files
        file_frame = tk.Frame(chat, bg=self.text_bg)
        file_frame.pack(fill=tk.X, pady=(0, 8))
        self.file_label = tk.Label(file_frame, text="No files", bg=self.text_bg, padx=12, pady=6)
        self.file_label.pack(side=tk.LEFT)
        tk.Button(file_frame, text="Attach", command=self.upload_files,
                 bg=self.success_color, fg="white", relief=tk.FLAT, padx=12, pady=5).pack(side=tk.RIGHT, padx=4)
        tk.Button(file_frame, text="Preview", command=self.show_file_preview,
                 bg=self.warning_color, fg="white", relief=tk.FLAT, padx=12, pady=5).pack(side=tk.RIGHT, padx=4)
        tk.Button(file_frame, text="Clear", command=self.clear_files,
                 bg=self.error_color, fg="white", relief=tk.FLAT, padx=12, pady=5).pack(side=tk.RIGHT, padx=4)
        
        # Input
        input_frame = tk.Frame(chat, bg=self.text_bg)
        input_frame.pack(fill=tk.X)
        
        self.user_input = tk.Text(input_frame, height=4, font=("Segoe UI", 10),
                                 bg=self.text_bg, wrap=tk.WORD, padx=12, pady=10)
        self.user_input.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=12, pady=8)
        self.user_input.bind("<Return>", self.on_enter_key)
        
        btn_container = tk.Frame(input_frame, bg=self.text_bg)
        btn_container.pack(side=tk.RIGHT, padx=12, pady=8)
        
        tk.Button(btn_container, text="Send", command=self.send_message,
                 bg=self.primary_color, fg="white", font=("Segoe UI", 10, "bold"),
                 relief=tk.FLAT, padx=20, pady=10, width=8).pack(pady=(0, 4))
        
        if SR_AVAILABLE:
            self.voice_btn = tk.Button(btn_container, text="Voice", command=self.listen_voice,
                                      bg=self.accent_color, fg="white", font=("Segoe UI", 10, "bold"),
                                      relief=tk.FLAT, padx=20, pady=10, width=8)
            self.voice_btn.pack()

    def create_menu_bar(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Clear Chat", command=self.clear_chat)
        file_menu.add_command(label="Export Chat", command=self.export_chat)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        settings_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Settings", menu=settings_menu)
        settings_menu.add_checkbutton(label="Enable TTS", variable=self.tts_var)
        settings_menu.add_command(label="Test All", command=self.test_all_connections)
        
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)

    def add_message(self, sender, message):
        self.chat_display.config(state=tk.NORMAL)
        timestamp = datetime.datetime.now().strftime("%H:%M")
        
        if sender == "user":
            self.chat_display.insert(tk.END, f"\nYou ({timestamp})\n", "user")
        elif sender == "buddy":
            self.chat_display.insert(tk.END, f"\nBuddy ({timestamp})\n", "buddy")
        elif sender in ["system", "file", "error", "warning"]:
            self.chat_display.insert(tk.END, f"\n{sender.title()} ({timestamp})\n", sender)
        
        self.chat_display.insert(tk.END, f"{message}\n", sender if sender != "user" else "buddy")
        self.chat_display.see(tk.END)
        self.chat_display.config(state=tk.DISABLED)
        
        if self.current_topic in self.chat_history:
            self.chat_history[self.current_topic].append({
                "sender": sender, "message": message, "timestamp": timestamp
            })

    def on_enter_key(self, event):
        if not event.state & 0x1:
            self.send_message()
            return "break"

    def send_message(self):
        user_message = self.user_input.get("1.0", tk.END).strip()
        if not user_message:
            return
        
        self.user_input.delete("1.0", tk.END)
        self.add_message("user", user_message)
        
        if self.handle_commands(user_message):
            return
        
        threading.Thread(target=self.get_ai_response, args=(user_message,), daemon=True).start()

    def handle_commands(self, message):
        msg = message.lower()
        
        if "time" in msg:
            self.add_message("buddy", datetime.datetime.now().strftime("%I:%M %p"))
            return True
        if "date" in msg:
            self.add_message("buddy", datetime.datetime.now().strftime("%B %d, %Y"))
            return True
        if "joke" in msg and JOKES_AVAILABLE:
            self.add_message("buddy", pyjokes.get_joke())
            return True
        
        return False

    def get_conversation_context(self):
        if self.current_topic not in self.chat_history:
            return ""
        context = self.chat_history[self.current_topic][-5:]
        conversation = "\n".join([f"{msg['sender']}: {msg['message']}"
                                 for msg in context if msg['sender'] in ['user', 'buddy']])
        return f"\nConversation:\n{conversation}\n" if conversation else ""

    def get_ai_response(self, user_message):
        try:
            model = self.current_ai_model.get()
            file_context = self.get_file_context()
            conversation_context = self.get_conversation_context()
            full_message = conversation_context + file_context + "\n" + user_message
            
            self.add_message("system", f"Generating with {self.ai_models[model]}...")
            
            if model == "gemini":
                response = self.get_gemini_response(full_message)
            elif model == "groq":
                response = self.get_groq_response(full_message)
            elif model == "huggingface":
                response = self.get_hf_response(full_message)
            else:
                response = "Model not available"
            
            self.add_message("buddy", response)
            self.speak(response[:200])
        except Exception as e:
            self.add_message("error", f"Error: {str(e)[:100]}")

    def get_gemini_response(self, message):
        if not self.gemini_enabled:
            raise Exception("Gemini not available")
        try:
            response = self.gemini.models.generate_content(
                model="gemini-2.0-flash-exp",
                contents=message
            )
            return response.text
        except Exception as e:
            raise Exception(f"Gemini: {str(e)[:50]}")

    def get_groq_response(self, message):
        try:
            url = "https://api.groq.com/openai/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.groq_api_key}",
                "Content-Type": "application/json"
            }
            data = {
                "model": "llama-3.3-70b-versatile",
                "messages": [
                    {"role": "system", "content": "You are Buddy, a helpful assistant."},
                    {"role": "user", "content": message}
                ],
                "temperature": 0.7,
                "max_tokens": 2000
            }
            response = requests.post(url, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            return response.json()['choices'][0]['message']['content']
        except Exception as e:
            raise Exception(f"Groq: {str(e)[:50]}")

    def get_hf_response(self, message):
        try:
            url = "https://api-inference.huggingface.co/models/google/flan-t5-large"
            headers = {"Authorization": f"Bearer {self.hf_api_key}"}
            payload = {"inputs": f"Answer this question as Buddy assistant: {message}"}
            response = requests.post(url, headers=headers, json=payload, timeout=60)
            response.raise_for_status()
            result = response.json()
            if isinstance(result, list) and len(result) > 0:
                return result[0].get('generated_text', 'No response')
            return str(result)
        except Exception as e:
            raise Exception(f"HF: {str(e)[:50]}")

    def listen_voice(self):
        if not SR_AVAILABLE or self.is_listening:
            return
        self.is_listening = True
        self.voice_btn.config(text="Listening...", bg=self.error_color)
        self.add_message("system", "Listening...")
        
        def listen_thread():
            try:
                with sr.Microphone() as source:
                    self.listener.adjust_for_ambient_noise(source, duration=0.5)
                    audio = self.listener.listen(source, timeout=5, phrase_time_limit=10)
                text = self.listener.recognize_google(audio)
                self.add_message("user", text)
                self.user_input.insert("1.0", text)
            except Exception as e:
                self.add_message("warning", f"Voice error: {str(e)[:30]}")
            finally:
                self.is_listening = False
                self.voice_btn.config(text="Voice", bg=self.accent_color)
        
        threading.Thread(target=listen_thread, daemon=True).start()

    def speak(self, text):
        if not self.tts_var.get() or not self.engine:
            return
        def speak_thread():
            try:
                self.engine.say(text)
                self.engine.runAndWait()
            except:
                pass
        threading.Thread(target=speak_thread, daemon=True).start()

    def on_topic_select(self, event):
        selection = self.topics_listbox.curselection()
        if selection:
            self.switch_topic(self.topics_listbox.get(selection[0]))

    def switch_topic(self, topic):
        self.current_topic = topic
        self.topic_label.config(text=topic)
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.delete("1.0", tk.END)
        self.chat_display.config(state=tk.DISABLED)
        if topic in self.chat_history:
            for msg in self.chat_history[topic]:
                self.add_message(msg["sender"], msg["message"])

    def add_new_topic(self):
        topic = simpledialog.askstring("New Topic", "Enter topic name:")
        if topic:
            self.topics_listbox.insert(tk.END, topic)
            self.chat_history[topic] = []
            self.topics_listbox.selection_clear(0, tk.END)
            self.topics_listbox.select_set(tk.END)
            self.switch_topic(topic)

    def delete_topic(self):
        selection = self.topics_listbox.curselection()
        if not selection:
            return
        topic = self.topics_listbox.get(selection[0])
        if topic in ["General Chat", "Programming", "Creative", "Science"]:
            messagebox.showwarning("Warning", "Cannot delete default topics")
            return
        if messagebox.askyesno("Delete Topic", f"Delete '{topic}'?"):
            self.topics_listbox.delete(selection[0])
            if topic in self.chat_history:
                del self.chat_history[topic]
            self.topics_listbox.select_set(0)
            self.switch_topic(self.topics_listbox.get(0))

    def on_model_change(self):
        model = self.current_ai_model.get()
        self.ai_indicator.config(text=self.ai_models[model])
        self.add_message("system", f"Switched to {self.ai_models[model]}")

    def clear_chat(self):
        if messagebox.askyesno("Clear Chat", "Clear current topic chat history?"):
            self.chat_history[self.current_topic] = []
            self.chat_display.config(state=tk.NORMAL)
            self.chat_display.delete("1.0", tk.END)
            self.chat_display.config(state=tk.DISABLED)
            self.add_message("system", "Chat cleared")

    def export_chat(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(f"Buddy AI Chat Export - {self.current_topic}\n")
                    f.write(f"Exported: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
                    f.write("="*60 + "\n\n")
                    for msg in self.chat_history.get(self.current_topic, []):
                        f.write(f"[{msg['timestamp']}] {msg['sender'].upper()}: {msg['message']}\n\n")
                messagebox.showinfo("Success", "Chat exported successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Export failed: {e}")

    def test_all_connections(self):
        self.add_message("system", "Testing all AI models...")
        for model in self.ai_models.keys():
            time.sleep(0.5)
            self.test_api_connection(model)

    def show_about(self):
        about_text = """
Buddy AI Assistant v1.0

A powerful multi-model AI assistant with:
• Google Gemini Integration
• Groq Llama 3.3 Integration
• HuggingFace Llama Integration
• File Upload Support (PDF, Text, Code)
• Voice Input/Output
• Multi-Topic Chat Management
• Conversation Context Memory

Created with Python & Tkinter
        """
        messagebox.showinfo("About Buddy AI", about_text)

    def load_history(self):
        try:
            if Path("chat_history.json").exists():
                with open("chat_history.json", 'r', encoding='utf-8') as f:
                    loaded_history = json.load(f)
                    self.chat_history.update(loaded_history)
                    for topic in loaded_history.keys():
                        if topic not in [self.topics_listbox.get(i) for i in range(self.topics_listbox.size())]:
                            self.topics_listbox.insert(tk.END, topic)
                self.add_message("system", "Chat history loaded")
        except Exception as e:
            self.add_message("warning", f"Could not load history: {e}")

    def save_history(self):
        try:
            with open("chat_history.json", 'w', encoding='utf-8') as f:
                json.dump(self.chat_history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Save error: {e}")

    def auto_save_history(self):
        self.save_history()
        self.root.after(300000, self.auto_save_history)

    def on_closing(self):
        if messagebox.askokcancel("Quit", "Save chat history and exit?"):
            self.save_history()
            self.root.destroy()


def main():
    root = tk.Tk()
    app = AIAssistant(root)
    root.mainloop()


if __name__ == "__main__":
    main()