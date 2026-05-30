"""
CodeAlpha Task 1: Language Translation Tool
Uses deep-translator (free, no API key needed) with a modern Tkinter UI
Install: pip install deep-translator pyttsx3 pyperclip
"""

import tkinter as tk
from tkinter import ttk, messagebox, font
import threading
try:
    from deep_translator import GoogleTranslator
    TRANSLATOR_AVAILABLE = True
except ImportError:
    TRANSLATOR_AVAILABLE = False

try:
    import pyttsx3
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False

try:
    import pyperclip
    CLIPBOARD_AVAILABLE = True
except ImportError:
    CLIPBOARD_AVAILABLE = False


# ── Language list ──────────────────────────────────────────────────────────────
LANGUAGES = {
    "Auto Detect": "auto",
    "Afrikaans": "af", "Albanian": "sq", "Amharic": "am",
    "Arabic": "ar", "Armenian": "hy", "Azerbaijani": "az",
    "Basque": "eu", "Belarusian": "be", "Bengali": "bn",
    "Bosnian": "bs", "Bulgarian": "bg", "Catalan": "ca",
    "Cebuano": "ceb", "Chinese (Simplified)": "zh-CN",
    "Chinese (Traditional)": "zh-TW", "Corsican": "co",
    "Croatian": "hr", "Czech": "cs", "Danish": "da",
    "Dutch": "nl", "English": "en", "Esperanto": "eo",
    "Estonian": "et", "Finnish": "fi", "French": "fr",
    "Frisian": "fy", "Galician": "gl", "Georgian": "ka",
    "German": "de", "Greek": "el", "Gujarati": "gu",
    "Haitian Creole": "ht", "Hausa": "ha", "Hawaiian": "haw",
    "Hebrew": "he", "Hindi": "hi", "Hmong": "hmn",
    "Hungarian": "hu", "Icelandic": "is", "Igbo": "ig",
    "Indonesian": "id", "Irish": "ga", "Italian": "it",
    "Japanese": "ja", "Javanese": "jv", "Kannada": "kn",
    "Kazakh": "kk", "Khmer": "km", "Kinyarwanda": "rw",
    "Korean": "ko", "Kurdish": "ku", "Kyrgyz": "ky",
    "Lao": "lo", "Latin": "la", "Latvian": "lv",
    "Lithuanian": "lt", "Luxembourgish": "lb", "Macedonian": "mk",
    "Malagasy": "mg", "Malay": "ms", "Malayalam": "ml",
    "Maltese": "mt", "Maori": "mi", "Marathi": "mr",
    "Mongolian": "mn", "Myanmar (Burmese)": "my", "Nepali": "ne",
    "Norwegian": "no", "Nyanja (Chichewa)": "ny", "Odia (Oriya)": "or",
    "Pashto": "ps", "Persian": "fa", "Polish": "pl",
    "Portuguese": "pt", "Punjabi": "pa", "Romanian": "ro",
    "Russian": "ru", "Samoan": "sm", "Scots Gaelic": "gd",
    "Serbian": "sr", "Sesotho": "st", "Shona": "sn",
    "Sindhi": "sd", "Sinhala": "si", "Slovak": "sk",
    "Slovenian": "sl", "Somali": "so", "Spanish": "es",
    "Sundanese": "su", "Swahili": "sw", "Swedish": "sv",
    "Tagalog (Filipino)": "tl", "Tajik": "tg", "Tamil": "ta",
    "Tatar": "tt", "Telugu": "te", "Thai": "th",
    "Turkish": "tr", "Turkmen": "tk", "Ukrainian": "uk",
    "Urdu": "ur", "Uyghur": "ug", "Uzbek": "uz",
    "Vietnamese": "vi", "Welsh": "cy", "Xhosa": "xh",
    "Yiddish": "yi", "Yoruba": "yo", "Zulu": "zu",
}

# ── Color palette ──────────────────────────────────────────────────────────────
BG        = "#0f1117"
CARD      = "#1a1d27"
ACCENT    = "#6c63ff"
ACCENT2   = "#ff6584"
TEXT      = "#e8e8f0"
SUBTEXT   = "#8888aa"
BORDER    = "#2a2d3e"
SUCCESS   = "#43d99e"
BTN_HV    = "#8079ff"


class TranslationApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("CodeAlpha — Language Translation Tool")
        self.geometry("900x680")
        self.configure(bg=BG)
        self.resizable(True, True)
        self.minsize(720, 540)

        self._tts_engine = None
        self._build_ui()

    # ── UI construction ────────────────────────────────────────────────────────
    def _build_ui(self):
        # Header
        hdr = tk.Frame(self, bg=BG, pady=18)
        hdr.pack(fill="x", padx=30)
        tk.Label(hdr, text="🌐  Language Translator",
                 bg=BG, fg=TEXT,
                 font=("Segoe UI", 22, "bold")).pack(side="left")
        tk.Label(hdr, text="CodeAlpha AI Internship · Task 1",
                 bg=BG, fg=SUBTEXT,
                 font=("Segoe UI", 10)).pack(side="right", anchor="s", pady=6)

        # Separator
        tk.Frame(self, bg=BORDER, height=1).pack(fill="x", padx=30)

        # Language selectors row
        lang_row = tk.Frame(self, bg=BG, pady=14)
        lang_row.pack(fill="x", padx=30)

        lang_names = list(LANGUAGES.keys())

        # Source
        tk.Label(lang_row, text="From", bg=BG, fg=SUBTEXT,
                 font=("Segoe UI", 9)).grid(row=0, column=0, sticky="w")
        self.src_var = tk.StringVar(value="Auto Detect")
        src_combo = self._make_combo(lang_row, self.src_var, lang_names)
        src_combo.grid(row=1, column=0, sticky="ew", padx=(0, 10))

        # Swap button
        swap_btn = tk.Button(lang_row, text="⇄", bg=CARD, fg=ACCENT,
                             font=("Segoe UI", 14), bd=0, relief="flat",
                             cursor="hand2", command=self._swap_languages,
                             activebackground=BORDER, activeforeground=ACCENT2)
        swap_btn.grid(row=1, column=1, padx=8)

        # Target
        tk.Label(lang_row, text="To", bg=BG, fg=SUBTEXT,
                 font=("Segoe UI", 9)).grid(row=0, column=2, sticky="w")
        self.tgt_var = tk.StringVar(value="Urdu")
        tgt_combo = self._make_combo(lang_row, self.tgt_var,
                                     [l for l in lang_names if l != "Auto Detect"])
        tgt_combo.grid(row=1, column=2, sticky="ew")

        lang_row.columnconfigure(0, weight=1)
        lang_row.columnconfigure(2, weight=1)

        # Text areas
        areas = tk.Frame(self, bg=BG)
        areas.pack(fill="both", expand=True, padx=30, pady=(0, 10))
        areas.columnconfigure(0, weight=1)
        areas.columnconfigure(1, weight=1)
        areas.rowconfigure(1, weight=1)

        # Input label + clear
        in_hdr = tk.Frame(areas, bg=BG)
        in_hdr.grid(row=0, column=0, sticky="ew", pady=(4, 4))
        tk.Label(in_hdr, text="Source Text", bg=BG, fg=SUBTEXT,
                 font=("Segoe UI", 9, "bold")).pack(side="left")
        tk.Button(in_hdr, text="✕ Clear", bg=BG, fg=SUBTEXT, bd=0,
                  font=("Segoe UI", 9), cursor="hand2",
                  command=self._clear_input,
                  activebackground=BG, activeforeground=ACCENT2).pack(side="right")

        self.input_text = tk.Text(areas, wrap="word", font=("Segoe UI", 12),
                                  bg=CARD, fg=TEXT, insertbackground=ACCENT,
                                  relief="flat", bd=0, padx=14, pady=12,
                                  highlightthickness=1,
                                  highlightcolor=ACCENT,
                                  highlightbackground=BORDER)
        self.input_text.grid(row=1, column=0, sticky="nsew", padx=(0, 8))
        self.input_text.bind("<Control-Return>", lambda e: self._translate())

        # Output label + action buttons
        out_hdr = tk.Frame(areas, bg=BG)
        out_hdr.grid(row=0, column=1, sticky="ew", pady=(4, 4))
        tk.Label(out_hdr, text="Translation", bg=BG, fg=SUBTEXT,
                 font=("Segoe UI", 9, "bold")).pack(side="left")
        if CLIPBOARD_AVAILABLE:
            tk.Button(out_hdr, text="📋 Copy", bg=BG, fg=SUBTEXT, bd=0,
                      font=("Segoe UI", 9), cursor="hand2",
                      command=self._copy_output,
                      activebackground=BG, activeforeground=SUCCESS).pack(side="right", padx=(6, 0))
        if TTS_AVAILABLE:
            tk.Button(out_hdr, text="🔊 Speak", bg=BG, fg=SUBTEXT, bd=0,
                      font=("Segoe UI", 9), cursor="hand2",
                      command=self._speak_output,
                      activebackground=BG, activeforeground=SUCCESS).pack(side="right")

        self.output_text = tk.Text(areas, wrap="word", font=("Segoe UI", 12),
                                   bg=CARD, fg=SUCCESS, insertbackground=ACCENT,
                                   relief="flat", bd=0, padx=14, pady=12,
                                   highlightthickness=1,
                                   highlightcolor=BORDER,
                                   highlightbackground=BORDER,
                                   state="disabled")
        self.output_text.grid(row=1, column=1, sticky="nsew", padx=(8, 0))

        # Bottom bar
        bot = tk.Frame(self, bg=BG, pady=14)
        bot.pack(fill="x", padx=30)

        self.status_var = tk.StringVar(value="Ready — press Translate or Ctrl+Enter")
        tk.Label(bot, textvariable=self.status_var, bg=BG, fg=SUBTEXT,
                 font=("Segoe UI", 9)).pack(side="left")

        self._translate_btn = tk.Button(
            bot, text="  Translate  ", bg=ACCENT, fg="white",
            font=("Segoe UI", 11, "bold"), bd=0, relief="flat",
            cursor="hand2", padx=20, pady=8,
            command=self._translate,
            activebackground=BTN_HV, activeforeground="white")
        self._translate_btn.pack(side="right")

        if not TRANSLATOR_AVAILABLE:
            self.status_var.set("⚠  deep-translator not installed — run: pip install deep-translator")

    def _make_combo(self, parent, var, values):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Dark.TCombobox",
                        fieldbackground=CARD, background=CARD,
                        foreground=TEXT, arrowcolor=ACCENT,
                        bordercolor=BORDER, lightcolor=BORDER,
                        darkcolor=BORDER, selectbackground=ACCENT,
                        selectforeground="white")
        cb = ttk.Combobox(parent, textvariable=var, values=values,
                          state="readonly", style="Dark.TCombobox",
                          font=("Segoe UI", 10))
        return cb

    # ── Actions ────────────────────────────────────────────────────────────────
    def _translate(self):
        if not TRANSLATOR_AVAILABLE:
            messagebox.showerror("Missing Library",
                                 "Install deep-translator:\n\npip install deep-translator")
            return
        text = self.input_text.get("1.0", "end").strip()
        if not text:
            self.status_var.set("⚠  Please enter some text to translate.")
            return
        self._translate_btn.config(state="disabled", text="  Translating…  ")
        self.status_var.set("Translating…")
        threading.Thread(target=self._do_translate, args=(text,), daemon=True).start()

    def _do_translate(self, text):
        try:
            src_name = self.src_var.get()
            tgt_name = self.tgt_var.get()
            src_code = LANGUAGES[src_name]
            tgt_code = LANGUAGES[tgt_name]

            translator = GoogleTranslator(source=src_code, target=tgt_code)
            result = translator.translate(text)

            self.after(0, self._show_result, result, src_name, tgt_name)
        except Exception as e:
            self.after(0, self._show_error, str(e))

    def _show_result(self, result, src, tgt):
        self.output_text.config(state="normal")
        self.output_text.delete("1.0", "end")
        self.output_text.insert("1.0", result)
        self.output_text.config(state="disabled")
        self.status_var.set(f"✓  Translated: {src} → {tgt}")
        self._translate_btn.config(state="normal", text="  Translate  ")

    def _show_error(self, msg):
        self.status_var.set(f"✗  Error: {msg}")
        self._translate_btn.config(state="normal", text="  Translate  ")

    def _swap_languages(self):
        src = self.src_var.get()
        tgt = self.tgt_var.get()
        if src != "Auto Detect":
            self.src_var.set(tgt)
            self.tgt_var.set(src)
            # Also swap text
            in_txt  = self.input_text.get("1.0", "end").strip()
            out_txt = self.output_text.get("1.0", "end").strip()
            self.input_text.delete("1.0", "end")
            self.input_text.insert("1.0", out_txt)
            self.output_text.config(state="normal")
            self.output_text.delete("1.0", "end")
            self.output_text.insert("1.0", in_txt)
            self.output_text.config(state="disabled")

    def _clear_input(self):
        self.input_text.delete("1.0", "end")
        self.output_text.config(state="normal")
        self.output_text.delete("1.0", "end")
        self.output_text.config(state="disabled")
        self.status_var.set("Cleared.")

    def _copy_output(self):
        text = self.output_text.get("1.0", "end").strip()
        if text:
            pyperclip.copy(text)
            self.status_var.set("✓  Copied to clipboard!")

    def _speak_output(self):
        text = self.output_text.get("1.0", "end").strip()
        if not text:
            return
        threading.Thread(target=self._tts, args=(text,), daemon=True).start()

    def _tts(self, text):
        try:
            engine = pyttsx3.init()
            engine.say(text)
            engine.runAndWait()
        except Exception as e:
            self.after(0, lambda: self.status_var.set(f"TTS error: {e}"))


if __name__ == "__main__":
    app = TranslationApp()
    app.mainloop()
