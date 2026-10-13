import os
import time
import tkinter as tk
from tkinter import ttk, messagebox
from backend.m1_pesanan import Array, LinkList, Pesanan, muat_data_csv

class AppUI:
    def __init__(self, root):
        self.root = root
        self.root.title("2EZ4U Food Delivery")
        self.root.geometry("1100x720")
        self.root.minsize(950, 600)

        # Path data pesanan CSV
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.csv_path = os.path.join(base_dir, "data", "pesanan.csv")

        # Struktur data
        self.array_data = Array()
        self.linked_list_data = LinkList()

        # State mode aktif
        self.active_mode = "ARRAY - TAMBAH PESANAN REGULER"

        # Pagination state
        self.page_size = 50
        self.current_page = 0

        self.setup_styles()
        self.create_layout()

        # Auto-load CSV data saat aplikasi pertama kali dibuka
        self.load_csv_data(silent_on_success=True)

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview.Heading", font=("Arial", 9, "bold"))
        style.configure("Treeview", font=("Arial", 9), rowheight=22)

    def create_layout(self):
        # Container utama
        main_container = tk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True)

        # ------------------ PANEL KIRI: SIDEBAR MENU ------------------
        sidebar_frame = tk.Frame(main_container, width=250, bg="#f0f0f0", relief=tk.GROOVE, borderwidth=1)
        sidebar_frame.pack(side=tk.LEFT, fill=tk.Y, padx=0, pady=0)
        sidebar_frame.pack_propagate(False)

        # Canvas dengan Scrollbar untuk sidebar agar muat semua tombol
        canvas = tk.Canvas(sidebar_frame, bg="#f0f0f0", highlightthickness=0)
        scrollbar = tk.Scrollbar(sidebar_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#f0f0f0")

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", width=230)
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Bagian DATA
        lbl_data = tk.Label(scrollable_frame, text="DATA", font=("Arial", 10, "bold"), bg="#f0f0f0", anchor="w")
        lbl_data.pack(fill=tk.X, padx=10, pady=(8, 2))

        btn_load = tk.Button(scrollable_frame, text="Load Data CSV", bg="#e1e1e1", activebackground="#d0d0d0",
                             font=("Arial", 9), command=self.on_click_load, cursor="hand2")
        btn_load.pack(fill=tk.X, padx=10, pady=2)

        ttk.Separator(scrollable_frame, orient="horizontal").pack(fill=tk.X, padx=10, pady=8)

        # Bagian M1 - DATA PESANAN
        lbl_m1 = tk.Label(scrollable_frame, text="M1 - DATA PESANAN", font=("Arial", 9, "bold"), bg="#f0f0f0", anchor="w")
        lbl_m1.pack(fill=tk.X, padx=10, pady=(2, 4))

        m1_menus = [
            ("ARRAY - LIHAT PESANAN", lambda: self.select_menu("ARRAY - LIHAT PESANAN")),
            ("ARRAY - TAMBAH PESANAN REGULER", lambda: self.select_menu("ARRAY - TAMBAH PESANAN REGULER")),
            ("ARRAY - TAMBAH PESANAN PRIORITAS", lambda: self.select_menu("ARRAY - TAMBAH PESANAN PRIORITAS")),
            ("ARRAY - TAMBAH PESANAN VIP", lambda: self.select_menu("ARRAY - TAMBAH PESANAN VIP")),
            ("ARRAY - HAPUS PESANAN", lambda: self.select_menu("ARRAY - HAPUS PESANAN")),
            ("LINKEDLIST - LIHAT PESANAN", lambda: self.select_menu("LINKEDLIST - LIHAT PESANAN")),
            ("LINKEDLIST - TAMBAH PESANAN REGULER", lambda: self.select_menu("LINKEDLIST - TAMBAH PESANAN REGULER")),
            ("LINKEDLIST - TAMBAH PESANAN PRIORITAS", lambda: self.select_menu("LINKEDLIST - TAMBAH PESANAN PRIORITAS")),
            ("LINKEDLIST - TAMBAH PESANAN VIP", lambda: self.select_menu("LINKEDLIST - TAMBAH PESANAN VIP")),
            ("LINKEDLIST - HAPUS PESANAN", lambda: self.select_menu("LINKEDLIST - HAPUS PESANAN")),
        ]

        self.sidebar_buttons = {}
        for text, cmd in m1_menus:
            btn = tk.Button(scrollable_frame, text=text, font=("Arial", 8), bg="#ffffff",
                            relief=tk.RAISED, anchor="w", padx=6, pady=2, command=cmd, cursor="hand2")
            btn.pack(fill=tk.X, padx=10, pady=2)
            self.sidebar_buttons[text] = btn

        ttk.Separator(scrollable_frame, orient="horizontal").pack(fill=tk.X, padx=10, pady=8)

        # Milestone Placeholder (Sesuai referensi PDF)
        placeholders = [
            ("M2 - ANTREAN DAN UNDO", ["Isi antrean FIFO", "Layani berikutnya", "Undo"]),
            ("M3 DAN M4 - LAPORAN & SEARCH", ["Laporan harian", "Cari di laporan", "Bangun indeks hash", "Cari pesanan (oid)"]),
            ("M5 - KATALOG & PRIORITAS", ["Menu per rentang harga", "Isi antrean prioritas"]),
            ("M6 - PETA DAN RUTE", ["Muat peta", "Cari rute terpendek"])
        ]

        for section_title, submenus in placeholders:
            lbl_sec = tk.Label(scrollable_frame, text=section_title, font=("Arial", 8, "bold"), fg="#888888", bg="#f0f0f0", anchor="w")
            lbl_sec.pack(fill=tk.X, padx=10, pady=(6, 2))
            for sub in submenus:
                btn_ph = tk.Button(scrollable_frame, text=sub, font=("Arial", 8), bg="#f8f8f8", fg="#999999",
                                   anchor="w", padx=6, pady=1, state=tk.DISABLED)
                btn_ph.pack(fill=tk.X, padx=10, pady=1)

        # ------------------ PANEL KANAN: WORKSPACE ------------------
        right_container = tk.Frame(main_container, bg="#ffffff")
        right_container.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # 1. Header & Deskripsi Form
        self.header_frame = tk.Frame(right_container, bg="#f9f9f9", padx=15, pady=10, relief=tk.RIDGE, borderwidth=1)
        self.header_frame.pack(fill=tk.X, padx=10, pady=(10, 5))

        self.lbl_title = tk.Label(self.header_frame, text="Array: pesanan REGULER, masuk paling belakang",
                                  font=("Arial", 12, "bold"), bg="#f9f9f9", anchor="w")
        self.lbl_title.pack(fill=tk.X)

        self.lbl_subtitle = tk.Label(self.header_frame, text="Menambahkan data pesanan reguler di antrean paling belakang",
                                     font=("Arial", 9), fg="#555555", bg="#f9f9f9", anchor="w")
        self.lbl_subtitle.pack(fill=tk.X, pady=(2, 0))

        # 2. Form Parameter Dinamis
        self.form_frame = tk.Frame(right_container, bg="#ffffff", padx=15, pady=8)
        self.form_frame.pack(fill=tk.X, padx=10, pady=5)
        self.build_form_inputs()

        # 3. Tabel Tampilan Data (Treeview)
        table_container = tk.Frame(right_container, bg="#ffffff")
        table_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Header info total data & paginasi
        nav_frame = tk.Frame(table_container, bg="#ffffff")
        nav_frame.pack(fill=tk.X, pady=(0, 4))

        self.lbl_status_data = tk.Label(nav_frame, text="Memuat data...", font=("Arial", 9, "bold"), bg="#ffffff")
        self.lbl_status_data.pack(side=tk.LEFT)

        # Tombol Navigasi Halaman
        btn_first = tk.Button(nav_frame, text="<<", width=3, command=self.page_first)
        btn_first.pack(side=tk.RIGHT, padx=1)
        btn_next = tk.Button(nav_frame, text=">", width=3, command=self.page_next)
        btn_next.pack(side=tk.RIGHT, padx=1)
        self.lbl_page_info = tk.Label(nav_frame, text="Hal 1 / 1", font=("Arial", 9), bg="#ffffff")
        self.lbl_page_info.pack(side=tk.RIGHT, padx=6)
        btn_prev = tk.Button(nav_frame, text="<", width=3, command=self.page_prev)
        btn_prev.pack(side=tk.RIGHT, padx=1)
        btn_last = tk.Button(nav_frame, text=">>", width=3, command=self.page_last)
        btn_last.pack(side=tk.RIGHT, padx=1)

        # Treeview dengan scrollbar vertikal & horizontal
        columns = ("oid", "pelanggan", "resto", "menu", "harga", "prioritas", "t_masuk", "t_selesai", "status")
        self.tree = ttk.Treeview(table_container, columns=columns, show="headings", height=10)

        self.tree.heading("oid", text="OID")
        self.tree.heading("pelanggan", text="Pelanggan")
        self.tree.heading("resto", text="Restoran")
        self.tree.heading("menu", text="Menu")
        self.tree.heading("harga", text="Harga")
        self.tree.heading("prioritas", text="Prioritas")
        self.tree.heading("t_masuk", text="T. Masuk")
        self.tree.heading("t_selesai", text="T. Selesai")
        self.tree.heading("status", text="Status")

        self.tree.column("oid", width=85, anchor="center")
        self.tree.column("pelanggan", width=180, anchor="w")
        self.tree.column("resto", width=120, anchor="w")
        self.tree.column("menu", width=120, anchor="w")
        self.tree.column("harga", width=95, anchor="e")
        self.tree.column("prioritas", width=70, anchor="center")
        self.tree.column("t_masuk", width=75, anchor="center")
        self.tree.column("t_selesai", width=75, anchor="center")
        self.tree.column("status", width=80, anchor="center")

        tree_scroll_y = ttk.Scrollbar(table_container, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=tree_scroll_y.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

        # 4. Detail Box (Jika ada pesanan terpilih)
        self.lbl_detail_selection = tk.Label(right_container, text="", font=("Arial", 9, "italic"), fg="#333333", bg="#ffffff", anchor="w")
        self.lbl_detail_selection.pack(fill=tk.X, padx=12, pady=(2, 2))

        # ------------------ PANEL BAWAH: COMMAND LOG ------------------
        bottom_frame = tk.Frame(self.root, height=130, bg="#1e1e1e", padx=10, pady=6)
        bottom_frame.pack(side=tk.BOTTOM, fill=tk.X)

        header_log = tk.Frame(bottom_frame, bg="#1e1e1e")
        header_log.pack(fill=tk.X)
        tk.Label(header_log, text="COMMAND", font=("Consolas", 10, "bold"), fg="#ffffff", bg="#1e1e1e").pack(side=tk.LEFT)
        btn_clear_log = tk.Button(header_log, text="Clear Log", font=("Consolas", 8), bg="#333333", fg="#ffffff",
                                  relief=tk.FLAT, command=self.clear_log)
        btn_clear_log.pack(side=tk.RIGHT)

        self.log_text = tk.Text(bottom_frame, height=5, bg="#121212", fg="#00ff66",
                                font=("Consolas", 9), insertbackground="white", relief=tk.SUNKEN)
        self.log_text.pack(fill=tk.BOTH, expand=True, pady=(4, 0))

    def build_form_inputs(self):
        for widget in self.form_frame.winfo_children():
            widget.destroy()

        if "LIHAT PESANAN" in self.active_mode:
            lbl = tk.Label(self.form_frame, text="Nomor Indeks Pesanan (i):", font=("Arial", 9, "bold"), bg="#ffffff")
            lbl.grid(row=0, column=0, sticky="w", padx=5, pady=4)
            self.entry_index = tk.Entry(self.form_frame, width=15)
            self.entry_index.insert(0, "0")
            self.entry_index.grid(row=0, column=1, sticky="w", padx=5, pady=4)

            btn_execute = tk.Button(self.form_frame, text="LIHAT PESANAN", bg="#007acc", fg="#ffffff",
                                    font=("Arial", 9, "bold"), command=self.execute_lihat_pesanan, cursor="hand2")
            btn_execute.grid(row=0, column=2, padx=15, pady=4)

            lbl_hint = tk.Label(self.form_frame, text=f"(Rentang valid: 0 s/d {max(0, self.array_data.size - 1)})",
                                font=("Arial", 8), fg="#777777", bg="#ffffff")
            lbl_hint.grid(row=0, column=3, sticky="w", padx=5, pady=4)

        elif "HAPUS PESANAN" in self.active_mode:
            lbl = tk.Label(self.form_frame, text="Indeks Pesanan yang Dihapus (i):", font=("Arial", 9, "bold"), bg="#ffffff")
            lbl.grid(row=0, column=0, sticky="w", padx=5, pady=4)
            self.entry_hapus_idx = tk.Entry(self.form_frame, width=15)
            self.entry_hapus_idx.insert(0, "0")
            self.entry_hapus_idx.grid(row=0, column=1, sticky="w", padx=5, pady=4)

            btn_execute = tk.Button(self.form_frame, text="HAPUS PESANAN", bg="#d9534f", fg="#ffffff",
                                    font=("Arial", 9, "bold"), command=self.execute_hapus_pesanan, cursor="hand2")
            btn_execute.grid(row=0, column=2, padx=15, pady=4)

            lbl_hint = tk.Label(self.form_frame, text=f"(Rentang valid: 0 s/d {max(0, self.array_data.size - 1)})",
                                font=("Arial", 8), fg="#777777", bg="#ffffff")
            lbl_hint.grid(row=0, column=3, sticky="w", padx=5, pady=4)

        else: # TAMBAH PESANAN (REGULER / PRIORITAS / VIP)
            tk.Label(self.form_frame, text="Nama Pelanggan:", font=("Arial", 9), bg="#ffffff").grid(row=0, column=0, sticky="w", padx=5, pady=3)
            self.entry_pelanggan = tk.Entry(self.form_frame, width=22)
            self.entry_pelanggan.insert(0, "Budi Santoso")
            self.entry_pelanggan.grid(row=0, column=1, padx=5, pady=3)

            tk.Label(self.form_frame, text="Resto:", font=("Arial", 9), bg="#ffffff").grid(row=0, column=2, sticky="w", padx=5, pady=3)
            self.entry_resto = tk.Entry(self.form_frame, width=18)
            self.entry_resto.insert(0, "kafe-teknik")
            self.entry_resto.grid(row=0, column=3, padx=5, pady=3)

            tk.Label(self.form_frame, text="Menu:", font=("Arial", 9), bg="#ffffff").grid(row=1, column=0, sticky="w", padx=5, pady=3)
            self.entry_menu = tk.Entry(self.form_frame, width=22)
            self.entry_menu.insert(0, "nasi-goreng")
            self.entry_menu.grid(row=1, column=1, padx=5, pady=3)

            tk.Label(self.form_frame, text="Harga (Rp):", font=("Arial", 9), bg="#ffffff").grid(row=1, column=2, sticky="w", padx=5, pady=3)
            self.entry_harga = tk.Entry(self.form_frame, width=18)
            self.entry_harga.insert(0, "20000")
            self.entry_harga.grid(row=1, column=3, padx=5, pady=3)

            btn_execute = tk.Button(self.form_frame, text="TAMBAH", bg="#28a745", fg="#ffffff",
                                    font=("Arial", 9, "bold"), width=12, command=self.execute_tambah_pesanan, cursor="hand2")
            btn_execute.grid(row=0, column=4, rowspan=2, padx=20, pady=3)

    def select_menu(self, menu_name):
        self.active_mode = menu_name

        # Update styling tombol sidebar
        for name, btn in self.sidebar_buttons.items():
            if name == menu_name:
                btn.config(bg="#dbeafe", relief=tk.SUNKEN)
            else:
                btn.config(bg="#ffffff", relief=tk.RAISED)

        # Update title & subtitle
        descriptions = {
            "ARRAY - LIHAT PESANAN": ("Array: LIHAT PESANAN ke-i", "Membuka detail satu pesanan berdasarkan indeks secara O(1)"),
            "ARRAY - TAMBAH PESANAN REGULER": ("Array: pesanan REGULER, masuk paling belakang", "Menambahkan pesanan biasa di ujung belakang menggunakan append O(1) amortized"),
            "ARRAY - TAMBAH PESANAN PRIORITAS": ("Array: pesanan PRIORITAS, menyerobot ke tengah", "Menyerobot ke tengah antrean (n/2), menggeser n/2 elemen: O(n)"),
            "ARRAY - TAMBAH PESANAN VIP": ("Array: pesanan VIP, langsung paling depan", "Menyerobot langsung ke urutan 0, menggeser seluruh isi array: O(n)"),
            "ARRAY - HAPUS PESANAN": ("Array: HAPUS PESANAN ke-i", "Mencabut pesanan ke-i dan menggeser elemen di belakangnya: O(n)"),
            "LINKEDLIST - LIHAT PESANAN": ("Linked List: LIHAT PESANAN ke-i", "Membuka detail pesanan dengan menelusuri rantai pointer dari head: O(n)"),
            "LINKEDLIST - TAMBAH PESANAN REGULER": ("Linked List: pesanan REGULER, masuk paling belakang", "Menambahkan simpul baru pada tail secara instan: O(1)"),
            "LINKEDLIST - TAMBAH PESANAN PRIORITAS": ("Linked List: pesanan PRIORITAS, menyerobot ke tengah", "Menelusuri n/2 simpul lalu menyambung pointer: O(n) telusur"),
            "LINKEDLIST - TAMBAH PESANAN VIP": ("Linked List: pesanan VIP, langsung paling depan", "Menyisipkan simpul di depan head secara instan: O(1)"),
            "LINKEDLIST - HAPUS PESANAN": ("Linked List: HAPUS PESANAN ke-i", "Menelusuri simpul ke-i lalu menghubungkan simpul sebelumnya ke berikutnya: O(n)")
        }

        title, sub = descriptions.get(menu_name, (menu_name, ""))
        self.lbl_title.config(text=title)
        self.lbl_subtitle.config(text=sub)

        self.build_form_inputs()

    def log_command(self, text):
        self.log_text.insert(tk.END, text + "\n")
        self.log_text.see(tk.END)

    def clear_log(self):
        self.log_text.delete("1.0", tk.END)

    def on_click_load(self):
        self.load_csv_data(silent_on_success=False)

    def load_csv_data(self, silent_on_success=False):
        if not os.path.exists(self.csv_path):
            messagebox.showerror("Error", f"File CSV tidak ditemukan pada:\n{self.csv_path}")
            self.lbl_status_data.config(text="File CSV tidak ditemukan!", fg="red")
            return

        t0 = time.perf_counter()
        try:
            self.array_data, self.linked_list_data = muat_data_csv(self.csv_path)
            duration_ms = (time.perf_counter() - t0) * 1000
            
            self.current_page = 0
            self.render_table()
            
            log_msg = f"[DATA LOAD] Selesai membaca '{os.path.basename(self.csv_path)}' ({self.array_data.size:,} data) dalam {duration_ms:.2f} ms"
            self.log_command(log_msg)
            
            if not silent_on_success:
                messagebox.showinfo("Sukses", f"Berhasil memuat {self.array_data.size:,} data pesanan!")
        except Exception as e:
            messagebox.showerror("Error", f"Gagal membaca data CSV: {e}")
            self.lbl_status_data.config(text="Gagal memuat CSV!", fg="red")

    def render_table(self):
        # Bersihkan tabel lama
        for item in self.tree.get_children():
            self.tree.delete(item)

        total = self.array_data.size
        if total == 0:
            self.lbl_status_data.config(text="Data Kosong (0 Pesanan)", fg="red")
            self.lbl_page_info.config(text="Hal 0 / 0")
            return

        total_pages = (total + self.page_size - 1) // self.page_size
        if self.current_page >= total_pages:
            self.current_page = total_pages - 1
        if self.current_page < 0:
            self.current_page = 0

        start_idx = self.current_page * self.page_size
        end_idx = min(start_idx + self.page_size, total)

        for i in range(start_idx, end_idx):
            pesanan = self.array_data.get(i)
            self.tree.insert("", tk.END, iid=str(i), values=pesanan.to_list())

        self.lbl_status_data.config(
            text=f"Total: {total:,} pesanan | Menampilkan indeks {start_idx:,} - {end_idx - 1:,}",
            fg="#111827"
        )
        self.lbl_page_info.config(text=f"Hal {self.current_page + 1:,} / {total_pages:,}")

    def page_first(self):
        self.current_page = 0
        self.render_table()

    def page_prev(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.render_table()

    def page_next(self):
        total_pages = (self.array_data.size + self.page_size - 1) // self.page_size
        if self.current_page < total_pages - 1:
            self.current_page += 1
            self.render_table()

    def page_last(self):
        total_pages = (self.array_data.size + self.page_size - 1) // self.page_size
        if total_pages > 0:
            self.current_page = total_pages - 1
            self.render_table()

    def jump_to_index(self, idx):
        self.current_page = idx // self.page_size
        self.render_table()
        if self.tree.exists(str(idx)):
            self.tree.selection_set(str(idx))
            self.tree.see(str(idx))

    # ------------------ EKSEKUSI OPERASI M1 ------------------
    def execute_lihat_pesanan(self):
        val_str = self.entry_index.get().strip()
        if not val_str.isdigit():
            messagebox.showwarning("Peringatan", "Masukkan indeks angka yang valid!")
            return
        
        idx = int(val_str)
        if idx < 0 or idx >= self.array_data.size:
            messagebox.showwarning("Peringatan", f"Indeks di luar rentang (0 s/d {self.array_data.size - 1})!")
            return

        is_array = "ARRAY" in self.active_mode

        # Ukur Array
        t0 = time.perf_counter()
        p_arr = self.array_data.get(idx)
        t_arr_ms = (time.perf_counter() - t0) * 1000

        # Ukur LinkedList
        t0 = time.perf_counter()
        p_ll = self.linked_list_data.get(idx)
        t_ll_ms = (time.perf_counter() - t0) * 1000

        self.jump_to_index(idx)
        self.lbl_detail_selection.config(
            text=f"Hasil Lihat [{idx}]: OID={p_arr.oid}, Pelanggan={p_arr.pelanggan}, Menu={p_arr.menu}, Harga=Rp{p_arr.harga:,}, Status={p_arr.status}"
        )

        log_lead = "m1 - array: lihat_pesanan" if is_array else "m1 - linkedlist: lihat_pesanan"
        self.log_command(f"> {log_lead} (indeks={idx:,})")
        self.log_command(f"  Array.get({idx:,})      : {t_arr_ms:.4f} ms (O(1))")
        self.log_command(f"  LinkList.get({idx:,})   : {t_ll_ms:.4f} ms (O(n) telusur)")

    def execute_tambah_pesanan(self):
        pelanggan = self.entry_pelanggan.get().strip()
        resto = self.entry_resto.get().strip()
        menu = self.entry_menu.get().strip()
        harga_str = self.entry_harga.get().strip()

        if not pelanggan or not menu:
            messagebox.showwarning("Peringatan", "Nama pelanggan dan menu tidak boleh kosong!")
            return

        harga = int(harga_str) if harga_str.isdigit() else 0
        new_oid = f"O-{self.array_data.size + 1:06d}"

        is_vip = "VIP" in self.active_mode
        is_prioritas = "PRIORITAS" in self.active_mode
        is_array = "ARRAY" in self.active_mode

        p_arr = Pesanan(new_oid, pelanggan, resto, menu, harga, 1 if is_vip else (2 if is_prioritas else 3), status="ANTRE")
        p_ll = Pesanan(new_oid, pelanggan, resto, menu, harga, 1 if is_vip else (2 if is_prioritas else 3), status="ANTRE")

        if is_vip:
            t0 = time.perf_counter()
            self.array_data.tambah_vip(p_arr)
            t_arr_ms = (time.perf_counter() - t0) * 1000

            t0 = time.perf_counter()
            self.linked_list_data.tambah_vip(p_ll)
            t_ll_ms = (time.perf_counter() - t0) * 1000

            op_name = "tambah_vip"
            target_idx = 0

        elif is_prioritas:
            t0 = time.perf_counter()
            self.array_data.tambah_prioritas(p_arr)
            t_arr_ms = (time.perf_counter() - t0) * 1000

            t0 = time.perf_counter()
            self.linked_list_data.tambah_prioritas(p_ll)
            t_ll_ms = (time.perf_counter() - t0) * 1000

            op_name = "tambah_prioritas"
            target_idx = (self.array_data.size - 1) // 2

        else: # REGULER
            t0 = time.perf_counter()
            self.array_data.tambah_reguler(p_arr)
            t_arr_ms = (time.perf_counter() - t0) * 1000

            t0 = time.perf_counter()
            self.linked_list_data.tambah_reguler(p_ll)
            t_ll_ms = (time.perf_counter() - t0) * 1000

            op_name = "tambah_reguler"
            target_idx = self.array_data.size - 1

        self.jump_to_index(target_idx)
        self.lbl_detail_selection.config(
            text=f"Berhasil ditambahkan di indeks [{target_idx:,}]: {p_arr.oid} - {p_arr.pelanggan} ({p_arr.menu})"
        )

        mod = "array" if is_array else "linkedlist"
        self.log_command(f"> m1 - {mod}: {op_name} ({p_arr.oid} - {p_arr.pelanggan})")
        self.log_command(f"  Array.{op_name}     : {t_arr_ms:.4f} ms")
        self.log_command(f"  LinkList.{op_name}  : {t_ll_ms:.4f} ms")

    def execute_hapus_pesanan(self):
        val_str = self.entry_hapus_idx.get().strip()
        if not val_str.isdigit():
            messagebox.showwarning("Peringatan", "Masukkan indeks angka yang valid!")
            return

        idx = int(val_str)
        if idx < 0 or idx >= self.array_data.size:
            messagebox.showwarning("Peringatan", f"Indeks di luar rentang (0 s/d {self.array_data.size - 1})!")
            return

        is_array = "ARRAY" in self.active_mode

        t0 = time.perf_counter()
        del_arr = self.array_data.delete(idx)
        t_arr_ms = (time.perf_counter() - t0) * 1000

        t0 = time.perf_counter()
        del_ll = self.linked_list_data.delete(idx)
        t_ll_ms = (time.perf_counter() - t0) * 1000

        self.jump_to_index(max(0, min(idx, self.array_data.size - 1)))
        self.lbl_detail_selection.config(
            text=f"Pesanan di indeks [{idx:,}] berhasil dihapus: {del_arr.oid} - {del_arr.pelanggan}"
        )

        mod = "array" if is_array else "linkedlist"
        self.log_command(f"> m1 - {mod}: hapus_pesanan (indeks={idx:,})")
        self.log_command(f"  Array.delete({idx:,})    : {t_arr_ms:.4f} ms")
        self.log_command(f"  LinkList.delete({idx:,}) : {t_ll_ms:.4f} ms")

    def run(self):
        self.root.mainloop()
