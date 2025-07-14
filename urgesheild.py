import tkinter as tk
from tkinter import messagebox
import datetime
import json
import os
import random
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.style as style

# ====== CONFIG ======
APPDATA_FOLDER = os.path.join(os.getenv('APPDATA'), "UrgeShield")
if not os.path.exists(APPDATA_FOLDER):
    os.makedirs(APPDATA_FOLDER)

PASSWORD_FILE = os.path.join(APPDATA_FOLDER, "password.txt")
DATA_FILE = os.path.join(APPDATA_FOLDER, "urgeshield_data.json")
COOLDOWN_DAYS = 2

# ====== STYLING ======
COLORS = {
    'bg': '#1e1e2e',
    'secondary_bg': '#313244',
    'accent': '#89b4fa',
    'success': '#a6e3a1',
    'warning': '#f9e2af',
    'error': '#f38ba8',
    'text': '#cdd6f4',
    'text_secondary': '#a6adc8',
    'purple': '#cba6f7',
    'surface': '#45475a'
}

FONTS = {
    'title': ('Segoe UI', 24, 'bold'),
    'heading': ('Segoe UI', 16, 'bold'),
    'body': ('Segoe UI', 12),
    'small': ('Segoe UI', 10),
    'quote': ('Segoe UI', 11, 'italic')
}

# ====== MOTIVATION ======
MOTIVATIONAL_QUOTES = [
    "You're not your past. You're building your future.",
    "Each day clean is a rep in the gym of self-mastery.",
    "You control the urge. The urge does NOT control you.",
    "Slip-ups don't define you—comebacks do.",
    "This fight? It's shaping you into something legendary.",
    "Progress, not perfection.",
    "Every moment is a fresh start.",
    "Your future self is counting on you.",
    "Strength grows from struggle.",
    "You've overcome 100% of your worst days so far."
]

# ====== UTILS ======

def load_password():
    if os.path.exists(PASSWORD_FILE):
        with open(PASSWORD_FILE, "r") as f:
            return f.read().strip()
    return None

def save_password(pw):
    with open(PASSWORD_FILE, "w") as f:
        f.write(pw)

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    else:
        return {
            "last_relapse": None,
            "next_allowed_date": None,
            "logs": []
        }

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

def days_since_last_relapse(last):
    if not last:
        return 0
    last_time = datetime.datetime.fromisoformat(last)
    delta = datetime.datetime.now() - last_time
    return delta.days

def create_modern_button(parent, text, command, bg_color=None, width=200, height=40):
    if bg_color is None:
        bg_color = COLORS['accent']
    
    frame = tk.Frame(parent, bg=COLORS['bg'])
    frame.pack(pady=8)
    
    button = tk.Button(
        frame,
        text=text,
        command=command,
        bg=bg_color,
        fg='black',
        font=FONTS['body'],
        relief='flat',
        bd=0,
        width=int(width/8),
        height=int(height/20),
        cursor='hand2'
    )
    button.pack()
    
    def on_enter(e):
        button.config(bg=lighten_color(bg_color))
    
    def on_leave(e):
        button.config(bg=bg_color)
    
    button.bind("<Enter>", on_enter)
    button.bind("<Leave>", on_leave)
    
    return button

def lighten_color(color):
    if color.startswith('#'):
        try:
            r = int(color[1:3], 16)
            g = int(color[3:5], 16)
            b = int(color[5:7], 16)
            r = min(255, r + 20)
            g = min(255, g + 20)
            b = min(255, b + 20)
            return f"#{r:02x}{g:02x}{b:02x}"
        except:
            return color
    return color

def show_streak_graph_embedded(parent, data):
    relapse_dates = [
        datetime.datetime.fromisoformat(log["timestamp"]) 
        for log in data["logs"] if log["type"] == "relapse"
    ]

    if not relapse_dates:
        return None

    streaks = []
    for i in range(len(relapse_dates) - 1):
        days = (relapse_dates[i + 1] - relapse_dates[i]).days
        streaks.append(days)

    if len(streaks) == 0:
        streaks.append((datetime.datetime.now() - relapse_dates[-1]).days)

    streaks.append(days_since_last_relapse(data["last_relapse"]))

    style.use('dark_background')
    fig, ax = plt.subplots(figsize=(6, 3))
    fig.patch.set_facecolor(COLORS['secondary_bg'])
    ax.set_facecolor(COLORS['secondary_bg'])
    
    ax.plot(streaks, marker='o', linestyle='-', color=COLORS['accent'], linewidth=2, markersize=6)
    ax.set_title("Streak Progress", color=COLORS['text'], fontsize=12, pad=10)
    ax.set_xlabel("Streak Number", color=COLORS['text_secondary'])
    ax.set_ylabel("Days", color=COLORS['text_secondary'])
    ax.grid(True, alpha=0.3, color=COLORS['surface'])
    ax.tick_params(colors=COLORS['text_secondary'])
    
    for spine in ax.spines.values():
        spine.set_color(COLORS['surface'])
    
    plt.tight_layout()
    
    canvas = FigureCanvasTkAgg(fig, parent)
    canvas.draw()
    return canvas.get_tk_widget()

# ====== APP CLASS ======

class UrgeShieldApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🛡️ UrgeShield")
        self.root.geometry("500x700")
        self.root.configure(bg=COLORS['bg'])
        self.root.resizable(False, False)
        
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.root.winfo_screenheight() // 2) - (700 // 2)
        self.root.geometry(f"500x700+{x}+{y}")
        
        self.data = load_data()
        self.quote = random.choice(MOTIVATIONAL_QUOTES)
        
        self.create_ui()
        self.update_streak()
        self.update_cooldown()

    def create_ui(self):
        main_frame = tk.Frame(self.root, bg=COLORS['bg'])
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        header_frame = tk.Frame(main_frame, bg=COLORS['secondary_bg'], relief='flat', bd=0)
        header_frame.pack(fill='x', pady=(0, 20))
        
        title_label = tk.Label(
            header_frame,
            text="🛡️ UrgeShield",
            font=FONTS['title'],
            fg=COLORS['accent'],
            bg=COLORS['secondary_bg']
        )
        title_label.pack(pady=20)
        
        streak_frame = tk.Frame(main_frame, bg=COLORS['secondary_bg'], relief='flat', bd=0)
        streak_frame.pack(fill='x', pady=(0, 15))
        
        self.streak_label = tk.Label(
            streak_frame,
            text="",
            font=FONTS['heading'],
            fg=COLORS['success'],
            bg=COLORS['secondary_bg']
        )
        self.streak_label.pack(pady=15)
        
        cooldown_frame = tk.Frame(main_frame, bg=COLORS['secondary_bg'], relief='flat', bd=0)
        cooldown_frame.pack(fill='x', pady=(0, 20))
        
        self.cooldown_label = tk.Label(
            cooldown_frame,
            text="",
            font=FONTS['body'],
            fg=COLORS['text_secondary'],
            bg=COLORS['secondary_bg']
        )
        self.cooldown_label.pack(pady=10)
        
        quote_frame = tk.Frame(main_frame, bg=COLORS['surface'], relief='flat', bd=0)
        quote_frame.pack(fill='x', pady=(0, 25))
        
        self.quote_label = tk.Label(
            quote_frame,
            text=self.quote,
            wraplength=400,
            justify="center",
            font=FONTS['quote'],
            fg=COLORS['text'],
            bg=COLORS['surface']
        )
        self.quote_label.pack(pady=20)
        
        buttons_frame = tk.Frame(main_frame, bg=COLORS['bg'])
        buttons_frame.pack(fill='x', pady=(0, 20))
        
        create_modern_button(buttons_frame, "💪 Log Urge Overcome", self.log_urge, COLORS['success'])
        create_modern_button(buttons_frame, "📝 Log Relapse", self.log_relapse, COLORS['error'])
        create_modern_button(buttons_frame, "🔄 Refresh Streak", self.update_streak, COLORS['accent'])


    def update_streak(self):
        streak = days_since_last_relapse(self.data["last_relapse"])
        emoji = "🔥" if streak > 0 else "🌱"
        max_streak = self.get_max_streak()
        self.streak_label.config(text=f"{emoji} Current Streak: {streak} days\n🏅 Max Streak: {max_streak} days")

        
        self.quote_label.config(text=random.choice(MOTIVATIONAL_QUOTES))

    def get_max_streak(self):
        relapse_dates = [
            datetime.datetime.fromisoformat(log["timestamp"]) 
            for log in self.data["logs"] if log["type"] == "relapse"
        ]

        if not relapse_dates:
            return days_since_last_relapse(self.data["last_relapse"])

        streaks = []
        for i in range(len(relapse_dates) - 1):
            streaks.append((relapse_dates[i + 1] - relapse_dates[i]).days)

        # Add current streak if it's the longest
        if self.data["last_relapse"]:
            current_streak = days_since_last_relapse(self.data["last_relapse"])
            streaks.append(current_streak)

        return max(streaks) if streaks else 0


    def update_cooldown(self):
        next_allowed = self.data.get("next_allowed_date")
        if next_allowed:
            date = datetime.datetime.fromisoformat(next_allowed)
            now = datetime.datetime.now()
            if now >= date:
                self.cooldown_label.config(
                    text="✅ You're clear. No cooldown active.",
                    fg=COLORS['success']
                )
            else:
                remaining = date - now
                self.cooldown_label.config(
                    text=f"⏳ Next release allowed in {remaining.days} day(s), {remaining.seconds//3600} hours",
                    fg=COLORS['warning']
                )
        else:
            self.cooldown_label.config(
                text="ℹ️ Cooldown not set.",
                fg=COLORS['text_secondary']
            )

    def log_urge(self):
        now = datetime.datetime.now().isoformat()
        self.data["logs"].append({"timestamp": now, "type": "urge"})
        save_data(self.data)
        
        messagebox.showinfo(
            "Well Done! 💪",
            "Urge logged successfully!\n\nYou showed incredible strength by not giving in. Each victory makes you stronger."
        )

    def log_relapse(self):
        response = messagebox.askyesno(
            "Confirm Relapse",
            "Are you sure you want to log a relapse?\n\nRemember: This is just data to help you improve."
        )
        
        if response:
            now = datetime.datetime.now()
            self.data["last_relapse"] = now.isoformat()
            self.data["logs"].append({"timestamp": now.isoformat(), "type": "relapse"})
            next_date = now + datetime.timedelta(days=COOLDOWN_DAYS)
            self.data["next_allowed_date"] = next_date.isoformat()
            save_data(self.data)
            
            self.update_streak()
            self.update_cooldown()
            
            messagebox.showinfo(
                "Relapse Logged 🤝",
                "It's okay. You're human, and you're learning.\n\nEvery setback is a setup for a comeback. Keep going!"
            )

    def toggle_graph(self):
        if self.graph_visible:
            self.graph_frame.pack_forget()
            self.graph_visible = False
        else:
            self.graph_widget = show_streak_graph_embedded(self.graph_frame, self.data)
            if self.graph_widget:
                self.graph_widget.pack(pady=10)
                self.graph_frame.pack(fill='x', pady=(10, 0))
                self.graph_visible = True
            else:
                messagebox.showinfo(
                    "No Data",
                    "Not enough data to display streak graph.\n\nKeep tracking your progress!"
                )

# ====== GUI Login Window ======

class LoginWindow:
    def __init__(self, master):
        self.master = master
        self.master.title("🔐 UrgeShield Login")
        self.master.geometry("400x300")
        self.master.configure(bg=COLORS['bg'])
        self.master.resizable(False, False)
        
        self.master.update_idletasks()
        x = (self.master.winfo_screenwidth() // 2) - (400 // 2)
        y = (self.master.winfo_screenheight() // 2) - (300 // 2)
        self.master.geometry(f"400x300+{x}+{y}")
        
        self.create_login_ui()

    def create_login_ui(self):
        main_frame = tk.Frame(self.master, bg=COLORS['bg'])
        main_frame.pack(fill='both', expand=True, padx=30, pady=30)
        
        header_frame = tk.Frame(main_frame, bg=COLORS['secondary_bg'], relief='flat', bd=0)
        header_frame.pack(fill='x', pady=(0, 30))
        
        title_label = tk.Label(
            header_frame,
            text="🔐 Access UrgeShield",
            font=FONTS['title'],
            fg=COLORS['accent'],
            bg=COLORS['secondary_bg']
        )
        title_label.pack(pady=20)
        
        password_frame = tk.Frame(main_frame, bg=COLORS['bg'])
        password_frame.pack(fill='x', pady=(0, 20))
        
        instruction_label = tk.Label(
            password_frame,
            text="Enter your password to continue:",
            font=FONTS['body'],
            fg=COLORS['text'],
            bg=COLORS['bg']
        )
        instruction_label.pack(pady=(0, 15))
        
        self.password_entry = tk.Entry(
            password_frame,
            show="*",
            width=25,
            font=FONTS['body'],
            bg=COLORS['secondary_bg'],
            fg=COLORS['text'],
            insertbackground=COLORS['text'],
            relief='flat',
            bd=10
        )
        self.password_entry.pack(pady=(0, 15))
        self.password_entry.focus()
        
        self.password_entry.bind('<Return>', lambda e: self.check_password())
        
        login_button = tk.Button(
            password_frame,
            text="🔓 Unlock",
            command=self.check_password,
            bg=COLORS['accent'],
            fg='white',
            font=FONTS['body'],
            relief='flat',
            bd=0,
            width=15,
            height=2,
            cursor='hand2'
        )
        login_button.pack(pady=(0, 15))
        
        def on_enter(e):
            login_button.config(bg=lighten_color(COLORS['accent']))
        
        def on_leave(e):
            login_button.config(bg=COLORS['accent'])
        
        login_button.bind("<Enter>", on_enter)
        login_button.bind("<Leave>", on_leave)
        
        self.error_label = tk.Label(
            password_frame,
            text="",
            fg=COLORS['error'],
            bg=COLORS['bg'],
            font=FONTS['small']
        )
        self.error_label.pack()

    def check_password(self):
        attempt = self.password_entry.get()
        stored_pw = load_password()
        if stored_pw is None:
            # Shouldn't happen, but fallback
            messagebox.showerror("Error", "No password set. Restart the app.")
            self.master.destroy()
            return
        
        if attempt == stored_pw:
            self.master.destroy()
            open_main_app()
        else:
            self.error_label.config(text="❌ Incorrect password. Please try again.")
            self.password_entry.delete(0, tk.END)
            self.password_entry.focus()

# ====== GUI Set Password Window ======

class SetPasswordWindow:
    def __init__(self, master):
        self.master = master
        self.master.title("🔐 Set Your Password")
        self.master.geometry("400x350")
        self.master.configure(bg=COLORS['bg'])
        self.master.resizable(False, False)
        
        self.master.update_idletasks()
        x = (self.master.winfo_screenwidth() // 2) - (400 // 2)
        y = (self.master.winfo_screenheight() // 2) - (350 // 2)
        self.master.geometry(f"400x350+{x}+{y}")
        
        self.create_ui()
    
    def create_ui(self):
        frame = tk.Frame(self.master, bg=COLORS['bg'])
        frame.pack(fill='both', expand=True, padx=30, pady=30)
        
        label = tk.Label(frame, text="Set a new password:", font=FONTS['heading'], fg=COLORS['accent'], bg=COLORS['bg'])
        label.pack(pady=10)
        
        self.pw_entry = tk.Entry(frame, show="*", font=FONTS['body'], bg=COLORS['secondary_bg'], fg=COLORS['text'], insertbackground=COLORS['text'], relief='flat', bd=10)
        self.pw_entry.pack(pady=10)
        self.pw_entry.focus()
        
        label2 = tk.Label(frame, text="Confirm password:", font=FONTS['heading'], fg=COLORS['accent'], bg=COLORS['bg'])
        label2.pack(pady=10)
        
        self.confirm_entry = tk.Entry(frame, show="*", font=FONTS['body'], bg=COLORS['secondary_bg'], fg=COLORS['text'], insertbackground=COLORS['text'], relief='flat', bd=10)
        self.confirm_entry.pack(pady=10)
        
        btn = tk.Button(frame, text="Set Password", command=self.set_password, bg=COLORS['accent'], fg='white', font=FONTS['body'], relief='flat', bd=0, width=15, height=2, cursor='hand2')
        btn.pack(pady=20)
        
        self.error_label = tk.Label(frame, text="", fg=COLORS['error'], bg=COLORS['bg'], font=FONTS['small'])
        self.error_label.pack()
    
    def set_password(self):
        pw = self.pw_entry.get()
        confirm = self.confirm_entry.get()
        if not pw or not confirm:
            self.error_label.config(text="Please fill both fields.")
            return
        if pw != confirm:
            self.error_label.config(text="Passwords do not match.")
            self.pw_entry.delete(0, tk.END)
            self.confirm_entry.delete(0, tk.END)
            self.pw_entry.focus()
            return
        
        save_password(pw)
        messagebox.showinfo("Success", "Password set! Please log in.")
        self.master.destroy()
        open_login_window()

# ====== STARTUP HELPERS ======

def open_login_window():
    login_root = tk.Tk()
    LoginWindow(login_root)
    login_root.mainloop()

def open_main_app():
    main_root = tk.Tk()
    UrgeShieldApp(main_root)
    main_root.mainloop()

# ====== MAIN ======

if __name__ == "__main__":
    if load_password() is None:
        # First launch, no password set yet
        root = tk.Tk()
        SetPasswordWindow(root)
        root.mainloop()
    else:
        open_login_window()
