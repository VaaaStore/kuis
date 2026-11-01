# Kuis latihan UTS

Web statis tanpa framework. Isi soal dibaca dari `soal.json`, jadi mengganti soal cukup mengganti file itu.

## Pasang di GitHub Pages
1. Unggah `index.html`, `style.css`, `app.js`, dan `soal.json` ke satu repositori (di root).
2. Settings, Pages, Deploy from a branch, pilih `main` dan folder `/ (root)`.
3. Buka `https://<username>.github.io/<nama-repo>/`.

Untuk uji di laptop: jalankan `python -m http.server` di folder ini, lalu buka `http://localhost:8000`.
Membuka `index.html` langsung dari folder tidak bisa, karena browser memblokir pembacaan JSON dari file lokal.

## Ganti soal tiap hari
Ganti isi `soal.json`, lalu commit. GitHub Pages butuh sekitar 1 sampai 10 menit untuk menayangkan perubahan.

Dari file .txt (format seperti file UTS Anda, dengan baris kunci di akhir):

    KUNCI: 1b 2c 3a 4d ...

jalankan:

    python txt_ke_json.py soal_baru.txt -o soal.json --judul "Judul kuis"

Kunci juga bisa dikirim lewat argumen: `--kunci "1b 2c 3a"`.

## Format soal.json
```json
{
  "judul": "UTS Algoritma dan Pemrograman",
  "soal": [
    {
      "id": 7,
      "materi": "Materi 1: Dasar Python",
      "pertanyaan": "Perhatikan potongan kode berikut:",
      "kode": "x = 10\nz = x * 3\nprint(z)",
      "lanjutan": "Berapa nilai keluaran akhir?",
      "opsi": ["30", "32", "35", "29", "33"],
      "jawaban": "a",
      "penjelasan": "10 * 3 = 30."
    }
  ]
}
```
- Wajib: `pertanyaan`, `opsi` (2 sampai 10), `jawaban`.
- `jawaban` boleh huruf (`"a"` untuk opsi pertama) atau angka mulai dari 0.
- Opsional: `id`, `materi` (dipakai untuk rincian skor), `kode`, `lanjutan`, `penjelasan`, `acakOpsi`.
- Teks mendukung `` `kode` ``, `**tebal**`, dan `*miring*`. Bungkus ekspresi seperti `2*3` dengan backtick.
- Opsi yang merujuk opsi lain ("Pilihan a dan b benar", "Semua benar") otomatis tidak diacak. Untuk mematikan acak pada soal lain, tambahkan `"acakOpsi": false`.
- Soal yang formatnya salah dilewati, dan daftarnya muncul di halaman awal.

Pintasan keyboard saat kuis: tombol a sampai e memilih opsi, Enter lanjut.
