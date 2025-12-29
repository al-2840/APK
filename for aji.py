# Aplikasi Sistem Usaha Terpadu: 
# Rental Mobil + Perbaikan Mobil + Restoran + Sparepart

NAMA_TEMPAT = "Belum"

# ------------------ DATA AWAL ------------------
mobil_list = [
    {"nama": "Toyota Avanza", "no_polisi": "B 1234 ABC", "status": "Tersedia"},
    {"nama": "Honda Brio", "no_polisi": "B 5678 DEF", "status": "Tersedia"},
    {"nama": "Mitsubishi Xpander", "no_polisi": "B 9101 GHI", "status": "Sudah dirental"}
]

makanan_list = [
    {"nama": "Nasi Goreng Spesial", "harga": 25000},
    {"nama": "Mie Ayam Bakso", "harga": 20000},
    {"nama": "Ayam Bakar Madu", "harga": 30000},
    {"nama": "Es Teh Manis", "harga": 5000}
]

penjualan_list = [
    {"sparepart": "Oli Mesin Shell 1L", "harga": 85000, "stok": 10},
    {"sparepart": "Kampas Rem Depan", "harga": 150000, "stok": 5},
    {"sparepart": "Filter Udara", "harga": 75000, "stok": 8}
]

karyawan_list = ["Andi Pratama", "Budi Santoso", "Rian Saputra", "Doni Prasetyo", "Rizky Ramadhan"]
perbaikan_list = []
inventaris_list = [{"barang": "Kunci Inggris", "jumlah": "5"},{"barang": "Dongkrak Hidrolik", "jumlah": "2"}]

# ------------------ FUNGSI RENTAL MOBIL ------------------

def tambah_mobil():
    print("\n=== TAMBAH MOBIL RENTAL ===")
    nama = input("Nama mobil: ")
    no_polisi = input("Nomor polisi: ")
    mobil_list.append({"nama": nama, "no_polisi": no_polisi, "status": "Tersedia"})
    print("Mobil berhasil ditambahkan!")

def cari_mobil():
    print("\n=== CARI MOBIL RENTAL ===")
    keyword = input("Nama mobil / nomor polisi: ")
    for mobil in mobil_list:
        if keyword.lower() in mobil["nama"].lower() or keyword.upper() in mobil["no_polisi"].upper():
            print(f"Nama: {mobil['nama']} | No. Polisi: {mobil['no_polisi']} | Status: {mobil['status']}")
            return
    print("Mobil tidak ditemukan.")

def hapus_mobil():
    print("\n=== HAPUS MOBIL RENTAL ===")
    no_polisi = input("Nomor polisi mobil yang ingin dihapus: ")
    for mobil in mobil_list:
        if mobil["no_polisi"].upper() == no_polisi.upper():
            mobil_list.remove(mobil)
            print("Mobil berhasil dihapus.")
            return
    print("Mobil tidak ditemukan.")

def daftar_mobil():
    print("\n=== DAFTAR MOBIL ===")
    if not mobil_list:
        print("Belum ada mobil.")
    else:
        for i, mobil in enumerate(mobil_list, 1):
            print(f"{i}. {mobil['nama']} ({mobil['no_polisi']}) - Status: {mobil['status']}")

def rental_mobil():
    print("\n=== PROSES RENTAL MOBIL ===")
    no_polisi = input("Masukkan nomor polisi mobil yang ingin disewa: ")
    for mobil in mobil_list:
        if mobil["no_polisi"].upper() == no_polisi.upper():
            if mobil["status"] == "Sudah dirental":
                print("Maaf, mobil ini sudah dirental.")
                return
            mobil["status"] = "Sudah dirental"
            print(f"Mobil {mobil['nama']} berhasil dirental.")
            return
    print("Mobil tidak ditemukan.")

# ------------------ FUNGSI RESTORAN ------------------

def tambah_makanan():
    print("\n=== TAMBAH MENU MAKANAN ===")
    nama = input("Nama makanan: ")
    harga = int(input("Harga: "))
    makanan_list.append({"nama": nama, "harga": harga})
    print("Menu makanan ditambahkan!")

def daftar_makanan():
    print("\n=== DAFTAR MENU MAKANAN TERSEDIA ===")
    if not makanan_list:
        print("Belum ada menu.")
    else:
        for i, m in enumerate(makanan_list, 1):
            print(f"{i}. {m['nama']} - Rp {m['harga']}")

def proses_pembayaran_makanan():
    print("\n=== KASIR RESTORAN ===")
    daftar_makanan()
    total = 0
    while True:
        nama = input("Masukkan nama makanan (atau ketik 'selesai'): ")
        if nama.lower() == "selesai": break
        
        ketemu = False
        for m in makanan_list:
            if m["nama"].lower() == nama.lower():
                jumlah = int(input(f"Jumlah porsi {m['nama']}: "))
                subtotal = m["harga"] * jumlah
                total += subtotal
                print(f"Ditambahkan: {jumlah} x {m['nama']} = Rp {subtotal}")
                ketemu = True
                break
        if not ketemu: print("Menu tidak ditemukan.")

    if total > 0:
        print(f"\nTotal: Rp {total}")
        bayar = int(input("Uang bayar: "))
        if bayar >= total:
            print(f"Kembalian: Rp {bayar - total}\nPembayaran berhasil!")
        else:
            print("Uang kurang, transaksi dibatalkan.")

# ------------------ FUNGSI PERBAIKAN MOBIL ------------------

def catat_mobil_servis():
    print("\n=== PENDAFTARAN MOBIL SERVIS ===")
    nama = input("Nama / tipe mobil: ")
    kerusakan = input("Keluhan / kerusakan: ")
    perbaikan_list.append({
        "mobil": nama, "kerusakan": kerusakan, 
        "status": "Menunggu dikerjakan", "mekanik": "-"
    })
    print("Mobil berhasil didaftarkan.")

def daftar_mobil_servis():
    print("\n=== DAFTAR ANTRIAN & PROSES SERVIS ===")
    if not perbaikan_list:
        print("Antrian kosong.")
        return
    for i, p in enumerate(perbaikan_list, 1):
        print(f"{i}. {p['mobil']} | Keluhan: {p['kerusakan']} | Status: {p['status']} | Mekanik: {p['mekanik']}")

def pilih_mekanik_servis():
    print("\n=== PENUGASAN MEKANIK ===")
    if not perbaikan_list:
        print("Tidak ada mobil untuk diservis."); return
    daftar_mobil_servis()
    idx = int(input("Pilih nomor mobil: ")) - 1
    
    print("\n--- MEKANIK TERSEDIA ---")
    for i, k in enumerate(karyawan_list, 1): print(f"{i}. {k}")
    mk = int(input("Pilih nomor mekanik: ")) - 1
    
    perbaikan_list[idx]["mekanik"] = karyawan_list[mk]
    perbaikan_list[idx]["status"] = "Sedang dikerjakan"
    print("Mekanik berhasil ditugaskan!")

def update_status_servis():
    print("\n=== UPDATE STATUS SERVIS ===")
    if not perbaikan_list: print("Data kosong."); return
    daftar_mobil_servis()
    idx = int(input("Pilih nomor mobil: ")) - 1
    print("1. Sedang dikerjakan\n2. Menunggu sparepart\n3. Selesai servis ✔")
    st = input("Pilih status: ")
    if st == "1": perbaikan_list[idx]["status"] = "Sedang dikerjakan"
    elif st == "2": perbaikan_list[idx]["status"] = "Menunggu sparepart"
    elif st == "3": perbaikan_list[idx]["status"] = "Selesai servis"
    print("Status diperbarui!")

# ------------------ FUNGSI SPAREPART ------------------

def tambah_sparepart_baru():
    print("\n=== TAMBAH SPAREPART BARU ===")
    nama = input("Nama sparepart: ")
    for s in penjualan_list:
        if s["sparepart"].lower() == nama.lower():
            print("Sparepart sudah ada!")
            return
    harga = int(input("Harga: "))
    stok = int(input("Stok awal: "))
    penjualan_list.append({"sparepart": nama, "harga": harga, "stok": stok})
    print("Sparepart berhasil ditambahkan.")

def tambah_stok_sparepart():
    print("\n=== TAMBAH STOK SPAREPART ===")
    for i, p in enumerate(penjualan_list, 1):
        print(f"{i}. {p['sparepart']} (Stok: {p['stok']})")
    nama = input("Nama sparepart: ")
    for s in penjualan_list:
        if s["sparepart"].lower() == nama.lower():
            tambah = int(input("Jumlah stok ditambahkan: "))
            s["stok"] += tambah
            print(f"Stok {s['sparepart']} sekarang: {s['stok']}")
            return
    print("Sparepart tidak ditemukan.")

def hapus_sparepart():
    print("\n=== HAPUS SPAREPART ===")
    for i, p in enumerate(penjualan_list, 1):
        print(f"{i}. {p['sparepart']}")
    nama = input("Masukkan nama sparepart yang ingin dihapus: ")
    for s in penjualan_list:
        if s["sparepart"].lower() == nama.lower():
            penjualan_list.remove(s)
            print(f"Sparepart '{nama}' berhasil dihapus.")
            return
    print("Sparepart tidak ditemukan.")

def proses_pembayaran_sparepart():
    print("\n=== PROSES PEMBAYARAN SPAREPART ===")
    for i, p in enumerate(penjualan_list, 1):
        print(f"{i}. {p['sparepart']} - Rp {p['harga']} (Stok: {p['stok']})")

    total = 0
    keranjang = []
    while True:
        nama = input("Nama sparepart (atau 'selesai'): ")
        if nama.lower() == "selesai": break
        
        ketemu = False
        for s in penjualan_list:
            if s["sparepart"].lower() == nama.lower():
                qty = int(input("Jumlah: "))
                if qty > s["stok"]:
                    print("Stok tidak mencukupi!")
                else:
                    subtotal = s["harga"] * qty
                    total += subtotal
                    s["stok"] -= qty
                    keranjang.append((s["sparepart"], qty, subtotal))
                    print(f"Ditambahkan: Rp {subtotal}")
                ketemu = True
                break
        if not ketemu: print("Sparepart tidak ditemukan.")

    if total > 0:
        print("\n--- RINCIAN BELANJA ---")
        for item in keranjang:
            print(f"{item[0]} x{item[1]} = Rp {item[2]}")
        print(f"Total Bayar: Rp {total}")
        
        bayar = int(input("Uang dibayar: Rp "))
        if bayar >= total:
            print(f"Kembalian: Rp {bayar - total}\nTerima kasih!")
        else:
            print("Uang kurang!")

# ------------------ MENU UTAMA ------------------

def menu():
    while True:
        print(f"\n{'='*45}\n      {NAMA_TEMPAT}\n    RENTAL | PERBAIKAN | RESTO | SPAREPART\n{'='*45}")
        print("1. Rental Mobil")
        print("2. Restoran")
        print("3. Perbaikan Mobil")
        print("4. Sparepart")
        print("5. Data Karyawan")
        print("6. Inventaris Alat")
        print("7. Keluar")
        pilih = input("Pilih menu utama: ")

        if pilih == "1":
            while True:
                print("\n--- SUB-MENU RENTAL ---")
                print("1. Tambah Mobil\n2. Cari Mobil\n3. Hapus Mobil\n4. Daftar Mobil\n5. Proses Rental\n0. Kembali")
                r = input("Pilih: ")
                if r=="1": tambah_mobil()
                elif r=="2": cari_mobil()
                elif r=="3": hapus_mobil()
                elif r=="4": daftar_mobil()
                elif r=="5": rental_mobil()
                elif r=="0": break

        elif pilih == "2":
            while True:
                print("\n--- SUB-MENU RESTORAN ---")
                print("1. Tambah Menu\n2. Daftar Menu\n3. Kasir Resto\n0. Kembali")
                m = input("Pilih: ")
                if m=="1": tambah_makanan()
                elif m=="2": daftar_makanan()
                elif m=="3": proses_pembayaran_makanan()
                elif m=="0": break

        elif pilih == "3":
            while True:
                print("\n--- SUB-MENU PERBAIKAN ---")
                print("1. Daftar Servis Baru\n2. Lihat Antrian\n3. Tugaskan Mekanik\n4. Update Status\n0. Kembali")
                s = input("Pilih: ")
                if s=="1": catat_mobil_servis()
                elif s=="2": daftar_mobil_servis()
                elif s=="3": pilih_mekanik_servis()
                elif s=="4": update_status_servis()
                elif s=="0": break

        elif pilih == "4":
            while True:
                print("\n--- SUB-MENU SPAREPART ---")
                print("1. Daftar & Penjualan\n2. Tambah Stok\n3. Tambah Sparepart Baru\n4. Hapus Sparepart\n0. Kembali")
                sp = input("Pilih: ")
                if sp=="1": proses_pembayaran_sparepart()
                elif sp=="2": tambah_stok_sparepart()
                elif sp=="3": tambah_sparepart_baru()
                elif sp=="4": hapus_sparepart()
                elif sp=="0": break

        elif pilih == "5":
            print("\n=== DAFTAR KARYAWAN ===")
            for k in karyawan_list: print("-", k)

        elif pilih == "6":
            print("\n--- INVENTARIS ALAT BENGKEL ---")
            for i, b in enumerate(inventaris_list, 1):
                print(f"{i}. {b['barang']} (Stok: {b['jumlah']})")

        elif pilih == "7":
            print("Sistem dimatikan. Terima kasih!")
            break
        else:
            print("Pilihan tidak tersedia.")

if __name__ == "__main__":
    menu()