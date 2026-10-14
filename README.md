# 2EZ4U APP

Proyek Akhir Struktur Data & Analisa Algoritma (EC234303).

## Struktur Folder
- `data/`: Berisi data CSV (200.000 data `pesanan.csv` dan graf `peta.csv`).
- `backend/`:
  - `m1_pesanan.py`: Larik dinamis (Array) dan Senarai Berantai (LinkList).
  - `m2_antrean.py`: Tumpukan (Stack), Konversi & Evaluasi Postfix Kasir, Antrean Naif vs Melingkar (Circular), dan Undo/Redo.
  - `m3_laporan.py`: Insertion Sort, Merge Sort, Linear Search, dan Binary Search.
- `frontend/`:
  - `ui.py`: Antarmuka desktop menggunakan Tkinter dengan panel menu di kiri, workspace di kanan, dan log command di bawah.
- `app.py`: Entry point utama aplikasi.

## Cara Menjalankan
Buka terminal pada folder proyek:
```bash
cd "C:\Users\Damar\OneDrive\Documents\SRUKDAT\2EZ4U APP\2ez4u"
python app.py
```

---

## Analisis Milestone 3 (Sort & Search)

### 1. Tabel $n$ vs Perbandingan (Sorting)
Kunci pengurutan: `harga`

| $n$ (Jumlah Data) | Insertion Sort (Perbandingan) | Merge Sort (Perbandingan) | Keterangan |
| :---: | :---: | :---: | :--- |
| **10** | 24 | 21 | Keduanya stabil, urutan data dengan harga sama tetap terjaga. |
| **2.000** | 962.430 | 19.240 | Merge sort ~50x lebih sedikit perbandingan. |
| **4.000** | 3.831.520 | 42.355 | Saat $n$ naik 2x, perbandingan Insertion Sort naik ~4x ($O(n^2)$), sedangkan Merge Sort hanya naik ~2x ($O(n \log n)$). |
| **200.000** | *DITOLAK* | 3.226.139 | Batas Insertion Sort adalah 20.000 baris untuk mencegah freeze. |

### 2. Tabel Perbandingan Pencarian (Searching)
Target: `O-137442` pada 200.000 data pesanan

| Algoritma | Kompleksitas | Jumlah Perbandingan | Waktu Eksekusi | Keterangan |
| :--- | :---: | :---: | :---: | :--- |
| **Linear Search** | $O(n)$ | 137.442 | ~26 ms | Tidak butuh data terurut, menelusuri satu per satu dari awal. |
| **Binary Search** | $O(\log n)$ | 17 | ~0.05 ms | Membutuhkan data terurut menurut OID (dibangun sekali dengan Merge Sort). |

### 3. Alasan Pemilihan Algoritma
- **Insertion Sort**: Dipilih untuk data berukuran kecil ($n \le 2000$) atau data yang sudah hampir terurut, karena bekerja in-place tanpa memori tambahan ($O(1)$ auxiliary space) dan stabil.
- **Merge Sort**: Dipilih untuk data besar ($n$ hingga 200.000) karena kompleksitasnya terjamin stabil $O(n \log n)$ dalam semua skenario (best, average, worst case).
- **Linear Search**: Dipilih untuk pencarian satu kali (*one-time lookup*) pada data acak yang belum terurut, karena biaya pengurutan awal jauh lebih besar daripada satu kali pencarian linear.
- **Binary Search**: Dipilih jika data akan dicari berkali-kali (*frequent lookups*), di mana biaya awal pengurutan terbayar lunas oleh efisiensi pencarian $O(\log n)$.
