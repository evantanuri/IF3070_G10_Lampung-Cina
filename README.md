# IF3070_G10_Lampung-Cina

Tugas Besar I IF3070 Dasar Intelegensi Artifisial: **Pencarian Solusi Penempatan Kendaraan pada Geladak Kapal dengan Local Search**.

Program untuk mencari penempatan kendaraan pada satu atau beberapa kapal kargo supaya nilai objective function setinggi mungkin, dengan tetap memenuhi seluruh batasan (tidak bertumpuk, di dalam geladak, dan tidak melebihi kapasitas kapal).

## Anggota Kelompok 10

| Nama | NIM |
|---|---|
| Indanna Halwah Raqiqah Masyhur | 18224014 |
| Evan Nathanael Tanuri | 18224019 |
| Muhammad Okto Huzainy | 18224021 |


Pembagian tugas:
- Indanna: Hill-Climbing with Sideways Move, Genetic Algorithm, serta format dan bagian umum laporan
- Evan: varian Hill-Climbing lainnya, alur program, dan pengelolaan repository GitHub
- Okto: Simulated Annealing dan kode visualisasi

## Algoritma yang Diimplementasikan

| No | Algoritma | Berkas |
|---|---|---|
| 1 | Simple Hill Climbing | `src/algorithms.py` |
| 2 | Steepest Ascent Hill Climbing | `src/algorithms.py` |
| 3 | Hill Climbing with Sideways Move | `src/hill_climbing_sideways_move.py` |
| 4 | Random Restart Hill Climbing | `src/algorithms.py` |
| 5 | Stochastic Hill Climbing | `src/algorithms.py` |
| 6 | Simulated Annealing | `src/simulated_annealing.py` |
| 7 | Genetic Algorithm | `src/genetic_algorithm.py` |

## Struktur Repositori

```
.
├── main.py                  # program utama (menu, input parameter, pencatatan hasil)
├── input.json               
├── input2.json              
├── input3.json              
├── src/
│   ├── entities.py          
│   ├── state.py             
│   ├── algorithms.py        # algoritma hill climbing selain Sideways Move
│   ├── hill_climbing_sideways_move.py
│   ├── simulated_annealing.py
│   ├── genetic_algorithm.py
│   └── visualizer.py        
├── output/                  
└── docs/                    # Dokumen laporan
```

## Persiapan

Dibutuhkan Python 3 dan pustaka `matplotlib`.

```
pip install matplotlib
```

## Cara Menjalankan

Jalankan dari folder utama repositori.

```
python main.py
```

(Pada Windows dapat memakai `py main.py`.)

Program menampilkan menu:

```
PILIH ALGORITMA SEARCHING:
  [1] Simple Hill Climbing
  [2] Steepest Ascent Hill Climbing
  [3] Hill Climbing with Sideways Move
  [4] Random Restart Hill Climbing
  [5] Stochastic Hill Climbing
  [6] Simulated Annealing
  [7] Genetic Algorithm
  [8] Clean output folder (hapus semua isinya)
```

Setelah memilih algoritma, program menanyakan:

1. Nama berkas masukan (`input.json` jika dikosongkan).
2. Berapa kali algoritma dijalankan.
3. Parameter khusus algoritma (jika ada):

| Menu | Parameter yang ditanyakan | Bawaan |
|---|---|---|
| 3. Sideways Move | Maksimum sideways move | 30 |
| 4. Random Restart | Maksimum restart | 30 |
| 5. Stochastic | Maksimum iterasi | 100 |
| 7. Genetic Algorithm | Ukuran populasi | 30 |
| 7. Genetic Algorithm | Jumlah generasi | 100 |

Contoh menjalankan Genetic Algorithm pada `input2.json` sebanyak 3 kali dengan populasi 30 dan 100 generasi:

```
Pilih nomor algoritma: 7
Masukkan nama file input (default: input.json): input2.json
Berapa kali algoritma dijalankan? : 3
Masukkan ukuran populasi GA (default: 30): 30
Masukkan jumlah generasi GA (default: 100): 100
```

Menu 8 menghapus seluruh isi folder `output/`. Jangan dijalankan sebelum hasil yang dibutuhkan disimpan.

## Format Berkas Masukan

Berkas JSON berisi daftar kapal dan kendaraan.

```json
{
  "ships": [
    { "id": "S1", "dimensions": { "w": 12, "l": 18 }, "max_capacity": 300 }
  ],
  "vehicles": [
    {
      "id": "V01",
      "dimensions": { "w": 2, "l": 4 },
      "shipping_fee": 65,
      "weight": 40,
      "orientation": "Horizontal",
      "eta": 2
    }
  ]
}
```

Program mendukung lebih dari satu kapal (bonus multi-kapal).

## Representasi dan Objective Function

- **State**: pemetaan setiap kendaraan ke `None` (di luar kapal) atau ke penempatan `{ship_id, x, y, orientation}`.
- **Neighbor**: memindahkan kendaraan ke koordinat lain, mengubah orientasi, atau menukar dua kendaraan.
- **Objective function** (`calculate_fitness` pada `src/state.py`):

  ```
  f(s) = jumlah ( ShippingFee(v) - alpha * ETA(v) ),  untuk kendaraan v yang diangkut, alpha = 5
  ```

  Pengurang `alpha * ETA` merupakan heuristik tambahan kelompok. Penjelasan lengkap ada di laporan.

## Keluaran

Setiap eksekusi membuat folder `output/Run_<tanggal-waktu>/` berisi, untuk tiap run:

- `state_awal_run_N.png`: gambar state awal
- `state_akhir_run_N.png`: gambar state akhir
- `grafik_fitness_run_N.png`: grafik objective function terhadap iterasi (untuk Genetic Algorithm: nilai maksimum dan rata-rata populasi terhadap generasi)
- `grafik_probabilitas_sa_run_N.png`: grafik e^(ΔE/T) (khusus Simulated Annealing)

Ringkasan tiap run dicetak di terminal: durasi pencarian, jumlah iterasi, nilai awal, dan nilai akhir. Untuk Genetic Algorithm juga dicetak jumlah populasi, dan untuk Sideways Move dicetak alasan berhenti serta total gerakan sideways.

Pada Genetic Algorithm, state awal yang digambar adalah individu terbaik pada populasi awal (generasi 0).

### Hasil Eksperimen yang Disimpan

Folder berikut berisi hasil eksperimen yang dipakai pada laporan (berkas masukan `input2.json`, 3 run per konfigurasi):

| Folder | Isi |
|---|---|
| `output/GA-Eksperimen1-V1` sampai `V3` | Genetic Algorithm, Eksperimen 1 (jumlah populasi tetap, banyak iterasi divariasikan) |
| `output/GA-Eksperimen2-V1` sampai `V3` | Genetic Algorithm, Eksperimen 2 (banyak iterasi tetap, jumlah populasi divariasikan) |
| `output/HC-SidewaysMove` | Hill Climbing with Sideways Move |

Rincian parameter dan analisis hasil ada di laporan pada folder `docs/`.
