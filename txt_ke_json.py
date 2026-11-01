#!/usr/bin/env python3
"""Ubah soal pilihan ganda berformat .txt menjadi soal.json untuk web kuis.

Pemakaian:
    python txt_ke_json.py soal.txt
    python txt_ke_json.py soal.txt -o soal.json --judul "UTS Algoritma"
    python txt_ke_json.py soal.txt --kunci "1b 2c 3a ..."

Format .txt yang dikenali:
    --- MATERI 1: Nama materi ---          (baris pemisah materi, opsional)
    1. Teks pertanyaan
       (baris kode atau teks lanjutan, opsional)
       a. Opsi pertama
       b. Opsi kedua
    ...
    KUNCI: 1b 2c 3a 4d ...                 (kunci jawaban, di akhir file)

Kunci jawaban juga bisa dikirim lewat --kunci. Soal tanpa kunci dilewati
dan dilaporkan di layar.
"""
import argparse
import json
import re
import sys
import textwrap

RE_SOAL = re.compile(r'^(\d+)\.\s+(.*\S)\s*$')
RE_OPSI = re.compile(r'^\s+([a-j])\.\s+(.*\S)\s*$')
RE_BAGIAN = re.compile(r'^-{2,}\s*(.+?)\s*-{2,}\s*$')
RE_KUNCI = re.compile(r'(\d+)\s*[.\-:)]?\s*([a-jA-J])\b')
RE_KODE = re.compile(
    r'^\s*(def |for |while |if |elif |else\s*:|return\b|import |from .+ import |class |print\(|[A-Za-z_][\w.]*\(.*\)\s*$)'
    r'|(^|\s)[A-Za-z_][\w\[\]\.]*\s*(=|\+=|-=|\*=|/=)\s+\S'
)


def bersihkan(teks):
    """Buang penanda LaTeX sederhana ($m \\times n$) menjadi teks biasa."""
    teks = re.sub(r'\$([^$]+)\$', lambda m: m.group(1), teks)
    return teks.replace('\\times', '×').strip()


def rapikan_materi(label):
    label = re.sub(r'\s*\(\d+\s*-\s*\d+\)', '', label).strip()
    if label.upper().startswith('MATERI'):
        return 'Materi' + label[6:]
    if label.isupper():
        return label.capitalize()
    return label


def pisah_baris(baris):
    """Pisahkan baris lanjutan menjadi (teks_sebelum, kode, teks_sesudah)."""
    idx = [i for i, b in enumerate(baris) if RE_KODE.search(b)]
    if not idx:
        return [b.strip() for b in baris], '', []
    awal, akhir = idx[0], idx[-1]
    kode = textwrap.dedent('\n'.join(baris[awal:akhir + 1])).strip('\n')
    sebelum = [b.strip() for b in baris[:awal]]
    sesudah = [b.strip() for b in baris[akhir + 1:]]
    return sebelum, kode, sesudah


def baca_txt(isi):
    soal, saat_ini, materi, kunci_teks = [], None, '', []
    di_kunci = False

    def tutup():
        nonlocal saat_ini
        if saat_ini and len(saat_ini['opsi']) >= 2:
            soal.append(saat_ini)
        saat_ini = None

    for mentah in isi.splitlines():
        if re.match(r'^\s*KUNCI\b', mentah, re.I):
            tutup()
            di_kunci = True
        if di_kunci:
            kunci_teks.append(mentah)
            continue
        if not mentah.strip():
            continue
        bagian = RE_BAGIAN.match(mentah)
        if bagian:
            tutup()
            materi = rapikan_materi(bagian.group(1))
            continue
        opsi = RE_OPSI.match(mentah)
        if opsi and saat_ini is not None:
            saat_ini['opsi'].append(bersihkan(opsi.group(2)))
            continue
        baru = RE_SOAL.match(mentah)
        if baru:
            tutup()
            saat_ini = {'id': int(baru.group(1)), 'materi': materi,
                        'pertanyaan': baru.group(2), 'baris': [], 'opsi': []}
            continue
        if saat_ini is not None and not saat_ini['opsi']:
            saat_ini['baris'].append(mentah.rstrip())
    tutup()
    return soal, '\n'.join(kunci_teks)


def main():
    ap = argparse.ArgumentParser(description='Ubah soal .txt menjadi soal.json')
    ap.add_argument('txt', help='file soal berformat .txt')
    ap.add_argument('-o', '--output', default='soal.json')
    ap.add_argument('--judul', default='Latihan Soal')
    ap.add_argument('--kunci', default='', help='contoh: "1b 2c 3a"')
    args = ap.parse_args()

    with open(args.txt, encoding='utf-8') as f:
        soal, kunci_teks = baca_txt(f.read())

    kunci = {int(n): h.lower() for n, h in RE_KUNCI.findall(kunci_teks)}
    kunci.update({int(n): h.lower() for n, h in RE_KUNCI.findall(args.kunci)})

    hasil, tanpa_kunci = [], []
    for s in soal:
        sebelum, kode, sesudah = pisah_baris(s.pop('baris'))
        s['pertanyaan'] = bersihkan('\n'.join([s['pertanyaan']] + [b for b in sebelum if b]))
        item = {'id': s['id']}
        if s['materi']:
            item['materi'] = s['materi']
        item['pertanyaan'] = s['pertanyaan']
        if kode:
            item['kode'] = kode
        if any(sesudah):
            item['lanjutan'] = bersihkan(' '.join(b for b in sesudah if b))
        item['opsi'] = s['opsi']
        huruf = kunci.get(s['id'])
        if huruf is None or 'abcdefghij'.index(huruf) >= len(s['opsi']):
            tanpa_kunci.append(s['id'])
            continue
        item['jawaban'] = huruf
        hasil.append(item)

    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump({'judul': args.judul, 'soal': hasil}, f, ensure_ascii=False, indent=2)
        f.write('\n')

    print(f'{len(hasil)} soal ditulis ke {args.output}.')
    if tanpa_kunci:
        print('Dilewati karena kunci jawaban tidak ada atau tidak valid: '
              + ', '.join(map(str, tanpa_kunci)), file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
