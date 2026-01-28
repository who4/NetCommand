import customtkinter as ctk
import threading
import time
from network_manager import NetworkManager
from utils import elevate

# --- THEME CONFIGURATION (Gray/Purple/White) ---
COLOR_BG = "#181818"       # Dark Gray Background
COLOR_CARD = "#2b2b2b"     # Lighter Gray Card
COLOR_ACCENT = "#7b2cbf"   # Deep Purple (Buttons)
COLOR_ACCENT_HOVER = "#9d4edd" # Brighter Purple (Hover)
COLOR_TEXT = "#ffffff"     # White Text
COLOR_TEXT_DIM = "#b3b3b3" # Light Gray Text

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

class NetCommandApp(ctk.CTk):
    def __init__(self):
        elevate()
        super().__init__()

        self.title("NetCommand v4")
        self.geometry("1100x800")
        self.configure(fg_color=COLOR_BG)
        
        self.nm = NetworkManager()
        self.adapters = []
        self.selected_adapter = ctk.StringVar(value="")

        # Grid: 2 Rows, 2 Columns
        self.grid_columnconfigure((0, 1), weight=1, uniform="col")
        self.grid_rowconfigure((0, 1), weight=1, uniform="row")
        
        # Components
        self.create_connection_card(0, 0)
        self.create_stats_card(0, 1)
        self.create_dns_card(1, 0)
        self.create_tools_card(1, 1)

        # Status Bar
        self.status_bar = ctk.CTkLabel(self, text="System Ready", text_color=COLOR_TEXT_DIM, 
                                       fg_color="#101010", height=30, anchor="w", padx=15)
        self.status_bar.grid(row=2, column=0, columnspan=2, sticky="ew")

        # Startup
        self.refresh_adapters()
        self.update_stats()

    def create_card(self, row, col, title):
        frame = ctk.CTkFrame(self, fg_color=COLOR_CARD, corner_radius=12, border_width=0)
        frame.grid(row=row, column=col, padx=12, pady=12, sticky="nsew")
        
        lbl = ctk.CTkLabel(frame, text=title.upper(), font=("Segoe UI", 12, "bold"), text_color=COLOR_ACCENT_HOVER)
        lbl.pack(anchor="nw", padx=20, pady=(20, 10))
        return frame

    # --- 1. CONNECTION (Top Left) ---
    def create_connection_card(self, row, col):
        card = self.create_card(row, col, "Connection Priority")
        
        ctk.CTkLabel(card, text="Route all traffic through specific adapter.", 
                     text_color=COLOR_TEXT_DIM, font=("Segoe UI", 13)).pack(padx=20, anchor="w")

        self.adapter_menu = ctk.CTkOptionMenu(card, variable=self.selected_adapter,
                                              fg_color=COLOR_ACCENT, button_color=COLOR_ACCENT,
                                              button_hover_color=COLOR_ACCENT_HOVER,
                                              text_color=COLOR_TEXT,
                                              dropdown_fg_color=COLOR_CARD,
                                              font=("Segoe UI", 14), height=35)
        self.adapter_menu.pack(fill="x", padx=20, pady=(15, 10))

        self.connect_btn = ctk.CTkButton(card, text="CONNECT & PRIORITIZE", 
                                         command=self.prioritize_connection,
                                         fg_color=COLOR_ACCENT, hover_color=COLOR_ACCENT_HOVER,
                                         text_color=COLOR_TEXT,
                                         font=("Segoe UI", 15, "bold"),
                                         height=50, corner_radius=8)
        self.connect_btn.pack(fill="x", padx=20, pady=20, side="bottom")

    # --- 2. STATS (Top Right) ---
    def create_stats_card(self, row, col):
        card = self.create_card(row, col, "Live Network Monitor")
        
        container = ctk.CTkFrame(card, fg_color="transparent")
        container.pack(expand=True, fill="both", padx=20)
        
        def item(label, var_name):
            f = ctk.CTkFrame(container, fg_color=COLOR_BG, corner_radius=8)
            f.pack(fill="x", pady=4)
            ctk.CTkLabel(f, text=label, text_color=COLOR_TEXT_DIM, font=("Segoe UI", 11)).pack(side="left", padx=10, pady=8)
            l = ctk.CTkLabel(f, text="---", text_color=COLOR_TEXT, font=("Segoe UI", 14, "bold"))
            l.pack(side="right", padx=10)
            setattr(self, var_name, l)

        item("PUBLIC IP", "lbl_ip")
        item("LOCATION", "lbl_loc")
        item("ISP", "lbl_isp")
        item("PING (8.8.8.8)", "lbl_ping")
        item("PACKET LOSS", "lbl_loss")

    # --- 3. DNS (Bottom Left) ---
    def create_dns_card(self, row, col):
        card = self.create_card(row, col, "DNS Configuration")
        
        self.dns1 = ctk.CTkEntry(card, placeholder_text="Primary DNS", 
                                 fg_color=COLOR_BG, border_color=COLOR_BG, text_color=COLOR_TEXT, height=35)
        self.dns1.pack(fill="x", padx=20, pady=(10, 5))
        
        self.dns2 = ctk.CTkEntry(card, placeholder_text="Secondary DNS", 
                                 fg_color=COLOR_BG, border_color=COLOR_BG, text_color=COLOR_TEXT, height=35)
        self.dns2.pack(fill="x", padx=20, pady=(5, 15))
        
        grid = ctk.CTkFrame(card, fg_color="transparent")
        grid.pack(fill="x", padx=20)
        
        def btn(txt, cmd):
            ctk.CTkButton(grid, text=txt, command=cmd, fg_color=COLOR_ACCENT, hover_color=COLOR_ACCENT_HOVER, 
                          text_color=COLOR_TEXT, height=32).pack(fill="x", pady=3)

        btn("Apply Custom DNS", self.apply_dns)
        btn("Google DNS (8.8.8.8)", lambda: self.quick_dns("8.8.8.8", "8.8.4.4"))
        btn("Cloudflare DNS (1.1.1.1)", lambda: self.quick_dns("1.1.1.1", "1.0.0.1"))
        
        ctk.CTkButton(grid, text="Reset to Automatic", command=self.clear_dns,
                      fg_color="#333", hover_color="#444", text_color=COLOR_TEXT_DIM, height=32).pack(fill="x", pady=3)

    # --- 4. TOOLS (Bottom Right) ---
    def create_tools_card(self, row, col):
        card = self.create_card(row, col, "Quick Tools")
        
        grid = ctk.CTkFrame(card, fg_color="transparent")
        grid.pack(expand=True, fill="both", padx=20, pady=10)
        grid.columnconfigure((0, 1), weight=1)
        grid.rowconfigure((0, 1), weight=1)
        
        def tbtn(r, c, txt, cmd):
            ctk.CTkButton(grid, text=txt, command=cmd, 
                          fg_color=COLOR_BG, hover_color=COLOR_ACCENT_HOVER,
                          text_color=COLOR_TEXT, font=("Segoe UI", 13)).grid(row=r, column=c, padx=6, pady=6, sticky="nsew")

        tbtn(0, 0, "FLUSH DNS", self.flush_dns)
        tbtn(0, 1, "RELEASE IP", self.release_ip)
        tbtn(1, 0, "RENEW IP", self.renew_ip)
        tbtn(1, 1, "REFRESH UI", self.refresh_adapters)

    # --- LOGIC ---

    def set_status(self, msg):
        self.status_bar.configure(text=f" > {msg}")

    def refresh_adapters(self):
        self.adapters = self.nm.get_adapters()
        names = [a['Name'] for a in self.adapters] if self.adapters else ["No Adapters"]
        self.adapter_menu.configure(values=names)
        if names: self.selected_adapter.set(names[0])

    def update_stats(self):
        def _task():
            # 1. Ping Stats
            lat, loss = self.nm.get_connection_stats()
            self.lbl_ping.configure(text=lat)
            self.lbl_loss.configure(text=loss)
            
            # 2. Location Stats
            data = self.nm.get_location_info()
            if data:
                self.lbl_ip.configure(text=data.get('query', 'Unknown'))
                loc_str = f"{data.get('city', '')}, {data.get('country', '')}"
                self.lbl_loc.configure(text=loc_str)
                self.lbl_isp.configure(text=data.get('isp', 'Unknown'))
            else:
                self.lbl_ip.configure(text="Unavailable")
        
        threading.Thread(target=_task, daemon=True).start()
        self.after(15000, self.update_stats)

    def prioritize_connection(self):
        target = self.selected_adapter.get()
        if not target: return
        self.set_status(f"Prioritizing {target}...")
        threading.Thread(target=lambda: self.set_status(self.nm.prioritize_adapter(target).replace("\n", " | ")), daemon=True).start()

    def apply_dns(self):
        t, p, s = self.selected_adapter.get(), self.dns1.get().strip(), self.dns2.get().strip()
        if t and p:
            self.set_status(f"Setting DNS for {t}...")
            threading.Thread(target=lambda: self.set_status(self.nm.set_dns(t, p, s)), daemon=True).start()

    def quick_dns(self, p, s):
        self.dns1.delete(0, "end"); self.dns1.insert(0, p)
        self.dns2.delete(0, "end"); self.dns2.insert(0, s)
        self.apply_dns()

    def clear_dns(self):
        t = self.selected_adapter.get()
        self.set_status(f"Resetting DNS for {t}...")
        threading.Thread(target=lambda: self.set_status(self.nm.clear_dns(t)), daemon=True).start()

    def flush_dns(self):
        threading.Thread(target=lambda: self.set_status(self.nm.flush_dns()), daemon=True).start()

    def release_ip(self):
        threading.Thread(target=lambda: self.set_status(self.nm.release_ip(self.selected_adapter.get())), daemon=True).start()

    def renew_ip(self):
        self.set_status("Renewing IP (One moment)...")
        threading.Thread(target=lambda: self.set_status(self.nm.renew_ip(self.selected_adapter.get())), daemon=True).start()

if __name__ == "__main__":
    app = NetCommandApp()
    app.mainloop()
