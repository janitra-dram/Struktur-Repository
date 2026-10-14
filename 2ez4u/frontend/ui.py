import os
import time
import tkinter as tk
from tkinter import ttk, messagebox
import csv
from backend.m1_pesanan import Array, LinkList, Pesanan
from backend.m2_antrean import (
    Stack,
    infix_to_postfix,
    evaluate_postfix,
    NaiveQueue,
    CircularQueue
)
from backend.m3_laporan import (
    insertion_sort,
    merge_sort,
    linear_search,
    binary_search
)

class ListWrapper:
    def __init__(self, data):
        self.data = data

    @property
    def size(self):
        return len(self.data)

    def get(self, i):
        if 0 <= i < len(self.data):
            return self.data[i]
        return None


class AppUI:
    def __init__(self, root):
        self.root = root
        self.root.title("2EZ4U Food Delivery")
        self.root.geometry("1100x720")
        self.root.minsize(950, 600)

        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.csv_path = os.path.join(base_dir, "data", "pesanan.csv")

        self.array_data = Array()
        self.linked_list_data = LinkList()
        self.master_list = []

        self.q_naif = NaiveQueue()
        self.q_circ = CircularQueue(32768)
        self.tumpukan_undo = Stack()
        self.tumpukan_redo = Stack()

        self.sorted_list = None
        self.oid_sorted_list = None

        self.active_mode = "ARRAY - TAMBAH PESANAN REGULER"
        self.page_size = 50
        self.current_page = 0
        self.current_view_mode = "M1"

        self.setup_styles()
        self.create_layout()
        self.load_csv_data(silent_on_success=True)

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview.Heading", font=("Arial", 9, "bold"))
        style.configure("Treeview", font=("Arial", 9), rowheight=22)

    def create_layout(self):
        main_container = tk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True)

        sidebar_frame = tk.Frame(main_container, width=250, bg="#f0f0f0", relief=tk.GROOVE, borderwidth=1)
        sidebar_frame.pack(side=tk.LEFT, fill=tk.Y)
        sidebar_frame.pack_propagate(False)

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

        tk.Label(scrollable_frame, text="DATA", font=("Arial", 10, "bold"), bg="#f0f0f0", anchor="w").pack(fill=tk.X, padx=10, pady=(8, 2))
        btn_load = tk.Button(scrollable_frame, text="Load Data CSV", bg="#e1e1e1", activebackground="#d0d0d0",
                             font=("Arial", 9), command=self.on_click_load, cursor="hand2")
        btn_load.pack(fill=tk.X, padx=10, pady=2)

        ttk.Separator(scrollable_frame, orient="horizontal").pack(fill=tk.X, padx=10, pady=8)

        # M1
        tk.Label(scrollable_frame, text="M1 - DATA PESANAN", font=("Arial", 9, "bold"), bg="#f0f0f0", anchor="w").pack(fill=tk.X, padx=10, pady=(2, 4))
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

        # M2
        tk.Label(scrollable_frame, text="M2 - ANTREAN DAN UNDO", font=("Arial", 9, "bold"), bg="#f0f0f0", anchor="w").pack(fill=tk.X, padx=10, pady=(2, 4))
        m2_menus = [
            ("STACK - POSTFIX (MESIN KASIR)", lambda: self.select_menu("STACK - POSTFIX (MESIN KASIR)")),
            ("QUEUE - ENQUEUE", lambda: self.select_menu("QUEUE - ENQUEUE")),
            ("QUEUE - DEQUEUE NAIF", lambda: self.select_menu("QUEUE - DEQUEUE NAIF")),
            ("QUEUE - DEQUEUE CIRCULAR", lambda: self.select_menu("QUEUE - DEQUEUE CIRCULAR")),
            ("STACK - UNDO", lambda: self.select_menu("STACK - UNDO")),
            ("STACK - REDO", lambda: self.select_menu("STACK - REDO")),
        ]

        for text, cmd in m2_menus:
            btn = tk.Button(scrollable_frame, text=text, font=("Arial", 8), bg="#ffffff",
                            relief=tk.RAISED, anchor="w", padx=6, pady=2, command=cmd, cursor="hand2")
            btn.pack(fill=tk.X, padx=10, pady=2)
            self.sidebar_buttons[text] = btn

        ttk.Separator(scrollable_frame, orient="horizontal").pack(fill=tk.X, padx=10, pady=8)

        # M3
        tk.Label(scrollable_frame, text="M3 - SORT & SEARCH", font=("Arial", 9, "bold"), bg="#f0f0f0", anchor="w").pack(fill=tk.X, padx=10, pady=(2, 4))
        m3_menus = [
            ("SORT - INSERTION SORT", lambda: self.select_menu("SORT - INSERTION SORT")),
            ("SORT - MERGE SORT", lambda: self.select_menu("SORT - MERGE SORT")),
            ("SEARCH - LINEAR SEARCH", lambda: self.select_menu("SEARCH - LINEAR SEARCH")),
            ("SEARCH - BINARY SEARCH", lambda: self.select_menu("SEARCH - BINARY SEARCH")),
        ]

        for text, cmd in m3_menus:
            btn = tk.Button(scrollable_frame, text=text, font=("Arial", 8), bg="#ffffff",
                            relief=tk.RAISED, anchor="w", padx=6, pady=2, command=cmd, cursor="hand2")
            btn.pack(fill=tk.X, padx=10, pady=2)
            self.sidebar_buttons[text] = btn



        right_container = tk.Frame(main_container, bg="#ffffff")
        right_container.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.header_frame = tk.Frame(right_container, bg="#f9f9f9", padx=15, pady=10, relief=tk.RIDGE, borderwidth=1)
        self.header_frame.pack(fill=tk.X, padx=10, pady=(10, 5))

        self.lbl_title = tk.Label(self.header_frame, text="Array: pesanan REGULER, masuk paling belakang",
                                  font=("Arial", 12, "bold"), bg="#f9f9f9", anchor="w")
        self.lbl_title.pack(fill=tk.X)

        self.lbl_subtitle = tk.Label(self.header_frame, text="Menambahkan data pesanan reguler di antrean paling belakang",
                                     font=("Arial", 9), fg="#555555", bg="#f9f9f9", anchor="w")
        self.lbl_subtitle.pack(fill=tk.X, pady=(2, 0))

        self.form_frame = tk.Frame(right_container, bg="#ffffff", padx=15, pady=8)
        self.form_frame.pack(fill=tk.X, padx=10, pady=5)
        self.build_form_inputs()

        self.table_container = tk.Frame(right_container, bg="#ffffff")
        self.table_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.nav_frame = tk.Frame(self.table_container, bg="#ffffff")
        self.nav_frame.pack(fill=tk.X, pady=(0, 4))

        self.lbl_status_data = tk.Label(self.nav_frame, text="Memuat data...", font=("Arial", 9, "bold"), bg="#ffffff")
        self.lbl_status_data.pack(side=tk.LEFT)

        self.btn_first = tk.Button(self.nav_frame, text="<<", width=3, command=self.page_first)
        self.btn_first.pack(side=tk.RIGHT, padx=1)
        self.btn_next = tk.Button(self.nav_frame, text=">", width=3, command=self.page_next)
        self.btn_next.pack(side=tk.RIGHT, padx=1)
        self.lbl_page_info = tk.Label(self.nav_frame, text="Hal 1 / 1", font=("Arial", 9), bg="#ffffff")
        self.lbl_page_info.pack(side=tk.RIGHT, padx=6)
        self.btn_prev = tk.Button(self.nav_frame, text="<", width=3, command=self.page_prev)
        self.btn_prev.pack(side=tk.RIGHT, padx=1)
        self.btn_last = tk.Button(self.nav_frame, text=">>", width=3, command=self.page_last)
        self.btn_last.pack(side=tk.RIGHT, padx=1)

        columns = ("oid", "pelanggan", "resto", "menu", "harga", "prioritas", "t_masuk", "t_selesai", "status")
        self.tree = ttk.Treeview(self.table_container, columns=columns, show="headings", height=10)

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

        self.tree_scroll_y = ttk.Scrollbar(self.table_container, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.tree_scroll_y.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.tree_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

        self.lbl_detail_selection = tk.Label(right_container, text="", font=("Arial", 9, "italic"), fg="#333333", bg="#ffffff", anchor="w")
        self.lbl_detail_selection.pack(fill=tk.X, padx=12, pady=(2, 2))

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

        mode = self.active_mode

        if mode == "STACK - POSTFIX (MESIN KASIR)":
            tk.Label(self.form_frame, text="Struk Kasir (Infix):", font=("Arial", 9, "bold"), bg="#ffffff").grid(row=0, column=0, sticky="w", padx=5, pady=4)
            self.entry_expr = tk.Entry(self.form_frame, width=40)
            self.entry_expr.insert(0, "( 3 * 12000 ) + ( 2 * 8500 ) - 5000")
            self.entry_expr.grid(row=0, column=1, sticky="w", padx=5, pady=4)

            btn_execute = tk.Button(self.form_frame, text="HITUNG TOTAL", bg="#007acc", fg="#ffffff",
                                    font=("Arial", 9, "bold"), command=self.execute_postfix, cursor="hand2")
            btn_execute.grid(row=0, column=2, padx=15, pady=4)

        elif mode in ("QUEUE - DEQUEUE NAIF", "QUEUE - DEQUEUE CIRCULAR"):
            tk.Label(self.form_frame, text="Jumlah pesanan yang dilayani (k):", font=("Arial", 9, "bold"), bg="#ffffff").grid(row=0, column=0, sticky="w", padx=5, pady=4)
            self.entry_k = tk.Entry(self.form_frame, width=12)
            self.entry_k.insert(0, "1")
            self.entry_k.grid(row=0, column=1, sticky="w", padx=5, pady=4)

            btn_text = "LAYANI (NAIF)" if mode == "QUEUE - DEQUEUE NAIF" else "LAYANI (CIRCULAR)"
            btn_color = "#d9534f" if mode == "QUEUE - DEQUEUE NAIF" else "#28a745"

            btn_execute = tk.Button(self.form_frame, text=btn_text, bg=btn_color, fg="#ffffff",
                                    font=("Arial", 9, "bold"),
                                    command=self.execute_dequeue_naif if mode == "QUEUE - DEQUEUE NAIF" else self.execute_dequeue_circular,
                                    cursor="hand2")
            btn_execute.grid(row=0, column=2, padx=15, pady=4)

            btn_quick100 = tk.Button(self.form_frame, text="Layani 100", bg="#f0f0f0",
                                     font=("Arial", 8), command=lambda: self.quick_dequeue(100))
            btn_quick100.grid(row=0, column=3, padx=5, pady=4)

        elif mode == "STACK - UNDO":
            lbl = tk.Label(self.form_frame, text=f"Tumpukan Undo: {self.tumpukan_undo.size} aksi | Tumpukan Redo: {self.tumpukan_redo.size} aksi",
                           font=("Arial", 9, "bold"), bg="#ffffff")
            lbl.grid(row=0, column=0, sticky="w", padx=5, pady=4)

            btn_execute = tk.Button(self.form_frame, text="UNDO LAST()", bg="#ff9900", fg="#ffffff",
                                    font=("Arial", 9, "bold"), command=self.execute_undo, cursor="hand2")
            btn_execute.grid(row=0, column=1, padx=15, pady=4)

        elif mode == "STACK - REDO":
            lbl = tk.Label(self.form_frame, text=f"Tumpukan Redo: {self.tumpukan_redo.size} aksi | Tumpukan Undo: {self.tumpukan_undo.size} aksi",
                           font=("Arial", 9, "bold"), bg="#ffffff")
            lbl.grid(row=0, column=0, sticky="w", padx=5, pady=4)

            btn_execute = tk.Button(self.form_frame, text="REDO LAST()", bg="#17a2b8", fg="#ffffff",
                                    font=("Arial", 9, "bold"), command=self.execute_redo, cursor="hand2")
            btn_execute.grid(row=0, column=1, padx=15, pady=4)

        elif mode in ("SORT - INSERTION SORT", "SORT - MERGE SORT"):
            tk.Label(self.form_frame, text="Kunci Pengurutan:", font=("Arial", 9, "bold"), bg="#ffffff").grid(row=0, column=0, sticky="w", padx=5, pady=3)
            self.combo_sort_key = ttk.Combobox(self.form_frame, values=["harga", "oid", "t_selesai_detik", "t_masuk_detik"], width=15, state="readonly")
            self.combo_sort_key.set("harga")
            self.combo_sort_key.grid(row=0, column=1, padx=5, pady=3)

            tk.Label(self.form_frame, text="Jumlah Baris (n):", font=("Arial", 9, "bold"), bg="#ffffff").grid(row=0, column=2, sticky="w", padx=10, pady=3)
            self.entry_sort_n = tk.Entry(self.form_frame, width=12)
            self.entry_sort_n.insert(0, "2000")
            self.entry_sort_n.grid(row=0, column=3, padx=5, pady=3)

            is_ins = mode == "SORT - INSERTION SORT"
            btn_txt = "URUTKAN (INSERTION)" if is_ins else "URUTKAN (MERGE)"
            btn_col = "#d9534f" if is_ins else "#007acc"
            btn_cmd = self.execute_insertion_sort if is_ins else self.execute_merge_sort

            btn_execute = tk.Button(self.form_frame, text=btn_txt, bg=btn_col, fg="#ffffff",
                                    font=("Arial", 9, "bold"), command=btn_cmd, cursor="hand2")
            btn_execute.grid(row=0, column=4, padx=15, pady=3)

            # Shortcut tombol n
            shortcuts_frame = tk.Frame(self.form_frame, bg="#ffffff")
            shortcuts_frame.grid(row=1, column=0, columnspan=5, sticky="w", padx=5, pady=(4, 0))
            tk.Label(shortcuts_frame, text="Preset n:", font=("Arial", 8), bg="#ffffff").pack(side=tk.LEFT, padx=(0, 5))
            for val_n in ("10", "2000", "4000", "200000"):
                b = tk.Button(shortcuts_frame, text=f"n={val_n}", font=("Arial", 8), bg="#f0f0f0",
                              command=lambda v=val_n: self.set_sort_n(v))
                b.pack(side=tk.LEFT, padx=2)

        elif mode in ("SEARCH - LINEAR SEARCH", "SEARCH - BINARY SEARCH"):
            tk.Label(self.form_frame, text="Target OID:", font=("Arial", 9, "bold"), bg="#ffffff").grid(row=0, column=0, sticky="w", padx=5, pady=4)
            self.entry_search_target = tk.Entry(self.form_frame, width=20)
            self.entry_search_target.insert(0, "O-137442")
            self.entry_search_target.grid(row=0, column=1, padx=5, pady=4)

            is_lin = mode == "SEARCH - LINEAR SEARCH"
            btn_txt = "CARI (LINEAR)" if is_lin else "CARI (BINARY)"
            btn_col = "#ff9900" if is_lin else "#28a745"
            btn_cmd = self.execute_linear_search if is_lin else self.execute_binary_search

            btn_execute = tk.Button(self.form_frame, text=btn_txt, bg=btn_col, fg="#ffffff",
                                    font=("Arial", 9, "bold"), command=btn_cmd, cursor="hand2")
            btn_execute.grid(row=0, column=2, padx=15, pady=4)

            presets_frame = tk.Frame(self.form_frame, bg="#ffffff")
            presets_frame.grid(row=0, column=3, sticky="w", padx=5)
            for oid_sample in ("O-000002", "O-137442", "O-199999"):
                b = tk.Button(presets_frame, text=oid_sample, font=("Arial", 8), bg="#f0f0f0",
                              command=lambda o=oid_sample: self.set_search_target(o))
                b.pack(side=tk.LEFT, padx=2)

        elif "LIHAT PESANAN" in mode:
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

        elif "HAPUS PESANAN" in mode:
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

        else:
            tk.Label(self.form_frame, text="Nama Pelanggan:", font=("Arial", 9), bg="#ffffff").grid(row=0, column=0, sticky="w", padx=5, pady=3)
            self.entry_pelanggan = tk.Entry(self.form_frame, width=22)
            self.entry_pelanggan.insert(0, "Pelanggan Baru" if "QUEUE" in mode else "Budi Santoso")
            self.entry_pelanggan.grid(row=0, column=1, padx=5, pady=3)

            tk.Label(self.form_frame, text="Resto:", font=("Arial", 9), bg="#ffffff").grid(row=0, column=2, sticky="w", padx=5, pady=3)
            self.entry_resto = tk.Entry(self.form_frame, width=18)
            self.entry_resto.insert(0, "kafe-teknik")
            self.entry_resto.grid(row=0, column=3, padx=5, pady=3)

            tk.Label(self.form_frame, text="Menu:", font=("Arial", 9), bg="#ffffff").grid(row=1, column=0, sticky="w", padx=5, pady=3)
            self.entry_menu = tk.Entry(self.form_frame, width=22)
            self.entry_menu.insert(0, "paket-hemat")
            self.entry_menu.grid(row=1, column=1, padx=5, pady=3)

            tk.Label(self.form_frame, text="Harga (Rp):", font=("Arial", 9), bg="#ffffff").grid(row=1, column=2, sticky="w", padx=5, pady=3)
            self.entry_harga = tk.Entry(self.form_frame, width=18)
            self.entry_harga.insert(0, "25000")
            self.entry_harga.grid(row=1, column=3, padx=5, pady=3)

            btn_cmd = self.execute_queue_enqueue if "QUEUE" in mode else self.execute_tambah_pesanan
            btn_execute = tk.Button(self.form_frame, text="ENQUEUE" if "QUEUE" in mode else "TAMBAH",
                                    bg="#28a745", fg="#ffffff", font=("Arial", 9, "bold"),
                                    width=12, command=btn_cmd, cursor="hand2")
            btn_execute.grid(row=0, column=4, rowspan=2, padx=20, pady=3)

    def set_sort_n(self, n_str):
        self.entry_sort_n.delete(0, tk.END)
        self.entry_sort_n.insert(0, n_str)

    def set_search_target(self, target_str):
        self.entry_search_target.delete(0, tk.END)
        self.entry_search_target.insert(0, target_str)

    def select_menu(self, menu_name):
        self.active_mode = menu_name

        for name, btn in self.sidebar_buttons.items():
            if name == menu_name:
                btn.config(bg="#dbeafe", relief=tk.SUNKEN)
            else:
                btn.config(bg="#ffffff", relief=tk.RAISED)

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
            "LINKEDLIST - HAPUS PESANAN": ("Linked List: HAPUS PESANAN ke-i", "Menelusuri simpul ke-i lalu menghubungkan simpul sebelumnya ke berikutnya: O(n)"),
            "STACK - POSTFIX (MESIN KASIR)": ("Stack: Mesin Kasir Infix ke Postfix", "Evaluasi ekspresi hitung kasir langkah demi langkah memakai stack"),
            "QUEUE - ENQUEUE": ("Queue: Tambah Pesanan ke Belakang Antrean", "Menambahkan pesanan baru ke belakang antrean Naif & Melingkar: O(1)"),
            "QUEUE - DEQUEUE NAIF": ("Queue Naif: Layani Pesanan", "Mengambil pesanan depan dengan menggeser seluruh sisa elemen: O(n)"),
            "QUEUE - DEQUEUE CIRCULAR": ("Queue Melingkar: Layani Pesanan", "Mengambil pesanan depan dengan memajukan pointer front: O(1) tanpa penggeseran"),
            "STACK - UNDO": ("Stack Undo: Batalkan Aksi Antrean", "Membatalkan aksi enqueue/dequeue terakhir dan mengembalikan status antrean"),
            "STACK - REDO": ("Stack Redo: Ulangi Aksi yang Dibatalkan", "Mengerjakan ulang aksi yang baru saja dibatalkan"),
            "SORT - INSERTION SORT": ("Sort: Insertion Sort (Stabil, In-Place)", "Pengurutan O(n^2) dengan membandingkan dan menggeser elemen ke kiri. Batas 20.000 baris."),
            "SORT - MERGE SORT": ("Sort: Merge Sort (Stabil, Divide & Conquer)", "Pengurutan O(n log n) yang mampu menangani seluruh 200.000 data sekaligus."),
            "SEARCH - LINEAR SEARCH": ("Search: Linear Search", "Pencarian O(n) satu per satu tanpa menuntut data terurut."),
            "SEARCH - BINARY SEARCH": ("Search: Binary Search", "Pencarian O(log n) pada data yang sudah terurut menurut OID.")
        }

        title, sub = descriptions.get(menu_name, (menu_name, ""))
        self.lbl_title.config(text=title)
        self.lbl_subtitle.config(text=sub)

        if menu_name.startswith("QUEUE") or menu_name.startswith("STACK - UNDO") or menu_name.startswith("STACK - REDO"):
            self.current_view_mode = "QUEUE"
            self.setup_table_columns_orders()
            self.current_page = 0
            self.render_table()
        elif menu_name == "STACK - POSTFIX (MESIN KASIR)":
            self.current_view_mode = "POSTFIX"
            self.setup_table_columns_postfix()
        elif menu_name.startswith("SORT"):
            self.current_view_mode = "SORTED" if self.sorted_list else "M1"
            self.setup_table_columns_orders()
            self.current_page = 0
            self.render_table()
        elif menu_name.startswith("SEARCH"):
            self.current_view_mode = "SORTED" if (menu_name == "SEARCH - BINARY SEARCH" and self.oid_sorted_list) else "M1"
            self.setup_table_columns_orders()
            self.render_table()
        else:
            self.current_view_mode = "M1"
            self.setup_table_columns_orders()
            self.current_page = 0
            self.render_table()

        self.build_form_inputs()

    def setup_table_columns_orders(self):
        self.nav_frame.pack(fill=tk.X, pady=(0, 4))
        columns = ("oid", "pelanggan", "resto", "menu", "harga", "prioritas", "t_masuk", "t_selesai", "status")
        self.tree.config(columns=columns)
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

    def setup_table_columns_postfix(self):
        self.nav_frame.pack_forget()
        columns = ("tahap", "token", "tindakan", "stack", "keluaran")
        self.tree.config(columns=columns)
        self.tree.heading("tahap", text="Tahap")
        self.tree.heading("token", text="Token")
        self.tree.heading("tindakan", text="Tindakan")
        self.tree.heading("stack", text="Isi Stack")
        self.tree.heading("keluaran", text="Keluaran / Nilai")

        self.tree.column("tahap", width=90, anchor="center")
        self.tree.column("token", width=70, anchor="center")
        self.tree.column("tindakan", width=260, anchor="w")
        self.tree.column("stack", width=180, anchor="w")
        self.tree.column("keluaran", width=260, anchor="w")

    def log_command(self, text):
        self.log_text.insert(tk.END, text + "\n")
        self.log_text.see(tk.END)

    def clear_log(self):
        self.log_text.delete("1.0", tk.END)

    def on_click_load(self):
        self.load_csv_data(silent_on_success=False)

    def load_csv_data(self, silent_on_success=False):
        if not os.path.exists(self.csv_path):
            messagebox.showerror("Error", f"File CSV tidak ditemukan:\n{self.csv_path}")
            self.lbl_status_data.config(text="File CSV tidak ditemukan!", fg="red")
            return

        t0 = time.perf_counter()
        try:
            arr = Array()
            ll = LinkList()
            qn = NaiveQueue()
            qc = CircularQueue(32768)
            ml = []

            with open(self.csv_path, mode="r", encoding="utf-8") as f:
                reader = csv.reader(f)
                try:
                    next(reader)
                except StopIteration:
                    pass
                for row in reader:
                    if not row or len(row) < 9:
                        continue
                    p = Pesanan(
                        row[0],
                        row[1],
                        row[2],
                        row[3],
                        row[4] if len(row) > 4 else 0,
                        row[5] if len(row) > 5 else 3,
                        row[6] if len(row) > 6 else 0,
                        row[7] if len(row) > 7 else 0,
                        row[8]
                    )
                    arr.append(p)
                    ll.append(p)
                    ml.append(p)
                    if p.status == "ANTRE":
                        qn.enqueue(p)
                        qc.enqueue(p)

            self.array_data = arr
            self.linked_list_data = ll
            self.master_list = ml
            self.q_naif = qn
            self.q_circ = qc
            self.tumpukan_undo.clear()
            self.tumpukan_redo.clear()
            self.sorted_list = None
            self.oid_sorted_list = None

            duration_ms = (time.perf_counter() - t0) * 1000

            self.current_page = 0
            self.render_table()

            self.log_command(f"[DATA LOAD] '{os.path.basename(self.csv_path)}' ({self.array_data.size:,} data) dimuat dalam {duration_ms:.2f} ms")
            self.log_command(f"  Antrean ANTRE diisi: {self.q_circ.size:,} pesanan (kapasitas circular: {self.q_circ.capacity:,})")

            if not silent_on_success:
                messagebox.showinfo("Sukses", f"Berhasil memuat {self.array_data.size:,} data pesanan!\n{self.q_circ.size:,} pesanan masuk antrean.")
        except Exception as e:
            messagebox.showerror("Error", f"Gagal membaca data CSV: {e}")
            self.lbl_status_data.config(text="Gagal memuat CSV!", fg="red")

    def get_active_data_source(self):
        if self.current_view_mode == "QUEUE":
            return self.q_circ
        if self.current_view_mode == "SORTED" and self.sorted_list:
            return self.sorted_list
        return self.array_data

    def render_table(self):
        if self.current_view_mode == "POSTFIX":
            return

        for item in self.tree.get_children():
            self.tree.delete(item)

        source = self.get_active_data_source()
        total = source.size

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
            pesanan = source.get(i)
            if pesanan is not None:
                self.tree.insert("", tk.END, iid=str(i), values=pesanan.to_list())

        if self.current_view_mode == "QUEUE":
            tag = "Antrean ANTRE"
        elif self.current_view_mode == "SORTED":
            tag = "Hasil Terurut"
        else:
            tag = "Data Master"

        self.lbl_status_data.config(
            text=f"[{tag}] Total: {total:,} | Menampilkan {start_idx:,} - {end_idx - 1:,}",
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
        source = self.get_active_data_source()
        total_pages = (source.size + self.page_size - 1) // self.page_size
        if self.current_page < total_pages - 1:
            self.current_page += 1
            self.render_table()

    def page_last(self):
        source = self.get_active_data_source()
        total_pages = (source.size + self.page_size - 1) // self.page_size
        if total_pages > 0:
            self.current_page = total_pages - 1
            self.render_table()

    def jump_to_index(self, idx):
        self.current_page = idx // self.page_size
        self.render_table()
        if self.tree.exists(str(idx)):
            self.tree.selection_set(str(idx))
            self.tree.see(str(idx))

    # Operasi M1
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

        t0 = time.perf_counter()
        p_arr = self.array_data.get(idx)
        t_arr_ms = (time.perf_counter() - t0) * 1000

        t0 = time.perf_counter()
        p_ll = self.linked_list_data.get(idx)
        t_ll_ms = (time.perf_counter() - t0) * 1000

        self.jump_to_index(idx)
        self.lbl_detail_selection.config(
            text=f"Hasil Lihat [{idx}]: OID={p_arr.oid}, Pelanggan={p_arr.pelanggan}, Menu={p_arr.menu}, Harga=Rp{p_arr.harga:,}, Status={p_arr.status}"
        )

        mod = "array" if is_array else "linkedlist"
        self.log_command(f"> m1 - {mod}: lihat_pesanan (indeks={idx:,})")
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

            self.master_list.insert(0, p_arr)
            op_name = "tambah_vip"
            target_idx = 0
        elif is_prioritas:
            t0 = time.perf_counter()
            self.array_data.tambah_prioritas(p_arr)
            t_arr_ms = (time.perf_counter() - t0) * 1000

            t0 = time.perf_counter()
            self.linked_list_data.tambah_prioritas(p_ll)
            t_ll_ms = (time.perf_counter() - t0) * 1000

            target_idx = (self.array_data.size - 1) // 2
            self.master_list.insert(target_idx, p_arr)
            op_name = "tambah_prioritas"
        else:
            t0 = time.perf_counter()
            self.array_data.tambah_reguler(p_arr)
            t_arr_ms = (time.perf_counter() - t0) * 1000

            t0 = time.perf_counter()
            self.linked_list_data.tambah_reguler(p_ll)
            t_ll_ms = (time.perf_counter() - t0) * 1000

            self.master_list.append(p_arr)
            op_name = "tambah_reguler"
            target_idx = self.array_data.size - 1

        self.oid_sorted_list = None
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

        if 0 <= idx < len(self.master_list):
            self.master_list.pop(idx)
        self.oid_sorted_list = None

        self.jump_to_index(max(0, min(idx, self.array_data.size - 1)))
        self.lbl_detail_selection.config(
            text=f"Pesanan di indeks [{idx:,}] berhasil dihapus: {del_arr.oid} - {del_arr.pelanggan}"
        )

        mod = "array" if is_array else "linkedlist"
        self.log_command(f"> m1 - {mod}: hapus_pesanan (indeks={idx:,})")
        self.log_command(f"  Array.delete({idx:,})    : {t_arr_ms:.4f} ms")
        self.log_command(f"  LinkList.delete({idx:,}) : {t_ll_ms:.4f} ms")

    # Operasi M2
    def execute_postfix(self):
        expr = self.entry_expr.get().strip()
        if not expr:
            messagebox.showwarning("Peringatan", "Ekspresi struk kasir tidak boleh kosong!")
            return

        t0 = time.perf_counter()
        tokens, postfix_str, steps1 = infix_to_postfix(expr)
        total, steps2 = evaluate_postfix(tokens)
        duration_ms = (time.perf_counter() - t0) * 1000

        for item in self.tree.get_children():
            self.tree.delete(item)

        row_id = 1
        for tok, act, st_val, out_val in steps1:
            self.tree.insert("", tk.END, values=(f"1.{row_id}", tok, act, st_val, out_val))
            row_id += 1

        row_id = 1
        for tok, act, st_val in steps2:
            self.tree.insert("", tk.END, values=(f"2.{row_id}", tok, act, st_val, ""))
            row_id += 1

        self.lbl_detail_selection.config(
            text=f"Hasil Postfix: {postfix_str}  ==>  TOTAL: Rp {total:,}"
        )

        self.log_command(f"> stack_postfix {expr}")
        self.log_command(f"  postfix: {postfix_str}")
        self.log_command(f"  TOTAL : Rp {total:,} [M2 - stack] {duration_ms:.2f} ms")

    def execute_queue_enqueue(self):
        pelanggan = self.entry_pelanggan.get().strip()
        resto = self.entry_resto.get().strip()
        menu = self.entry_menu.get().strip()
        harga_str = self.entry_harga.get().strip()

        if not pelanggan or not menu:
            messagebox.showwarning("Peringatan", "Nama pelanggan dan menu tidak boleh kosong!")
            return

        harga = int(harga_str) if harga_str.isdigit() else 25000
        new_oid = f"O-{self.array_data.size + self.tumpukan_undo.size + 1:06d}"

        p = Pesanan(new_oid, pelanggan, resto, menu, harga, 3, status="ANTRE")

        t0 = time.perf_counter()
        self.q_naif.enqueue(p)
        t_naif = (time.perf_counter() - t0) * 1000

        t0 = time.perf_counter()
        self.q_circ.enqueue(p)
        t_circ = (time.perf_counter() - t0) * 1000

        self.tumpukan_undo.push(("ENQUEUE", p))
        self.tumpukan_redo.clear()

        self.render_table()
        self.lbl_detail_selection.config(
            text=f"Enqueue berhasil: {p.oid} ({p.pelanggan}) masuk paling belakang. Panjang antrean: {self.q_circ.size:,}"
        )

        self.log_command(f"> queue_enqueue {pelanggan}")
        self.log_command(f"  {p.oid} masuk paling belakang [M2 - queue] {t_circ:.2f} ms (naif: {t_naif:.2f} ms)")
        self.log_command(f"  tumpukan undo {self.tumpukan_undo.size}, redo {self.tumpukan_redo.size}")

    def quick_dequeue(self, k):
        self.entry_k.delete(0, tk.END)
        self.entry_k.insert(0, str(k))
        if self.active_mode == "QUEUE - DEQUEUE NAIF":
            self.execute_dequeue_naif()
        else:
            self.execute_dequeue_circular()

    def execute_dequeue_naif(self):
        k_str = self.entry_k.get().strip()
        if not k_str.isdigit() or int(k_str) <= 0:
            messagebox.showwarning("Peringatan", "Masukkan jumlah pesanan k yang valid!")
            return

        k = int(k_str)
        if self.q_naif.size == 0:
            messagebox.showinfo("Info", "Antrean naif sudah kosong!")
            return

        t0 = time.perf_counter()
        keluar, total_geseran = self.q_naif.dequeue_batch(k)
        duration_ms = (time.perf_counter() - t0) * 1000

        self.q_circ.dequeue_batch(len(keluar))

        self.tumpukan_undo.push(("DEQUEUE", keluar))
        self.tumpukan_redo.clear()

        self.render_table()
        self.lbl_detail_selection.config(
            text=f"{len(keluar):,} pesanan keluar dari Antrean Naif | {total_geseran:,} elemen digeser | Sisa: {self.q_naif.size:,}"
        )

        self.log_command(f"> queue_dequeue_naive {k}")
        self.log_command(f"  {len(keluar):,} pesanan keluar | {total_geseran:,} elemen digeser [M2 - queue naif] {duration_ms:.2f} ms")

    def execute_dequeue_circular(self):
        k_str = self.entry_k.get().strip()
        if not k_str.isdigit() or int(k_str) <= 0:
            messagebox.showwarning("Peringatan", "Masukkan jumlah pesanan k yang valid!")
            return

        k = int(k_str)
        if self.q_circ.size == 0:
            messagebox.showinfo("Info", "Antrean circular sudah kosong!")
            return

        t0 = time.perf_counter()
        keluar, _ = self.q_circ.dequeue_batch(k)
        duration_ms = (time.perf_counter() - t0) * 1000

        self.q_naif.dequeue_batch(len(keluar))

        self.tumpukan_undo.push(("DEQUEUE", keluar))
        self.tumpukan_redo.clear()

        self.render_table()
        self.lbl_detail_selection.config(
            text=f"{len(keluar):,} pesanan keluar dari Antrean Circular | 0 elemen digeser (front={self.q_circ.front}, rear={self.q_circ.rear}) | Sisa: {self.q_circ.size:,}"
        )

        self.log_command(f"> queue_dequeue_circular {k}")
        self.log_command(f"  {len(keluar):,} pesanan keluar | 0 elemen digeser [M2 - queue circular] {duration_ms:.2f} ms")

    def execute_undo(self):
        if self.tumpukan_undo.is_empty():
            self.log_command("> stack_undo")
            self.log_command("  tumpukan undo kosong, tidak ada yang dibatalkan [M2 - stack] 0.01 ms")
            messagebox.showinfo("Info", "Tumpukan undo kosong!")
            return

        t0 = time.perf_counter()
        action = self.tumpukan_undo.pop()
        tipe, data = action

        if tipe == "ENQUEUE":
            p = data
            self.q_naif.pop_rear()
            self.q_circ.pop_rear()
            self.tumpukan_redo.push(action)
            dur = (time.perf_counter() - t0) * 1000

            self.render_table()
            self.lbl_detail_selection.config(
                text=f"Undo: {p.oid} dikeluarkan lagi dari belakang. Panjang antrean: {self.q_circ.size:,}"
            )
            self.log_command("> stack_undo")
            self.log_command(f"  {p.oid} dikeluarkan lagi dari belakang [M2 - stack] {dur:.2f} ms")
            self.log_command(f"  tumpukan undo {self.tumpukan_undo.size}, redo {self.tumpukan_redo.size}")

        elif tipe == "DEQUEUE":
            daftar = data
            self.q_naif.push_front_batch(daftar)
            self.q_circ.push_front_batch(daftar)
            self.tumpukan_redo.push(action)
            dur = (time.perf_counter() - t0) * 1000

            self.render_table()
            self.lbl_detail_selection.config(
                text=f"Undo: {len(daftar):,} pesanan dikembalikan ke DEPAN antrean. Panjang antrean: {self.q_circ.size:,}"
            )
            self.log_command("> stack_undo")
            self.log_command(f"  {len(daftar):,} pesanan dikembalikan ke DEPAN antrean circular [M2 - stack] {dur:.2f} ms")
            self.log_command(f"  tumpukan undo {self.tumpukan_undo.size}, redo {self.tumpukan_redo.size}")

        self.build_form_inputs()

    def execute_redo(self):
        if self.tumpukan_redo.is_empty():
            self.log_command("> stack_redo")
            self.log_command("  tumpukan redo kosong, tidak ada yang diulang [M2 - stack] 0.01 ms")
            messagebox.showinfo("Info", "Tumpukan redo kosong!")
            return

        t0 = time.perf_counter()
        action = self.tumpukan_redo.pop()
        tipe, data = action

        if tipe == "ENQUEUE":
            p = data
            self.q_naif.enqueue(p)
            self.q_circ.enqueue(p)
            self.tumpukan_undo.push(action)
            dur = (time.perf_counter() - t0) * 1000

            self.render_table()
            self.lbl_detail_selection.config(
                text=f"Redo: {p.oid} masuk kembali ke belakang. Panjang antrean: {self.q_circ.size:,}"
            )
            self.log_command("> stack_redo")
            self.log_command(f"  {p.oid} masuk kembali ke belakang [M2 - stack] {dur:.2f} ms")
            self.log_command(f"  tumpukan undo {self.tumpukan_undo.size}, redo {self.tumpukan_redo.size}")

        elif tipe == "DEQUEUE":
            daftar = data
            k = len(daftar)
            self.q_naif.dequeue_batch(k)
            self.q_circ.dequeue_batch(k)
            self.tumpukan_undo.push(action)
            dur = (time.perf_counter() - t0) * 1000

            self.render_table()
            self.lbl_detail_selection.config(
                text=f"Redo: {k:,} pesanan keluar lagi dari antrean. Panjang antrean: {self.q_circ.size:,}"
            )
            self.log_command("> stack_redo")
            self.log_command(f"  {k:,} pesanan keluar lagi dari antrean circular [M2 - stack] {dur:.2f} ms")
            self.log_command(f"  tumpukan undo {self.tumpukan_undo.size}, redo {self.tumpukan_redo.size}")

        self.build_form_inputs()

    # Operasi M3: Sort & Search
    def execute_insertion_sort(self):
        n_str = self.entry_sort_n.get().strip()
        if not n_str.isdigit() or int(n_str) <= 0:
            messagebox.showwarning("Peringatan", "Masukkan jumlah baris n yang valid!")
            return

        n = int(n_str)
        key = self.combo_sort_key.get()

        data_to_sort = self.master_list[:n]
        res, comps, shifts, dur_ms, err = insertion_sort(data_to_sort, key)

        if err:
            self.log_command(f"> insertion_sort jumlah={n}")
            self.log_command(f"  {err}")
            messagebox.showwarning("Ditolak", err)
            return

        self.sorted_list = ListWrapper(res)
        self.current_view_mode = "SORTED"
        self.current_page = 0
        self.render_table()

        self.lbl_detail_selection.config(
            text=f"Insertion Sort: {n:,} pesanan terurut menurut '{key}' | {comps:,} perbandingan | {shifts:,} pemindahan | {dur_ms:.2f} ms"
        )
        self.log_command(f"> insertion_sort jumlah={n:,} kunci={key}")
        self.log_command(f"  {n:,} pesanan terurut | {comps:,} perbandingan [M3 - insertion sort] {dur_ms:.2f} ms")

    def execute_merge_sort(self):
        n_str = self.entry_sort_n.get().strip()
        if not n_str.isdigit() or int(n_str) <= 0:
            messagebox.showwarning("Peringatan", "Masukkan jumlah baris n yang valid!")
            return

        n = int(n_str)
        key = self.combo_sort_key.get()

        data_to_sort = self.master_list[:n]
        res, comps, shifts, dur_ms, _ = merge_sort(data_to_sort, key)

        self.sorted_list = ListWrapper(res)
        if key == "oid" and n == len(self.master_list):
            self.oid_sorted_list = res

        self.current_view_mode = "SORTED"
        self.current_page = 0
        self.render_table()

        time_str = f"{dur_ms / 1000:.2f} s" if dur_ms >= 1000 else f"{dur_ms:.2f} ms"
        self.lbl_detail_selection.config(
            text=f"Merge Sort: {n:,} pesanan terurut menurut '{key}' | {comps:,} perbandingan | {shifts:,} pemindahan | {time_str}"
        )
        self.log_command(f"> merge_sort jumlah={n:,} kunci={key}")
        self.log_command(f"  {n:,} pesanan terurut | {comps:,} perbandingan [M3 - merge sort] {time_str}")

    def execute_linear_search(self):
        target = self.entry_search_target.get().strip()
        if not target:
            messagebox.showwarning("Peringatan", "Masukkan target OID!")
            return

        idx, comps, dur_ms = linear_search(self.master_list, target)

        if idx != -1:
            self.current_view_mode = "M1"
            self.jump_to_index(idx)
            item = self.master_list[idx]
            self.lbl_detail_selection.config(
                text=f"Linear Search: Ditemukan {item.oid} ({item.pelanggan}) di indeks {idx:,} | {comps:,} perbandingan | {dur_ms:.2f} ms"
            )
            self.log_command(f"> linear_search {target}")
            self.log_command(f"  ditemukan di indeks {idx:,} | {comps:,} perbandingan [M3 - linear] {dur_ms:.2f} ms")
        else:
            self.log_command(f"> linear_search {target}")
            self.log_command(f"  tidak ditemukan | {comps:,} perbandingan [M3 - linear] {dur_ms:.2f} ms")
            messagebox.showinfo("Hasil", f"Pesanan {target} tidak ditemukan!")

    def execute_binary_search(self):
        target = self.entry_search_target.get().strip()
        if not target:
            messagebox.showwarning("Peringatan", "Masukkan target OID!")
            return

        built_now = False
        if self.oid_sorted_list is None:
            res, _, _, dur_build, _ = merge_sort(self.master_list, "oid")
            self.oid_sorted_list = res
            built_now = True

        idx, comps, dur_ms = binary_search(self.oid_sorted_list, target)

        self.sorted_list = ListWrapper(self.oid_sorted_list)
        self.current_view_mode = "SORTED"

        self.log_command(f"> binary_search {target}")
        if built_now:
            self.log_command(f"  daftar terurut oid dibangun sekali (merge sort) {dur_build:.2f} ms")

        if idx != -1:
            self.jump_to_index(idx)
            item = self.oid_sorted_list[idx]
            self.lbl_detail_selection.config(
                text=f"Binary Search: Ditemukan {item.oid} ({item.pelanggan}) di baris {idx + 1:,} | {comps:,} perbandingan | {dur_ms:.2f} ms"
            )
            self.log_command(f"  ditemukan di baris {idx + 1:,} | {comps:,} perbandingan [M3 - binary] {dur_ms:.2f} ms")
        else:
            self.log_command(f"  tidak ditemukan | {comps:,} perbandingan [M3 - binary] {dur_ms:.2f} ms")
            messagebox.showinfo("Hasil", f"Pesanan {target} tidak ditemukan!")

    def run(self):
        self.root.mainloop()
