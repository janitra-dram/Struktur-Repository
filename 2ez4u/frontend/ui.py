import tkinter as tk
from tkinter import ttk, messagebox
import time
from backend.m1_pesanan import Array, LinkList

class AppUI:
    def __init__(self, root):
        self.root = root
        self.root.title("2EZ4U Food Delivery - Milestone 1")
        self.root.geometry("800x500")
        
        # Inisialisasi struktur data dari backend
        self.array_data = Array()
        self.linked_list_data = LinkList()
        
        self.create_widgets()

    def create_widgets(self):
        # Frame Kiri: Menu
        left_frame = tk.Frame(self.root, width=200, bg="lightgray", relief=tk.SUNKEN, borderwidth=2)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        
        tk.Label(left_frame, text="M1 - DATA PESANAN", bg="lightgray", font=("Arial", 10, "bold")).pack(pady=10)
        
        menus = [
            ("Lihat Pesanan", self.lihat_pesanan),
            ("Tambah Reguler", self.tambah_reguler),
            ("Tambah Prioritas", self.tambah_prioritas),
            ("Tambah VIP", self.tambah_vip),
            ("Hapus Pesanan", self.hapus_pesanan)
        ]
        
        for text, command in menus:
            btn = tk.Button(left_frame, text=text, command=command, width=20)
            btn.pack(pady=5, padx=10)
            
        # Frame Kanan Atas: Input & Hasil
        right_frame = tk.Frame(self.root)
        right_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Form Input
        form_frame = tk.Frame(right_frame)
        form_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(form_frame, text="Data Pesanan (Nama):").pack(side=tk.LEFT, padx=5)
        self.entry_pesanan = tk.Entry(form_frame, width=30)
        self.entry_pesanan.pack(side=tk.LEFT, padx=5)
        
        # Listbox untuk menampilkan data Array
        tk.Label(right_frame, text="Tampilan Data (Array):").pack(anchor=tk.W)
        self.listbox = tk.Listbox(right_frame, height=12)
        self.listbox.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Frame Bawah: Command Log & Waktu Eksekusi
        bottom_frame = tk.Frame(self.root, height=100, relief=tk.SUNKEN, borderwidth=2)
        bottom_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)
        
        tk.Label(bottom_frame, text="COMMAND LOG & WAKTU EKSEKUSI:", font=("Arial", 9, "bold")).pack(anchor=tk.W, padx=5)
        self.log_text = tk.Text(bottom_frame, height=6, bg="black", fg="lime", font=("Consolas", 9))
        self.log_text.pack(fill=tk.BOTH, padx=5, pady=5)

    def log_command(self, command, arr_time, ll_time):
        log_msg = f"> {command}\n  Array Time: {arr_time:.6f} ms | LinkedList Time: {ll_time:.6f} ms\n"
        self.log_text.insert(tk.END, log_msg)
        self.log_text.see(tk.END)

    def refresh_listbox(self):
        self.listbox.delete(0, tk.END)
        for i in range(self.array_data.size):
            self.listbox.insert(tk.END, f"[{i}] {self.array_data.get(i)}")

    def get_input(self):
        val = self.entry_pesanan.get()
        if not val:
            messagebox.showwarning("Peringatan", "Input pesanan tidak boleh kosong!")
            return None
        return val

    def lihat_pesanan(self):
        self.refresh_listbox()
        self.log_command("LIHAT PESANAN (Refresh UI)", 0, 0)

    def tambah_reguler(self):
        val = self.get_input()
        if val:
            # Test Array Time
            start = time.perf_counter()
            self.array_data.tambah_reguler(val)
            arr_time = (time.perf_counter() - start) * 1000
            
            # Test LinkedList Time
            start = time.perf_counter()
            self.linked_list_data.tambah_reguler(val)
            ll_time = (time.perf_counter() - start) * 1000
            
            self.refresh_listbox()
            self.log_command(f"TAMBAH REGULER: {val}", arr_time, ll_time)
            self.entry_pesanan.delete(0, tk.END)

    def tambah_prioritas(self):
        val = self.get_input()
        if val:
            start = time.perf_counter()
            self.array_data.tambah_prioritas(val)
            arr_time = (time.perf_counter() - start) * 1000
            
            start = time.perf_counter()
            self.linked_list_data.tambah_prioritas(val)
            ll_time = (time.perf_counter() - start) * 1000
            
            self.refresh_listbox()
            self.log_command(f"TAMBAH PRIORITAS: {val}", arr_time, ll_time)
            self.entry_pesanan.delete(0, tk.END)

    def tambah_vip(self):
        val = self.get_input()
        if val:
            start = time.perf_counter()
            self.array_data.tambah_vip(val)
            arr_time = (time.perf_counter() - start) * 1000
            
            start = time.perf_counter()
            self.linked_list_data.tambah_vip(val)
            ll_time = (time.perf_counter() - start) * 1000
            
            self.refresh_listbox()
            self.log_command(f"TAMBAH VIP: {val}", arr_time, ll_time)
            self.entry_pesanan.delete(0, tk.END)

    def hapus_pesanan(self):
        selection = self.listbox.curselection()
        if not selection:
            messagebox.showwarning("Peringatan", "Pilih pesanan di listbox untuk dihapus!")
            return
            
        index = selection[0]
        
        start = time.perf_counter()
        val_arr = self.array_data.delete(index)
        arr_time = (time.perf_counter() - start) * 1000
        
        start = time.perf_counter()
        val_ll = self.linked_list_data.delete(index)
        ll_time = (time.perf_counter() - start) * 1000
        
        self.refresh_listbox()
        self.log_command(f"HAPUS PESANAN [{index}]: {val_arr}", arr_time, ll_time)

    def run(self):
        self.root.mainloop()
