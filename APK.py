"""
Aplikasi       : ? (?) - Versi 4.3.0 (target max fix, MAJOR.MINOR.PATCH)
Fitur          : Mengelola inventaris, karyawan, penjualan, service mobil, dan pemesanan makanan, semuanya terintegrasi dengan laporan ringkas di dashboard.
Penulis        : 2840 & 2835
Versi (update) : 4.2.14
"""
import sys
import time
import ast
import json
import random
import os

from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Tuple, Optional


''' DATA LAYER '''
# Data (10 item per module)
def seed_data():
    # Tambah gudang
    add_warehouse("Pusat", "Jl. Malang No.1", silent=True)
    add_warehouse("Cabang 1", "Jl. Ahmad Yani No.25", silent=True)
    add_warehouse("Cabang 2", "Jl. Cempaka No.15", silent=True)

    # Ambil object gudang pusat
    pusat = None
    for wh in store.warehouses.values():
        if wh.name.lower() == "pusat":
            pusat = wh
            break

    # Inventaris dengan stok awal
    items = [
        ("Oli Mesin", 75000, "1", 10),
        ("Filter Udara", 120000, "1", 5),
        ("Ban Lokomotif", 1500000, "1", 2),
        ("Kampas Rem", 250000, "1", 8),
        ("Busi", 35000, "1", 20),
        ("Cat Body Merah", 200000, "2", 3),
        ("Cat Body Biru", 200000, "2", 4),
        ("Toolkit Mekanik", 500000, "2", 6),
        ("Dongkrak Hidrolik", 1250000, "2", 1),
        ("Solar", 10000, "3", 100),
    ]
    for name, harga, kategori, stok in items:
        item = add_inventory(name, harga, kategori, stok_awal=stok, silent=True)
        if pusat:
            pusat.stock[item.item_id] = {"qty": stok, "status": "Pending"}

    # Karyawan + akun login (cek dulu apakah sudah ada)
    for name, role, address, phone in [
        ("Putra", "Dapur", "Jl. Merdeka No.1", "08123456789"),
        ("Andi", "Kasir", "Jl. Sudirman No.3", "081234598998"),
        ("Budi", "Service", "Jl. Ahmad Yani No.5", "08234567890"),
        ("Citra", "Admin", "Jl. Pangeran Antasari No.7", "08345678901"),
        ("Putri", "Rental", "Jl. Cempaka No.10", "08456789012"),
        ("Eko", "Gudang", "Jl. Veteran No.12", "08567890123"),
        ("Fajar", "Kasir", "Jl. Gatot Subroto No.15", "08678901234"),
        ("Gina", "Service", "Jl. Banjarbaru Raya No.20", "08789012345"),
        ("Hadi", "Dapur", "Jl. Panglima Batur No.25", "08890123456"),
        ("Indra", "Rental", "Jl. Hasan Basri No.30", "08901234567"),
    ]:
        emp_id = add_employee(name, role, address, phone, silent=True)
        username = name.lower()
        if username not in users:   # hanya tambah kalau belum ada
            users[username] = {
                "password": emp_id,        # sementara password = emp_id
                "employee_id": emp_id,
                "role": role.lower(),
                "status": "Aktif",
                "last_login": "-"          # default, akan diupdate saat login
            }
    save_users()

    # Servis
    add_lokomotif("Unit Mesin A", "Perbaikan Mesin", 350000, silent=True)
    add_lokomotif("Unit Mesin B", "Overhaul", 450000, silent=True)
    add_lokomotif("Unit Cat 1", "Pengecatan", 300000, silent=True)
    add_lokomotif("Unit Mesin C", "Perbaikan Mesin", 375000, silent=True)
    add_lokomotif("Unit Mesin D", "Overhaul", 600000, silent=True)
    add_lokomotif("Unit Cat 2", "Pengecatan", 350000, silent=True)
    add_lokomotif("Unit Mesin E", "Perbaikan Mesin", 400000, silent=True)
    add_lokomotif("Unit Mesin F", "Overhaul", 500000, silent=True)
    add_lokomotif("Unit Cat 3", "Pengecatan", 325000, silent=True)
    add_lokomotif("Unit Mesin G", "Perbaikan Mesin", 420000, silent=True)

    # Menu (harga, stok)
    add_menu("Nasi Goreng", 25000, 20, silent=True)
    add_menu("Mie Ayam", 20000, 25, silent=True)
    add_menu("Soto Banjar", 30000, 15, silent=True)
    add_menu("Ayam Bakar", 35000, 20, silent=True)
    add_menu("Ikan Bakar", 40000, 15, silent=True)
    add_menu("Es Teh Manis", 5000, 50, silent=True)
    add_menu("Es Jeruk", 8000, 40, silent=True)
    add_menu("Kopi Hitam", 10000, 30, silent=True)
    add_menu("Teh Tarik", 12000, 25, silent=True)
    add_menu("Jus Alpukat", 15000, 20, silent=True)

''' HELPERS '''
# Konstanta & Kategori
KATEGORI_LIST = {"1": "Suku Cadang", "2": "Peralatan", "3": "Bahan Bakar"}

def pilih_kategori(prompt="Pilih kategori (1-3): ", return_name=False):
    while True:
        print("\n\033[34m>>> PILIH KATEGORI\033[0m")
        for key, value in KATEGORI_LIST.items():
            print(f"{key}. {value}")
        pilih = input(prompt).strip()
        if pilih in KATEGORI_LIST:
            return KATEGORI_LIST[pilih] if return_name else pilih
        print("\n\033[31mPilihan kategori tidak valid\033[0m")

# Format & Validasi Input
def format_rupiah(n: int) -> str:
    s = f" {n:,}".replace(",", ".")
    return f"Rp {s}"

def input_int(prompt: str, min_val: int = None, max_val: int = None) -> int:
    while True:
        try:
            v = int(input(prompt).strip())
            if min_val is not None and v < min_val:
                print(f"Masukkan angka minimal \033[33m{min_val}\033[0m")
                continue
            if max_val is not None and v > max_val:
                print(f"Masukkan angka maksimal \033[33m{max_val}\033[0m")
                continue
            return v
        except ValueError:
            print("\n\033[33mMasukkan angka yang valid\033[0m")

def safe_input(prompt: str) -> str:
    try:
        return input(prompt).strip()
    except (EOFError, KeyboardInterrupt):
        print("\n\033[31m Input dibatalkan \033[0m")
        return ""

# UI & Tampilan
def head(prompt):
    print(f"\n\033[44m {prompt} \033[0m")
    print_line()

def print_line():
    print("\033[34m" + "="*40 + "\033[0m")

def input_menu(title: str, options: dict):
    while True:
        print(f"\n\033[34m\033[4m ===> {title} ֍ \033[0m\033[0m")
        for key, desc in options.items():
            print(f"{key}. {desc}")
        val = input("Pilih: ").strip()
        if val in options:
            return val
        print(f"\n\033[31m Pilihan tidak valid. Pilih {', '.join(options.keys())} \033[0m")

def pause(duration: float = 0.02, total: int = 20):
    print('\033[33m')
    for i in range(total + 1):
        percent = int((i / total) * 100)
        bar = "█" * i + " " * (total - i)
        text = "Tunggu"
        bar_with_text = text + bar[len(text):]
        sys.stdout.write(f"\r|{bar_with_text}| {percent}%")
        sys.stdout.flush()
        time.sleep(duration)
    print("\033[32m - Selesai!\033[0m")

def kategori_color(kategori):
    if kategori == "Suku Cadang":
        return f"\033[36m{kategori}\033[0m"
    elif kategori == "Peralatan":
        return f"\033[35m{kategori}\033[0m"
    elif kategori == "Bahan Bakar":
        return f"\033[34m{kategori}\033[0m"
    else:
        return kategori

# Inventaris & Gudang
def find_item(query: str, warehouse_id: str = None):
    keywords = [q.strip().lower() for q in query.split(",")]
    results = []

    for kw in keywords:
        # cari berdasarkan ID
        if kw.upper() in store.inventory:
            item = store.inventory[kw.upper()]
            # kalau ada warehouse_id, cek stok gudang
            if warehouse_id:
                wh = store.warehouses.get(warehouse_id)
                if wh and item.item_id in wh.stock:
                    results.append(item)
            else:
                results.append(item)
            continue

        # cari berdasarkan nama
        for item in store.inventory.values():
            if item.name.lower() == kw:
                if warehouse_id:
                    wh = store.warehouses.get(warehouse_id)
                    if wh and item.item_id in wh.stock:
                        results.append(item)
                else:
                    results.append(item)
                break

    if len(results) == 1:
        return results[0]
    return results if results else None

def find_warehouse(query: str):
    q = query.strip().lower()
    for wh in store.warehouses.values():
        if wh.warehouse_id.lower() == q or wh.name.lower() == q:
            return wh
    return None

def inventory_per_gudang():
    print("\n\033[34m>> INVENTARIS PER GUDANG:\033[0m")
    for wh in store.warehouses.values():
        print(f"\nGudang {wh.warehouse_id} | {wh.name} | Alamat: {wh.address}")
        print("-" * 80)
        found = False
        for item in sorted(store.inventory.values(), key=lambda x: x.name):
            qty = item.stock_by_warehouse.get(wh.warehouse_id, 0)
            if qty > 0:
                found = True
                # Warna status
                if item.status in ["Rusak", "Hilang"]:
                    status_ui = f"\033[31m{item.status}\033[0m"
                elif item.status == "Pending":
                    status_ui = f"\033[33m{item.status}\033[0m"
                elif item.status == "Siap Jual":
                    status_ui = f"\033[32m{item.status}\033[0m"
                else:
                    status_ui = item.status

                kategori_ui = KATEGORI_LIST.get(str(item.category), item.category)

                print(f"{item.item_id:<8} | {item.name:<20} | Stok: {qty:<5} | Harga Beli: {format_rupiah(item.price):<12} | Kategori: {kategori_ui:<12} | Kondisi: {status_ui}")
        if not found:
            print("\033[33mTidak ada stok barang di gudang ini\033[0m")

def print_inventory_by_category():
    print("\n\033[34m>>> INVENTARIS PER KATEGORI\033[0m")
    for code, cat in KATEGORI_LIST.items():
        print(f"\nKategori {code} - {cat}")
        print(f"{'ID':<8} | {'Nama':<20} | {'Unit':<10} | {'Harga':<15} | {'Kondisi':<12}")
        print("-"*85)
        found = False

        for it in store.inventory.values():
            if str(it.category) == code:
                found = True
                # Warna status
                if it.status in ["Rusak", "Hilang"]:
                    status_ui = f"\033[31m{it.status}\033[0m"
                elif it.status == "Pending":
                    status_ui = f"\033[33m{it.status}\033[0m"
                elif it.status == "Siap Jual":
                    status_ui = f"\033[32m{it.status}\033[0m"
                else:
                    status_ui = it.status
                print(f"{it.item_id:<8} | {it.name:<20} | {it.confirmed_stock:<10} | "
                    f"{format_rupiah(it.price):<15} | {status_ui:<12}")
        if not found:
            print("\033[33mTidak ada barang di kategori ini\033[0m")

def print_inventory():
    print("\n\033[34m>> INVENTARIS BARANG:\033[0m")
    if not store.inventory:
        print("\033[31m- KOSONG -\033[0m")
        return
    # Header tabel
    print(f"{'ID':<8} | {'Nama':<20} | {'Unit':<5} | {'Harga Beli':<15} | {'Kategori':<15} | {'Kondisi':<12} | {'Gudang':<20}")
    print("-"*110)

    for it in store.inventory.values():
        # Warna status
        if it.status in ["Rusak", "Hilang"]:
            status_ui = f"\033[31m{it.status}\033[0m"
        elif it.status == "Pending":
            status_ui = f"\033[33m{it.status}\033[0m"
        elif it.status == "Siap Jual":
            status_ui = f"\033[32m{it.status}\033[0m"
        else:
            status_ui = it.status
        # Ambil kategori dari KATEGORI_LIST lalu warnai
        kategori_text = KATEGORI_LIST.get(str(it.category), it.category)
        kategori_ui = kategori_color(kategori_text)

        # Cari gudang tempat item ini tercatat
        gudang_list = []
        for w in store.warehouses.values():
            if it.item_id in w.stock:
                gudang_list.append(w.name)
        gudang_ui = ", ".join(gudang_list) if gudang_list else "-"

        # Isi baris
        print(f"{it.item_id:<8} | {it.name:<20} | {it.confirmed_stock:<5} | {format_rupiah(it.price):<15} | {kategori_ui:<24} | {status_ui:<21} | {gudang_ui:<20}")

def adjust_stock(item_id: str, warehouse_id: str, delta: int, silent=False):
    if item_id not in store.inventory:
        if not silent: print("\n\033[31mItem tidak ditemukan\033[0m")
        return
    if warehouse_id not in store.warehouses:
        if not silent: print("\n\033[31mGudang tidak ditemukan\033[0m")
        return
    item = store.inventory[item_id]
    current = item.stock_by_warehouse.get(warehouse_id, 0)
    new_stock = current + delta
    if new_stock < 0:
        if not silent:
            print(f"\n\033[31mStok {item.name} di {store.warehouses[warehouse_id].name} tidak cukup (tersedia {current})\033[0m")
        return
    item.stock_by_warehouse[warehouse_id] = new_stock
    if not silent:
        wh_name = store.warehouses[warehouse_id].name
        print(f"\n\033[32mStok {item.name} di {wh_name} sekarang {new_stock}\033[0m")

def transfer_stock(item_id: str, from_wh: str, to_wh: str, qty: int):
    if item_id not in store.inventory:
        print("\n\033[31mItem tidak ditemukan\033[0m")
        return
    if from_wh not in store.warehouses or to_wh not in store.warehouses:
        print("\n\033[31mGudang asal/tujuan tidak ditemukan\033[0m")
        return
    if from_wh == to_wh:
        print("\n\033[33mGudang asal dan tujuan tidak boleh sama\033[0m")
        return
    item = store.inventory[item_id]
    current_stock = item.stock_by_warehouse.get(from_wh, 0)
    if current_stock < qty:
        print(f"\n\033[31mStok di gudang {store.warehouses[from_wh].name} tidak cukup (tersedia {current_stock})\033[0m")
        return
    item.stock_by_warehouse[from_wh] = current_stock - qty
    item.stock_by_warehouse[to_wh] = item.stock_by_warehouse.get(to_wh, 0) + qty
    log_warehouse("Mutasi Stok", item_id, from_wh=from_wh, to_wh=to_wh, qty=qty)
    print(f"\033[32mTransfer {qty} unit {item.name} dari {store.warehouses[from_wh].name} ke {store.warehouses[to_wh].name}\033[0m")

def konfirmasi_stok_gudang():
    # Tampilkan daftar gudang dulu
    print_warehouses()

    # User pilih gudang (ID atau Nama)
    wh_input = input("\nPilih ID/Nama Gudang yang mau dikonfirmasi stoknya: ").strip()
    warehouse = find_warehouse(wh_input)
    if not warehouse:
        print("\n\033[31mGudang tidak ditemukan\033[0m")
        return
    wh_id = warehouse.warehouse_id

    # User input barang (bisa banyak)
    print_inventory()
    item_query = input("\nMasukkan ID/Nama barang (gunakan koma): ").strip()
    items = find_item(item_query)
    if not items:
        print("\n\033[31mBarang tidak ditemukan\033[0m")
        return

    # Normalisasi hasil jadi list
    if isinstance(items, InventoryItem):
        items = [items]

    # Loop tiap barang untuk konfirmasi stok
    for item in items:
        qty_real = input_int(f"Jumlah aktual hasil cek untuk {item.name}: ", min_val=0)

        # Ambil data lama
        old_data = store.warehouses[wh_id].stock.get(item.item_id, {})
        old_qty = old_data.get("qty", 0)
        old_status = old_data.get("status", "Pending")

        # Update stok gudang
        store.warehouses[wh_id].stock[item.item_id] = {
            "qty": qty_real,
            "status": old_status}

        # Sinkronisasi ke inventaris
        store.inventory[item.item_id].confirmed_stock = qty_real

        # Catat log
        log_warehouse(
            "Konfirmasi Stok Gudang",
            item.item_id,
            extra={"warehouse": wh_id, "old_qty": old_qty, "new_qty": qty_real})

        print(f"\n\033[32mStok {item.name} di {wh_id} dikonfirmasi: {qty_real} unit\033[0m")

def print_stock_per_warehouse(wh_id=None):
    print("\n\033[34m>> STOK PER GUDANG:\033[0m")
    gudangs = [store.warehouses[wh_id]] if wh_id and wh_id in store.warehouses else store.warehouses.values()

    for w in gudangs:
        print(f"\nGudang {w.warehouse_id} - {w.name} (Alamat: {w.address})")
        if not w.stock:
            print("\033[31m- KOSONG -\033[0m")
        else:
            print(f"{'ID':<8} | {'Nama':<20} | {'Jumlah':<6} | {'Harga Beli':<12} | {'Kategori':<15} | {'Kondisi':<12}")
            print("-"*85)
            for item_id, data in w.stock.items():
                item = store.inventory.get(item_id)
                if not item:
                    nama, harga, kategori = "Unknown", "-", "-"
                else:
                    nama, harga, kategori = item.name, f"Rp {item.price:,}", KATEGORI_LIST.get(str(item.category), item.category)

                qty = data.get("qty", 0)
                status = data.get("status") or getattr(item, "status", "Pending")
                # Warna status
                if status.lower() == "baik":
                    status_colored = f"\033[32m{status}\033[0m"
                elif status.lower() == "pending":
                    status_colored = f"\033[33m{status}\033[0m"
                else:
                    status_colored = f"\033[31m{status}\033[0m"
                print(f"{item_id:<8} | {nama:<20} | {qty:<6} | {harga:<12} | {kategori:<15} | {status_colored:<12}")

def print_warehouses():
    print("\n\033[34m>> DAFTAR GUDANG:\033[0m")
    if not store.warehouses:
        print("\n\033[31m- KOSONG -\033[0m")
        return

    # Header tabel
    print(f"{'ID':<8} | {'Nama Gudang':<20} | {'Alamat':<30}")
    print("-"*65)

    # Isi tabel
    default_wh = getattr(store, "default_warehouse", "WH01")
    for w in store.warehouses.values():
        mark = " *DEFAULT*" if w.warehouse_id == default_wh else ""
        print(f"{w.warehouse_id:<8} | {w.name:<20} | {w.address:<30}{mark}")

# Akses & Role
def check_access(required_role):
    if current_role != required_role:
        print(f"\033[31mAkses ditolak: hanya {required_role} yang bisa menjalankan menu ini\033[0m")
        return False
    return True

# Logging / Pencatatan
def log_employee_action(user, role, action, extra=None, filename="employee_log.txt"):
    record = {
        "date": datetime.now().strftime("%Y-%m-%d (%H:%M:%S)"),
        "user": user,
        "role": role,
        "action": action}
    if extra:
        record.update(extra)
    with open(filename, "a") as f:
        f.write(json.dumps(record) + "\n")

def log_inventory(action, item, extra=None, filename="inventory_log.txt"):
    record = {
        "date": datetime.now().strftime("%Y-%m-%d (%H:%M)"),
        "user": current_user,
        "item_id": item.item_id,
        "name": item.name,
        "action": action,
        "kategori": str(item.category),   # simpan kode kategori
        "jumlah": item.confirmed_stock,
        "harga": item.price}
    if extra:
        record.update(extra)
    with open(filename, "a") as f:
        f.write(json.dumps(record) + "\n")

def log_warehouse(action, item_id, from_wh=None, to_wh=None, qty=None, extra=None, filename="warehouse_log.txt"):
    record = {
        "date": datetime.now().strftime("%Y-%m-%d (%H:%M:%S)"),
        "user": current_user,
        "action": action,
        "item_id": item_id,
        "from": from_wh,
        "to": to_wh,
        "qty": qty}
    if extra:
        record.update(extra)
    with open(filename, "a") as f:
        f.write(json.dumps(record) + "\n")

def log_service(action, record, filename="services.txt"):
    data = {
        "date": datetime.now().strftime("%Y-%m-%d (%H:%M:%S)"),
        "user": current_user,
        "action": action,
        **record.__dict__}
    with open(filename, "a") as f:
        f.write(json.dumps(data) + "\n")

def log_sale(sale_type, ref_id, amount, extra=None, filename="sales.txt"):
    record = {
        "date": datetime.now().strftime("%Y-%m-%d (%H:%M:%S)"),
        "user": current_user,
        "role": current_role,
        "type": sale_type,
        "ref": ref_id,
        "amount": amount}
    if extra:
        record.update(extra)
    with open(filename, "a") as f:
        f.write(json.dumps(record) + "\n")

# Admin & Review
def review_requests():
    print("\n\033[34m>>> REVIEW PERMINTAAN KONFIRMASI\033[0m")
    try:
        with open("inventory_requests.txt", "r") as f:
            lines = f.readlines()
        if not lines:
            print("\n\033[33mTidak ada permintaan konfirmasi\033[0m")
            return

        # Header tabel
        print(f"{'No':<4} | {'Tanggal':<12} | {'User':<12} | {'Barang':<20} | {'ID':<8}")
        print("-"*65)

        # Isi tabel
        for idx, line in enumerate(lines, 1):
            req = json.loads(line)
            print(f"{idx:<4} | {req['date']:<12} | {req['user']:<12} | {req['name']:<20} | {req['item_id']:<8}")

        # Input pilihan
        idx_choice = input_int("Pilih nomor untuk approve (0=keluar): ", min_val=0)
        if idx_choice == 0:
            return
        if idx_choice > len(lines):
            print(f"\n\033[31mNomor {idx_choice} tidak valid\033[0m")
            return

        req = json.loads(lines[idx_choice-1])
        item = store.inventory.get(req['item_id'])

        if item and item.confirmed_stock > 0 and item.price > 0:
            item.status = "Siap Jual"
            print(f"\n\033[32mBarang {item.item_id} ({item.name}) dikonfirmasi SIAP JUAL oleh Admin\033[0m")

            # hapus request yang sudah diproses
            with open("inventory_requests.txt", "w") as f:
                for i, line in enumerate(lines, 1):
                    if i != idx_choice:
                        f.write(line)
        else:
            print(f"\n\033[31mBarang {req['name']} tidak valid (stok/harga belum ada)\033[0m")
    except FileNotFoundError:
        print("\n\033[33mBelum ada file permintaan\033[0m")

# Riwayat
def riwayat_barang():
    print("\n\033[34m>>> LIHAT RIWAYAT BARANG\033[0m")
    ops = {"1": "Semua Riwayat", "2": "Filter berdasarkan Tanggal", "3": "Filter berdasarkan Kategori"}
    choice = input_menu("Opsi Riwayat", ops)

    if choice == "1":
        tampilkan_riwayat()
    elif choice == "2":
        tanggal = input("Masukkan tanggal (Thn-Bln-Tgl): ").strip()
        tampilkan_riwayat(filter_date=tanggal)
    elif choice == "3":
        category_code = pilih_kategori() 
        tampilkan_riwayat(filter_category=category_code)

def tampilkan_riwayat(filter_date=None, filter_category=None):
    print("\n\033[34m>> RIWAYAT BARANG MASUK\033[0m")

    try:
        with open("inventory_log.txt", "r") as f:
            lines = f.readlines()
    except FileNotFoundError:
        print("\033[33mBelum ada riwayat barang masuk\033[0m")
        return

    if not lines:
        print("\033[33mBelum ada riwayat barang masuk\033[0m")
        return

    # Header tabel
    print(f"{'Tanggal':<20} | {'Nama':<20} | {'Jumlah':<6} | {'Harga':<18} | {'Kategori':<15}")
    print("-"*85)

    seen = set()
    for line in lines:
        if line in seen: 
            continue
        seen.add(line)
        rec = json.loads(line)

        if filter_date and rec["date"] != filter_date:
            continue
        if filter_category and rec["kategori"] != str(filter_category):
            continue

        kategori_text = KATEGORI_LIST.get(rec["kategori"], rec["kategori"])
        kategori_ui = kategori_color(kategori_text)

        print(f"{rec['date']:<20} | {rec['name']:<20} | {rec.get('jumlah',''):<6} | "
            f"{format_rupiah(int(rec.get('harga',0))):<18} | {kategori_ui:<15}")

def show_inventory_log(filename="inventory_log.txt"):
    try:
        with open(filename, "r") as f:
            lines = f.readlines()
    except FileNotFoundError:
        print("\n\033[33mBelum ada riwayat\033[0m")
        return

    seen = set()
    for line in lines:
        if line not in seen:
            seen.add(line)
            record = json.loads(line)
            kategori_text = KATEGORI_LIST.get(record.get("kategori",""), record.get("kategori",""))
            print(f"{record['date']} | {record['name']} | Jumlah: {record.get('jumlah','')} | "
                f"Harga: {record.get('harga','')} | Kategori: {kategori_text}")

def tampilkan_riwayat_semua():
    print("\n\033[34m>> Riwayat Penjualan\033[0m")
    if not store.sales:
        print("\n\033[33m- KOSONG -\033[0m")
        return
    # Header tabel
    print(f"{'No':<4} | {'ID':<10} | {'Tanggal':<16} | {'Kasir':<12} | {'Detail':<30} | {'Total':<15} | {'Bayar':<10} | {'Gudang':<8}")
    print("-"*120)
    # Isi tabel
    for idx, sale in enumerate(store.sales, 1):
        detail = "; ".join(f"{store.inventory[i].name if i in store.inventory else i} x{q}" for i, q in sale.items)
        print(f"{idx:<4} | {sale.sale_id:<10} | {sale.date:<16} | {sale.cashier:<12} | {detail:<30} | "
            f"{format_rupiah(sale.total):<15} | {sale.payment_method:<10} | {sale.warehouse_id:<8}")

def tampilkan_riwayat_sendiri():
    print("\n\033[34m>> Riwayat Penjualan (Anda)\033[0m")
    found = False
    # Header tabel
    print(f"{'No':<4} | {'ID':<10} | {'Tanggal':<16} | {'Detail':<30} | {'Total':<15} | {'Bayar':<10} | {'Gudang':<8}")
    print("-"*100)

    for idx, sale in enumerate(store.sales, 1):
        if sale.cashier == current_user:
            found = True
            detail = "; ".join(f"{store.inventory[i].name if i in store.inventory else i} x{q}" for i, q in sale.items)
            print(f"{idx:<4} | {sale.sale_id:<10} | {sale.date:<16} | {detail:<30} | "
                f"{format_rupiah(sale.total):<15} | {sale.payment_method:<10} | {sale.warehouse_id:<8}")

    if not found:
        print("\n\033[33mBelum ada penjualan oleh Anda\033[0m")

def transaksi_penjualan():
    cart = []
    while True:
        print('\033[33m\033[3m*enter jika selesai\033[0m')
        query = input("\nID/Nama barang: ").strip()
        if query == "":
            break

        item = find_item(query)

        # hasil tunggal → langsung objek
        if isinstance(item, InventoryItem):
            if item.status != "Siap Jual" or item.confirmed_stock <= 0:
                print(f"\nBarang {item.name} belum dikonfirmasi untuk dijual")
                continue
            qty = input_int("Jumlah: ", min_val=1)
            if qty > item.confirmed_stock:
                print(f"\nStok {item.name} aman kurang")
                continue
            cart.append((item.item_id, qty))

        # hasil list → loop semua
        elif isinstance(item, list):
            for obj in item:
                if obj.status != "Siap Jual" or obj.confirmed_stock <= 0:
                    print(f"\nBarang {obj.name} belum dikonfirmasi untuk dijual")
                    continue
                qty = input_int(f"Jumlah {obj.name}: ", min_val=1)
                if qty > obj.confirmed_stock:
                    print(f"\nStok {obj.name} aman kurang")
                    continue
                cart.append((obj.item_id, qty))

        else:
            print(f"\nBarang {query} tidak ada")
            continue

    if not cart:
        print("\n\033[31mKeranjang kosong. Ulangi input barang\033[0m")
        return

    total = sum(store.inventory[i].price * q for i, q in cart)

    # Pilih gudang asal
    wh_id = input("\nGudang asal (ID): ").strip().upper()
    if wh_id not in store.warehouses:
        print("\n\033[31mGudang tidak ditemukan\033[0m")
        return

    # Kurangi stok gudang + sinkron ke inventaris
    for i, q in cart:
        if store.warehouses[wh_id].stock.get(i, {}).get("qty", 0) < q:
            print(f"\n\033[31mStok {i} di gudang {wh_id} tidak cukup\033[0m")
            return
        store.warehouses[wh_id].stock[i]["qty"] -= q
        store.inventory[i].confirmed_stock -= q
        log_warehouse("OUT", i, q, current_user, warehouse_id=wh_id)

    # Input metode pembayaran
    payment_method = input("Metode pembayaran (Tunai/Transfer): ").strip() or "Tunai"

    # Buat objek Sale
    sale_id = store.gen_id("SALE")
    sale = Sale(
        sale_id=sale_id,
        items=cart,
        total=total,
        date=datetime.now().strftime("%Y-%m-%d (%H:%M)"),
        cashier=current_user
    )
    sale.payment_method = payment_method
    sale.warehouse_id = wh_id
    store.sales.append(sale)

    # Simpan ke file sales.txt
    with open("sales.txt", "a") as f:
        f.write(json.dumps(asdict(sale)) + "\n")

    # Catat log
    log_sale("barang", sale.sale_id, total, {"items": cart, "payment": payment_method, "warehouse": wh_id})
    log_employee_action(current_user, current_role, "Transaksi Penjualan",
        {"items": cart, "total": total, "payment": payment_method, "warehouse": wh_id, "reason": "Customer membeli barang"})

    # Cetak nota barang
    print("\n\033[34m>> NOTA TRANSAKSI PENJUALAN\033[0m")
    print("="*80)
    print(f"{'ID Barang':<12} | {'Nama Barang':<25} | {'Qty':<5} | {'Harga':<15} | {'Subtotal':<15}")
    print("-"*80)
    for i, q in cart:
        item = store.inventory[i]
        subtotal = item.price * q
        print(f"{i:<12} | {item.name:<25} | {q:<5} | {format_rupiah(item.price):<15} | {format_rupiah(subtotal):<15}")
    print("-"*80)
    print(f"{'TOTAL':<12} {'':<25} {'':<5} {'':<15} {format_rupiah(total):<15}")
    print("="*80)
    print(f"Metode Bayar: {payment_method} | Gudang: {wh_id}")

def print_sales_history_barang(sales_list):
    print("\n\033[34m>> RIWAYAT PENJUALAN BARANG:\033[0m")
    if not sales_list:
        print("\033[31m- KOSONG -\033[0m")
        return

    # Header tabel
    print(f"{'No':<4} | {'ID':<10} | {'Tanggal':<16} | {'Kasir':<12} | {'Detail':<30} | {'Total':<15} | {'Bayar':<10} | {'Gudang':<8}")
    print("-"*120)

    # Isi tabel
    for idx, sale in enumerate(sales_list, 1):
        detail = "; ".join(
            f"{store.inventory[i].name if i in store.inventory else i} x{q}"
            for i, q in sale.items
        )
        bayar = sale.payment_method if sale.payment_method else "-"
        gudang = sale.warehouse_id if sale.warehouse_id else "-"
        print(f"{idx:<4} | {sale.sale_id:<10} | {sale.date:<16} | {sale.cashier:<12} | {detail:<30} | {format_rupiah(sale.total):<15} | {bayar:<10} | {gudang:<8}")

def print_food_orders_history(food_orders):
    print("\n\033[34m>> RIWAYAT PESANAN MAKANAN:\033[0m")
    if not food_orders:
        print("\033[31m- KOSONG -\033[0m")
        return
    # Header tabel
    print(f"{'No':<4} | {'Tanggal':<16} | {'Waiter':<12} | {'Detail':<40} | {'Total':<15}")
    print("-"*100)
    # Isi tabel
    for idx, o in enumerate(food_orders, 1):
        detail = "; ".join(f"{store.menu[mid].name} x{qty}" for mid, qty in o.items)
        print(f"{idx:<4} | {o.date:<16} | {o.waiter:<12} | {detail:<40} | {format_rupiah(o.total):<15}")

def laporan_detail():
    head("LAPORAN DETAIL")
    # Barang Terlaris
    counter = {}
    for s in store.sales.values():   # ambil objek Sale dari dict
        for i, q in s.items:         # items = list of tuple (id, qty)
            it = store.inventory.get(i)
            key = it.name if it else f"[UNKNOWN:{i}]"
            counter[key] = counter.get(key, 0) + q
    top_items(counter, "Barang Terlaris", "unit")

    # Lokomotif Terlaris
    lokomotif_count = {}
    for r in store.services:
        lok = store.lokomotif.get(r.lokomotif_id)
        if lok:
            lokomotif_count[lok.name] = lokomotif_count.get(lok.name, 0) + 1
    top_items(lokomotif_count, "Lokomotif Terlaris", "kali diservis")

    # Menu Favorit
    food_count = {}
    for o in store.food_orders:
        for i, q in o.items:
            m = store.menu.get(i)
            key = m.name if m else f"[UNKNOWN:{i}]"
            food_count[key] = food_count.get(key, 0) + q
    top_items(food_count, "Menu Favorit", "porsi")

    # Laporan Karyawan & Akun
    print("\n\033[34m>> Laporan Karyawan & Akun\033[0m")
    print(f"{'Emp.ID':<8} | {'Nama':<20} | {'Jabatan':<10} | {'Username':<15} | {'Role Akun':<10} | {'Status':<10}")
    print("-"*85)
    for emp_id, emp in store.employees.items():
        username = "-"
        role_akun = "-"
        for uname, udata in users.items():
            if udata["employee_id"] == emp_id:
                username = uname
                role_akun = udata.get("role", "-")
                break
        print(f"{emp.id:<8} | {emp.name:<20} | {emp.role:<10} | {username:<15} | {role_akun:<10} | {emp.status:<10}")

# Karyawan
def print_employees():
    print("\n\033[34m>> KARYAWAN:\033[0m")
    if not store.employees:
        print("\n\033[31m- KOSONG -\033[0m")
        return

    # Header tabel
    print(f"{'ID (EMP)':<8} | {'Nama':<12} | {'Jabatan':<12} | {'Alamat':<30} | {'Telepon':<15}")
    print("-"*85)

    # Isi tabel
    for emp in store.employees.values():
        print(f"{emp.id:<8} | {emp.name:<12} | {emp.role:<12} | {emp.address:<30} | {emp.phone:<15}")

EMPLOYEE_FILE = "employees.json"  # lokasi file

def save_employees():
    data = {}
    for emp_id, emp in store.employees.items():
        data[emp_id] = {
            "name": emp.name,
            "role": emp.role,
            "status": getattr(emp, "status", "Aktif"),
            "address": getattr(emp, "address", "-"),
            "phone": getattr(emp, "phone", "-")
        }
    with open(EMPLOYEE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    print("\033[32mData karyawan berhasil disimpan\033[0m")

def load_employees():
    if not os.path.exists(EMPLOYEE_FILE):
        return
    with open(EMPLOYEE_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
        for emp_id, info in data.items():
            emp = Employee(emp_id, info["name"], info["role"])
            # isi field tambahan jika ada
            emp.status = info.get("status", "Aktif")
            emp.address = info.get("address", "-")
            emp.phone = info.get("phone", "-")
            store.employees[emp_id] = emp
    print("\033[32mData karyawan berhasil dimuat\033[0m")

# Service / Lokomotif
def print_lokomotif():
    print("\n\033[34m>> LOKOMOTIF / UNIT SERVICE:\033[0m")
    if not store.lokomotif:
        print("\033[31m- KOSONG -\033[0m")
        return

    # Header tabel
    print(f"{'ID':<8} | {'Nama':<20} | {'Jenis':<15} | {'Tarif/Hari':<15} | {'Status':<12}")
    print("-"*75)

    # Isi tabel
    for lok in store.lokomotif.values():
        status_color = (
            "\033[32mTersedia\033[0m" if lok.status == "Tersedia"
            else "\033[33mDiservis\033[0m" if lok.status == "Diservis"
            else "\033[36mSelesai\033[0m"
        )
        print(f"{lok.id:<8} | {lok.name:<20} | {lok.service_type:<15} | "
            f"{format_rupiah(lok.rate_per_day):<15} | {status_color:<12}")

def rental_service_menu():
    ops = {
        "1": "Manajemen Rental",
        "2": "Manajemen Servis",
        "0": "Kembali"
    }
    choice = input_menu("MENU RENTAL & SERVIS", ops)

    if choice == "1":
        rental_menu()
    elif choice == "2":
        service_menu()
    elif choice == "0":
        return

# Makanan
def print_menu_items(hide_id=False):
    print("\n\033[34m>> MENU MAKANAN:\033[0m")
    if not store.menu:
        print("\n\033[31m- KOSONG -\033[0m")
        return
    if hide_id:
        # Header tanpa ID
        print(f"{'Nama Menu':<20} | {'Harga':<15} | {'Stok':<6}")
        print("-"*48)
        for m in store.menu.values():
            print(f"{m.name:<20} | {format_rupiah(m.price):<15} | {m.stock:<6}")
    else:
        # Header dengan ID
        print(f"{'ID':<8} | {'Nama Menu':<20} | {'Harga':<15} | {'Stok':<6}")
        print("-"*58)
        for m in store.menu.values():
            print(f"{m.id:<8} | {m.name:<20} | {format_rupiah(m.price):<15} | {m.stock:<6}")

def tambah_makanan():
    head("TAMBAH MENU MAKANAN")
    nama = input("\nNama makanan: ").strip()
    harga = input_int("Harga: ", min_val=1000)
    stok = input_int("Stok: ", min_val=1)

    # Generate ID menu baru
    menu_id = store.gen_id("MEN")
    # Buat objek
    store.menu[menu_id] = MenuItem(
        id=menu_id,
        name=nama,
        price=harga,
        stock=stok)
    # catat aktivitas karyawan
    log_employee_action(current_user, current_role, "Tambah Menu Food", {"id": menu_id, "nama": nama, "harga": harga, "stok": stok})
    print(f"\n\033[32mMenu {nama} berhasil ditambahkan dengan ID {menu_id}\033[0m")

def proses_pembayaran_makanan(customer_name: str, table_number: str, cart: List[Tuple[str, int]]):
    # Hitung total
    total = sum(store.menu[mid].price * q for mid, q in cart)

    # Buat objek FoodOrder
    order = FoodOrder(
        items=cart,
        total=total,
        date=datetime.now().strftime("%Y-%m-%d (%H:%M)"),
        waiter=current_user,
        customer_name=customer_name,
        table_number=table_number)
    store.food_orders.append(order)

    # Kurangi stok menu makanan
    for mid, qty in cart:
        store.menu[mid].stock -= qty

    # Simpan ke file food_orders.txt
    with open("food_orders.txt", "a") as f:
        f.write(json.dumps(asdict(order)) + "\n")

    # Integrasi ke penjualan
    sale_id = store.gen_id("SALE")
    sale = Sale(
        sale_id=sale_id,
        items=cart,
        total=total,
        date=order.date,
        cashier=current_user)

    # simpan ke dict, bukan append
    store.sales[sale_id] = sale

    # Simpan ke file sales.txt
    with open("sales.txt", "a") as f:
        f.write(json.dumps(asdict(sale)) + "\n")

    # Catat log
    log_sale("food", order.customer_name, total, {"items": cart, "table": table_number})
    log_employee_action(current_user, current_role, "Kasir Food",
        {"customer": customer_name, "table": table_number, "items": cart, "total": total})

    # Cetak nota makanan
    tampilkan_nota_makanan(order, store)

# Sparepart
def pilih_sparepart():
    parts_used = []
    parts_cost = 0
    while True:
        print_inventory()
        part_id = input("ID sparepart (Enter untuk selesai): ").strip().upper()
        if part_id == "":
            break
        if part_id not in store.inventory:
            print("\n\033[31mID tidak ditemukan\033[0m")
            continue
        qty = input_int("Jumlah: ", min_val=1)
        if qty > store.inventory[part_id].stock:
            print("\n\033[31mStok tidak cukup\033[0m")
            continue
        store.inventory[part_id].stock -= qty
        parts_used.append(f"{store.inventory[part_id].name} x{qty}")
        parts_cost += store.inventory[part_id].price * qty
    return parts_used, parts_cost

# Nota / Bukti Transaksi
def tampilkan_nota_service(record, jasa, parts_cost, total_fee):
    print("\n\033[30m=== NOTA SERVICE PT.AMOT \033[0m")
    print(f"Customer      : {record.customer}")
    print(f"Lokomotif     : {record.lokomotif_id}")
    print(f"Jenis Service : {record.service_type}")
    print(f"Tgl Mulai     : {record.start_date}")
    print(f"Tgl Selesai   : {record.end_date}")
    print(f"Sparepart     : {', '.join(record.parts_used) if record.parts_used else '-'}")
    print(f"Biaya Sparepart: {format_rupiah(parts_cost)}")
    print(f"Biaya Jasa    : {format_rupiah(jasa)}")
    print(f"Total Biaya   : {format_rupiah(total_fee)}")

def tampilkan_nota_makanan(order: "FoodOrder", store: "Store"):
    print("\n\033[30m=== NOTA PEMBELIAN MAKANAN PT. \033[0m\n")
    print(f"Customer      : {order.customer_name}")
    print(f"Meja          : {order.table_number}")
    print(f"Waiter        : {order.waiter}")
    print(f"Tanggal Pesan : {order.date}")

    # Detail pesanan
    detail_lines = []
    for mid, qty in order.items:
        item = store.menu.get(mid)
        if item:
            subtotal = item.price * qty
            detail_lines.append(f"{item.name} x{qty} = {format_rupiah(subtotal)}")
        else:
            detail_lines.append(f"{mid} x{qty}")

    print("Pesanan       :")
    for line in detail_lines:
        print(f"  - {line}")

    print(f"\nTotal Biaya   : {format_rupiah(order.total)}")
    print("\n\033[30m=== Terima kasih telah berbelanja di PT. \033[0m")

def tampilkan_nota_rental(record):
    print("\n\033[30m=== NOTA RENTAL PT.AMOT \033[0m")
    print(f"Customer      : {record.customer}")
    print(f"Lokomotif     : {record.lokomotif_id}")
    print(f"Durasi        : {record.days} hari")
    print(f"Tgl Mulai     : {record.start_date}")
    print(f"Tgl Selesai   : {record.end_date}")
    print(f"Total Biaya   : {format_rupiah(record.total_fee)}")
    print(f"Officer       : {record.officer}")
    # cek status lokomotif
    lok = store.lokomotif.get(record.lokomotif_id)
    if lok and lok.status == "Disewa":
        print("Status        : \033[33mDisewa\033[0m")
    else:
        print("Status        : \033[32mSelesai\033[0m")

# Dashboard & Statistik
def top_items(counter: dict, label: str, unit: str = ""):
    if counter:
        print(f"\n\033[4m>> {label}:\033[0m")
        for nm, qty in sorted(counter.items(), key=lambda x: x[1], reverse=True):
            print(f"- {nm}: {qty} {unit}")
    else:
        print(f"\n\033[33mBelum ada data {label.lower()}\033[0m")

# Stok & Gudang
def adjust_stock(item_id: str, warehouse_id: str, delta: int, silent=False):
    if item_id not in store.inventory:
        if not silent: print("\033[31mItem tidak ditemukan\033[0m")
        return
    if warehouse_id not in store.warehouses:
        if not silent: print("\033[31mGudang tidak ditemukan\033[0m")
        return
    item = store.inventory[item_id]
    current = item.stock_by_warehouse.get(warehouse_id, 0)
    new_stock = current + delta
    if new_stock < 0:
        if not silent:
            print(f"\033[31mStok {item.name} di {store.warehouses[warehouse_id].name} tidak cukup (tersedia {current})\033[0m")
        return
    item.stock_by_warehouse[warehouse_id] = new_stock
    if not silent:
        wh_name = store.warehouses[warehouse_id].name
        print(f"\033[32mStok {item.name} di {wh_name} sekarang {new_stock}\033[0m")

def transfer_stock(item_id: str, from_wh: str, to_wh: str, qty: int):
    if item_id not in store.inventory:
        print("\033[31mItem tidak ditemukan\033[0m")
        return
    if from_wh not in store.warehouses or to_wh not in store.warehouses:
        print("\033[31mGudang asal/tujuan tidak ditemukan\033[0m")
        return
    if from_wh == to_wh:
        print("\033[33mGudang asal dan tujuan tidak boleh sama\033[0m")
        return
    item = store.inventory[item_id]
    current_stock = item.stock_by_warehouse.get(from_wh, 0)
    if current_stock < qty:
        print(f"\033[31mStok di gudang {store.warehouses[from_wh].name} tidak cukup (tersedia {current_stock})\033[0m")
        return
    item.stock_by_warehouse[from_wh] = current_stock - qty
    item.stock_by_warehouse[to_wh] = item.stock_by_warehouse.get(to_wh, 0) + qty
    log_warehouse("Mutasi Stok", item_id, from_wh=from_wh, to_wh=to_wh, qty=qty)
    print(f"\033[32mTransfer {qty} unit {item.name} dari {store.warehouses[from_wh].name} ke {store.warehouses[to_wh].name}\033[0m")

def print_ready_stock():
    ready_list = []
    waiting_list = []

    # Pisahkan barang siap jual dan barang menunggu konfirmasi
    for item in store.inventory.values():
        if item.status == "Siap Jual" and item.confirmed_stock > 0:
            ready_list.append(item)
        else:
            total_gudang = sum(wh.stock.get(item.item_id, {}).get("qty", 0) for wh in store.warehouses.values())
            if total_gudang > 0 and item.status != "Siap Jual":
                waiting_list.append((item.item_id, item.name, total_gudang))

    # Jika ada barang siap jual → tampilkan tabel siap jual
    if ready_list:
        print("\n\033[34m>> Barang Siap Jual:\033[0m")
        print(f"{'ID':<10} | {'Nama Barang':<25} | {'Harga':>15} | {'Stok Aman':>15}")
        print("-"*80)
        for item in ready_list:
            print(f"{item.item_id:<10} | {item.name:<25} | {format_rupiah(item.price):>15} | {item.confirmed_stock:>15}")

    # Kalau tidak ada barang siap jual, tapi ada waiting_list → tampilkan tabel menunggu konfirmasi
    elif waiting_list:
        print("\n\033[33m>> Barang menunggu konfirmasi gudang:\033[0m")
        print(f"{'ID':<10} | {'Nama Barang':<25} | {'Stok Gudang':<15}")
        print("-"*57)
        for iid, name, qty in waiting_list:
            print(f"{iid:<10} | {name:<25} | {qty:<15}")
        print("\n\033[33mStok tersedia di gudang, menunggu pihak terkait untuk mengkonfirmasi sebagai 'Siap Jual'\033[0m")

    # Kalau keduanya kosong
    else:
        print("\n\033[31mTidak ada barang siap jual maupun stok menunggu konfirmasi\033[0m")

''' MODELS '''
@dataclass
class Employee:
    id: str
    name: str
    role: str
    address: str = "-"
    phone: str = "-"
    status: str = "Aktif"
@dataclass
class Lokomotif:
    id: str
    name: str
    service_type: str      
    rate_per_day: int           # biaya service per hari
    status: str = "Tersedia"
@dataclass
class MenuItem:
    id: str
    name: str
    price: int
    stock: int
@dataclass
class Sale:
    sale_id: str
    items: List[Tuple[str, int]]
    total: int
    date: str
    cashier: str
    payment_method: str = "Tunai"
    warehouse_id: Optional[str] = None
    note: Optional[str] = None
@dataclass
class ServiceRecord:
    lokomotif_id: str
    customer: str
    service_type: str
    days: int
    parts_used: List[str]        # daftar sparepart dari inventory
    parts_cost: int              # biaya sparepart
    total_fee: int               # total = jasa + sparepart
    start_date: str
    end_date: str
    officer: str
    status: str = "Berjalan"     # default saat mulai service
@dataclass
class FoodOrder:
    items: List[Tuple[str, int]]
    total: int
    date: str
    waiter: str
    customer_name: str
    table_number: str
@dataclass
class InventoryItem:
    item_id: str
    name: str
    price: int
    category: str = "Umum"          # contoh: "Suku Cadang", "Peralatan", "Bahan Bakar"
    status: str = "Pending"         # "Pending", "Siap Jual", "Rusak/Hilang", "Disimpan"
    confirmed_stock: int = 0        # stok aman yang dikonfirmasi oleh admin inventaris
    stock_by_warehouse: Dict[str, int] = field(default_factory=dict)  # stok fisik per gudang

    def total_stock(self) -> int:
        # total stok fisik dari semua gudang
        return sum(self.stock_by_warehouse.values())
@dataclass
class Warehouse:
    warehouse_id: str
    name: str
    address: str
    stock: dict = field(default_factory=dict)
class RentalRecord:
    def __init__(self, lokomotif_id: str, customer: str, days: int,
                total_fee: int, start_date: str, end_date: str, officer: str):
        self.lokomotif_id = lokomotif_id
        self.customer = customer
        self.days = days
        self.total_fee = total_fee
        self.start_date = start_date
        self.end_date = end_date
        self.officer = officer
        self.status = "Berjalan"  # default saat mulai rental
class Store:
    def __init__(self):
        self.inventory: Dict[str, InventoryItem] = {}
        self.employees: Dict[str, Employee] = {}
        self.lokomotif: Dict[str, Lokomotif] = {}
        self.menu: Dict[str, MenuItem] = {}
        self.sales: Dict[str, Sale] = {}
        self.services: List[ServiceRecord] = []
        self.food_orders: List[FoodOrder] = []
        self.warehouses: Dict[str, Warehouse] = {}
        self.rentals: List[RentalRecord] = []  
        self.counters = {"INV": 0, "EMP": 0, "LOK": 0, "MEN": 0, "REN": 0, "SALE": 0}

    def gen_id(self, prefix: str) -> str:
        self.counters[prefix] += 1
        return f"{prefix}{self.counters[prefix]:04d}"
store = Store()

''' USER MANAGEMENT '''
current_user = None
current_role = None

# Load & Save Users
def load_users():
    try:
        with open("users.json", "r") as f:
            data = json.load(f)
            # Pastikan semua akun punya field last_login *auto-fix
            for uname, info in data.items(): 
                if "last_login" not in info:
                    info["last_login"] = "-"
                if "status" not in info:
                    info["status"] = "Aktif"  # fallback default
            return data
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_users():
    # pastikan all account punya filed wajib
    for uname, info in users.items():
        if "last_login" not in info:
            info["last_login"] = "-"
        if "status" not in info:
            info["status"] = "Aktif"
        if "role" not in info:
            info["role"] = "N/A"
        if "employee_id" not in info:
            info["employee_id"] = "N/A"

    with open("users.json", "w") as f:
        json.dump(users, f, indent=2)

# Inisialisasi users
users = load_users()
# default admin
if "admin" not in users:
    emp_id = "EMP0004"
    users["admin"] = {
        "password": "123",
        "employee_id": emp_id,
        "role": "admin",
        "status": "Aktif",
        "last_login": "-"}
    save_users()

# Registrasi
def register():
    head("REGISTRASI")
    print("\033[3m\033[33m*ketik 0 untuk kembali\033[0m\n")

    username = input("Buat username: ").strip().lower()
    if username == "0":
        return
    if not username:
        print("\n\033[31mUsername tidak boleh kosong\033[0m")
        return
    if username in users:
        print("\n\033[31mUsername sudah dipakai\033[0m")
        return

    # Password
    while True:
        password = input("Buat password: ").strip()
        if password == "0":
            return
        if not password:
            print("\n\033[31mPassword tidak boleh kosong\033[0m")
            continue

        confirm_password = input("Konfirmasi password: ").strip()
        if confirm_password == "0":
            return
        if confirm_password != password:
            print("\n\033[31mPassword tidak cocok, silakan coba lagi\033[0m")
            continue
        else:
            break

    # Pilih role
    role_ops = {
        "1": "admin",
        "2": "kasir",
        "3": "service",
        "4": "rental",
        "5": "dapur",
        "6": "pembeli",
        "7": "gudang"}
    print("\n>> Pilih role:")
    for k, v in role_ops.items():
        print(f"{k}. {v.capitalize()}")

    while True:
        role_choice = input("Role \033[33m(pilih angka)\033[0m: ").strip()
        if role_choice == "0":
            return
        if role_choice in role_ops:
            role = role_ops[role_choice]
            break
        else:
            print("\n\033[31mPilihan tidak valid. Coba lagi\033[0m")

    # Karyawan baru
    emp_id = store.gen_id("EMP")
    store.employees[emp_id] = Employee(emp_id, username.capitalize(), role)

    # Simpan user dengan field lengkap
    users[username] = {
        "password": password,
        "employee_id": emp_id,
        "role": role,
        "status": "Aktif",       # default status
        "last_login": "-"}        # default last login
    save_users()
    print(f"\n\033[32mRegistrasi berhasil sebagai \033[36m{username}\033[0m \033[33m(role: {role})\033[0m")

# Akun
def change_role():
    username = input("\nUsername akun: ").strip().lower()
    if username not in users:
        print("\n\033[31mAkun tidak ditemukan\033[0m")
        return

    old_role = users[username].get("role")
    if not old_role:
        # fallback: ambil dari Employee
        emp_id = users[username].get("employee_id")
        if emp_id in store.employees:
            old_role = store.employees[emp_id].role
        else:
            old_role = "N/A"

    print(f"Role lama akun '{username}': {old_role}\n\033[3m\033[33m*enter jika ingin batal\033[0m")
    new_role = input("\nMasukkan role baru: ").strip()
    if new_role:
        users[username]["role"] = new_role
        # sinkron ke Employee juga
        emp_id = users[username].get("employee_id")
        if emp_id in store.employees:
            store.employees[emp_id].role = new_role
        save_users()
        print(f"\n\033[32mRole akun '{username}' berhasil diubah menjadi {new_role}\033[0m")

def reset_password():
    global users, current_user, current_role
    print("\n\033[44m=========== RESET PASSWORD ===========\033[0m")

    if not current_user:
        print("\n\033[31mAnda harus login terlebih dahulu\033[0m")
        return

    # Admin tidak boleh reset password orang lain
    if current_role == "admin":
        print("\n\033[31mAdmin tidak bisa mereset password karyawan lain\033[0m")
        return
    # Ambil akun yang sedang login
    username = current_user
    old_pass = input("\nPassword lama: ").strip()
    if old_pass != users[username]["password"]:
        print("\n\033[31mPassword lama salah\033[0m")
        return
    # Input password baru
    while True:
        new_pass = input("Password baru: ").strip()
        if not new_pass:
            print("\n\033[31mPassword tidak boleh kosong\033[0m")
            continue

        confirm_pass = input("Konfirmasi password baru: ").strip()
        if confirm_pass != new_pass:
            print("\n\033[31mPassword tidak cocok, coba lagi\033[0m")
            continue
        else:
            break
    # Simpan perubahan
    users[username]["password"] = new_pass
    save_users()
    print(f"\n\033[32mPassword akun '{username}' berhasil diubah\033[0m")

def forgot_password():
    global users, current_role
    print("\n\033[44m=========== LUPA PASSWORD ===========\033[0m")

    # Hanya admin boleh jalankan
    if current_role != "admin":
        print("\n\033[31mHanya admin yang bisa melakukan reset darurat\033[0m")
        return

    username = input("\nUsername lupa password: ").strip().lower()
    if not username:
        print("\n\033[31mUsername tidak boleh kosong\033[0m")
        return

    if username not in users:
        print("\n\033[31mUsername tidak ditemukan\033[0m")
        return

    # Generate password numeric random (6 digit)
    temp_pass = str(random.randint(100000, 999999))

    users[username]["password"] = temp_pass
    save_users()

    print(f"\n\033[32mPassword akun '{username}' berhasil direset ke sementara: {temp_pass}\033[0m")
    print("\033[33mUser wajib login dengan password sementara lalu mengganti password sendiri\033[0m")

def list_accounts(simple=False):
    print("\n\033[44m============= DAFTAR AKUN =============\033[0m")
    if not users:
        print("\n\033[33mBelum ada akun terdaftar\033[0m")
        return

    if simple:
        # Versi ringkas (seperti print_users)
        print(f"\n{'Username':<12} | {'Role':<10} | {'Employee ID':<12} | {'Nama':<20} | {'Last Login':<20}")
        print("-"*80)
        for uname, data in users.items():
            role = data.get("role", "-")
            emp_id = data.get("employee_id", "-")
            emp_name = store.employees[emp_id].name if emp_id in store.employees else "-"
            last_login = data.get("last_login", "-")
            print(f"{uname:<12} | {role:<10} | {emp_id:<12} | {emp_name:<20} | {last_login:<20}")
    else:
        # Versi lengkap (status + fallback)
        print(f"\n{'Username':<12} | {'Role':<10} | {'ID (EMP)':<8} | {'Nama Karyawan':<15} | {'Status':<11} | {'Last Login':<20}")
        print("-"*90)
        for uname, data in users.items():
            emp_id = data.get("employee_id", "N/A")
            emp_name = "Unknown"
            role = data.get("role")
            if emp_id in store.employees:
                emp_name = store.employees[emp_id].name
                if not role or role == "N/A":
                    role = store.employees[emp_id].role
            else:
                role = role if role else "N/A"

            status = data.get("status", "Aktif")
            last_login = data.get("last_login", "-")
            status_display = "\033[32mAktif\033[0m" if status == "Aktif" else "\033[33mNonaktif\033[0m"
            print(f"{uname:<12} | {role:<10} | {emp_id:<8} | {emp_name:<15} | {status_display:<21} | {last_login:<20}")
    pause()

def lihat_profil(emp_id, current_user, current_role):
    print("\n\033[44m=========== PROFIL KARYAWAN ===========\033[0m\n")
    user_data = users.get(current_user)

    # Karyawan biasa hanya bisa lihat profil sendiri
    if current_role != "admin":
        if not user_data or user_data.get("employee_id") != emp_id:
            print("\n\033[31mAnda hanya bisa melihat profil sendiri\033[0m")
            return

    # Cek di store.employees dulu
    if emp_id in store.employees:
        emp = store.employees[emp_id]
        print(f"ID Karyawan   : {emp.id}")
        print(f"Nama          : {emp.name}")
        print(f"Role          : {emp.role}")
        print(f"Alamat        : {getattr(emp, 'address', '-')}")
        print(f"Nomor HP      : {getattr(emp, 'phone', '-')}")
        print(f"Status        : {getattr(emp, 'status', 'Aktif')}")
    else:
        # Fallback ke users.json
        for uname, data in users.items():
            if data.get("employee_id") == emp_id:
                print(f"ID Karyawan   : {emp_id}")
                print(f"Nama          : {uname.capitalize()}")
                print(f"Role          : {data.get('role','N/A')}")
                print(f"Alamat        : -")
                print(f"Nomor HP      : -")
                print(f"Status        : {data.get('status','Aktif')}")
                break
        else:
            print(f"\n\033[31mKaryawan '{emp_id}' tidak ditemukan\033[0m")
            return

    # Hubungan dengan akun login
    for uname, data in users.items():
        if data.get("employee_id") == emp_id:
            role_akun = data.get("role") or "N/A"
            print(f"Akun Login    : {uname}")
            print(f"Role Akun     : {role_akun}")
            print(f"Status Akun   : {data.get('status','Aktif')}")
            print(f"Last Login    : {data.get('last_login','-')}")
            break

def edit_profil(emp_id, current_user, current_role):
    if emp_id not in store.employees:
        print(f"\n\033[31mKaryawan '{emp_id}' tidak ditemukan\033[0m")
        return
    emp = store.employees[emp_id]
    print("\n\033[44m=========== EDIT PROFIL ===========\033[0m")
    print("\033[3m*Kosongkan input jika tidak ingin mengubah field\033[0m\n")
    # Semua bisa ubah nama, alamat, kontak
    new_name = input(f"\nNama ({emp.name}): ").strip()
    if new_name:
        emp.name = new_name

    if hasattr(emp, "address"):
        new_address = input(f"Alamat ({emp.address}): ").strip()
        if new_address:
            emp.address = new_address

    if hasattr(emp, "phone"):
        new_phone = input(f"Nomor HP ({emp.phone}): ").strip()
        if new_phone:
            emp.phone = new_phone
    # Hanya admin boleh ubah status & role
    if current_role == "admin":
        new_status = input(f"Status ({getattr(emp, 'status', 'Aktif')}): ").strip()
        if new_status:
            emp.status = new_status
            # sinkron ke akun login
            for uname, data in users.items():
                if data.get("employee_id") == emp_id:
                    data["status"] = new_status

        new_role = input(f"Role ({emp.role}): ").strip()
        if new_role:
            emp.role = new_role
            for uname, data in users.items():
                if data.get("employee_id") == emp_id:
                    # fallback: kalau role kosong/N/A, isi baru
                    if not data.get("role") or data.get("role") == "N/A":
                        data["role"] = new_role
                    else:
                        data["role"] = new_role
    else:
        print("\n\033[33mAnda tidak memiliki izin untuk mengubah status atau role\033[0m")
    save_users()
    print("\n\033[32mProfil berhasil diperbarui\033[0m")

def set_account_status():
    uname = input("\nUsername akun: ").strip().lower()
    if uname not in users:
        print(f"\n\033[31mAkun {uname} tidak ditemukan\033[0m")
        return

    emp_id = users[uname].get("employee_id")
    emp_name = store.employees[emp_id].name if emp_id in store.employees else "Unknown"

    current_status = users[uname].get("status", "Aktif")
    print(f"\nStatus akun '{uname}' ({emp_name}) saat ini: {current_status}")

    if current_status == "Aktif":
        yakin = input("\nNonaktifkan akun ini? (y/n): ").strip().lower()
        if yakin == "y":
            users[uname]["status"] = "Nonaktif"
            print(f"\n\033[33mAkun '{uname}' ({emp_name}) berhasil dinonaktifkan\033[0m")
    else:
        yakin = input("\nAktifkan kembali akun ini? (y/n): ").strip().lower()
        if yakin == "y":
            users[uname]["status"] = "Aktif"
            print(f"\n\033[32mAkun '{uname}' ({emp_name}) berhasil diaktifkan kembali\033[0m")
    save_users()

def search_account(keyword: str):
    print("\n\033[44m=========== PENCARIAN AKUN ===========\033[0m")
    if not keyword:
        print("\n\033[31mInput pencarian tidak boleh kosong\033[0m")
        return

    keyword = keyword.lower()
    found = False

    # Header tabel
    print(f"\n{'Username':<12} | {'Role':<10} | {'ID (EMP)':<8} | {'Nama Karyawan':<15} | {'Status':<11} | {'Last Login':<20}")
    print("-"*95)

    for uname, data in users.items():
        emp_id = data.get("employee_id", "N/A")
        emp_name = "Unknown"
        role = data.get("role")

        if emp_id in store.employees:
            emp_name = store.employees[emp_id].name
            # fallback kalau role kosong/N/A
            if not role or role == "N/A":
                role = store.employees[emp_id].role
        else:
            role = role if role else "N/A"

        status = data.get("status", "Aktif")
        last_login = data.get("last_login", "-")

        # Warna status hanya saat ditampilkan
        if status == "Aktif":
            status_display = "\033[32mAktif\033[0m"
        else:
            status_display = "\033[33mNonaktif\033[0m"

        # Cocokkan dengan username, nama karyawan, atau Emp.ID
        if keyword in uname.lower() or keyword in emp_name.lower() or keyword in emp_id.lower():
            print(f"{uname:<12} | {role:<10} | {emp_id:<8} | {emp_name:<15} | {status_display:<20} | {last_login:<20}")
            found = True

    if not found:
        print(f"\n\033[33mTidak ada akun yang cocok dengan '{keyword}'\033[0m")

def update_last_login(uname: str):
    if uname in users:
        ts = datetime.now().strftime("%Y-%m-%d (%H:%M:%S)")
        users[uname]["last_login"] = ts
        save_users()
        
# Login
def login():
    global current_user, current_role
    while True:
        head("LOGIN SISTEM")
        print("\033[3m\033[33m*ketik 0 untuk kembali\033[0m\n")
        u = input("Username: ").strip().lower()
        if u == "0": 
            return
        p = input("Password: ").strip()

        if u in users and users[u]["password"] == p:
            emp_id = users[u].get("employee_id")
            emp = store.employees.get(emp_id) if emp_id else None

            current_user = u
            # pastikan role selalu lowercase agar cocok dengan main_menu
            role_val = users[u].get("role", emp.role if emp else "pembeli")
            current_role = role_val.lower()

            emp_name = emp.name if emp else u.capitalize()
            print(f"\n\033[32mLogin berhasil sebagai \033[33m{emp_name}\033[32m (role: {current_role})\033[0m")

            # debug tambahan untuk memastikan role benar
            print(f"[DEBUG] current_user={current_user}, current_role={current_role}")
            update_last_login(u)
            return
        else:
            print("\n\033[31mLogin gagal. Coba lagi\033[0m")

# Logout uv.4.2.7
def logout():
    global current_user, current_role
    current_user, current_role = None, None
    print("\n\033[32mBerhasil logout. Silakan login kembali.\033[0m")
    return

# Delelte User uv.3.3
def delete_user():
    global users, current_user, current_role
    if current_role != "admin":
        print("\033[31mHanya admin yang boleh menghapus akun\033[0m")
        return

    if not isinstance(users, dict) or not users:
        print("\n\033[31mData users belum tersedia atau rusak\033[0m")
        return

    print("\n\033[44m=========== HAPUS AKUN ===========\033[0m")
    username = input("Username yang dihapus: ").strip().lower()  # konsisten lowercase

    if username in users:
        confirm = input(
            f"\n\033[33mYakin ingin menghapus akun '\033[32m{username}\033[33m'? (y/n):\033[0m "
        ).strip().lower()
        if confirm == "y":
            del users[username]
            save_users()
            print(f"\n\033[32mAkun '{username}' berhasil dihapus\033[0m")

            # logout otomatis kalau akun sendiri dihapus
            if current_user == username:
                logout()  # panggil fungsi logout() biar konsisten
        else:
            print("\n\033[33mPenghapusan dibatalkan\033[0m")
    else:
        print(f"\n\033[33mUsername '{username}' tidak ditemukan\033[0m")

# Utk transaksi
def safe_load_json_line(line: str):
    try:
        return json.loads(line)
    except json.JSONDecodeError:
        print(f"\033[33mBaris rusak, dilewati: {line.strip()}\033[0m")
        return None

def load_sales():
    try:
        with open("sales.txt", "r") as f:
            for line in f:
                rec = safe_load_json_line(line)
                if rec:
                    sale = Sale(
                        sale_id=rec.get("sale_id", store.gen_id("SALE")),
                        items=rec.get("items", []),
                        total=int(rec.get("total", rec.get("amount", 0))),
                        date=rec.get("date", "-"),
                        cashier=rec.get("cashier", "-"))
                    # simpan ke dict dengan key sale_id
                    store.sales[sale.sale_id] = sale
    except FileNotFoundError:
        pass

def load_services():
    try:
        with open("services.txt", "r") as f:
            for line in f:
                rec = safe_load_json_line(line)
                if rec:
                    store.services.append(ServiceRecord(
                        lokomotif_id=rec["lokomotif_id"],
                        customer=rec["customer"],
                        service_type=rec.get("service_type", "Umum"),
                        days=int(rec["days"]),
                        parts_used=rec.get("parts_used", []),
                        parts_cost=int(rec.get("parts_cost", 0)),
                        total_fee=int(rec.get("total_fee", rec.get("total", 0))),
                        start_date=rec.get("start_date", rec.get("date", "")),
                        end_date=rec.get("end_date", ""),
                        officer=rec.get("officer", ""),
                        status=rec.get("status", "Berjalan")
                    ))
    except FileNotFoundError:
        pass

def load_food_orders():
    try:
        with open("food_orders.txt", "r") as f:
            for line in f:
                rec = safe_load_json_line(line)
                if rec:
                    store.food_orders.append(FoodOrder(
                        rec["items"], int(rec["total"]), rec["date"],
                        rec["waiter"], rec.get("customer_name", ""), rec.get("table_number", "")
                    ))
    except FileNotFoundError:
        pass

''' CRUD MODULES '''
def add_inventory(name: str, price: int, category: str = "Umum", stok_awal: int = 0, silent=False):
    # Cek duplikat nama barang
    for it in store.inventory.values():
        if it.name.lower() == name.lower():
            if not silent:
                print("\n\033[31mBarang dengan nama ini sudah ada\033[0m")
            return None

    # Buat ID baru
    item_id = store.gen_id("INV")
    item = InventoryItem(item_id, name, price, category)
    item.confirmed_stock = stok_awal
    store.inventory[item_id] = item

    # Catat ke log
    record = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "user": current_user if not silent else "system",
        "item_id": item_id,
        "name": name,
        "jumlah": item.confirmed_stock,
        "harga": price,
        "kategori": str(category),
        "status": "Pending"}
    with open("inventory_log.txt", "a") as f:
        f.write(json.dumps(record) + "\n")

    # Tambahkan stok ke Gudang Pusat
    pusat = store.warehouses.get("Pusat")
    if pusat:
        pusat.stock[item_id] = pusat.stock.get(item_id, 0) + stok_awal
    if not silent:
        print(f"\033[32mBarang {name} ditambahkan dengan ID {item_id}\033[0m")
    return item

def edit_inventory(item_id: str, new_name: str = None, new_price: int = None,
                new_category: str = None, new_confirmed_stock: int = None,
                delete: bool = False, reason: str = None, note: str = None):
    if item_id not in store.inventory:
        print("\n\033[31mBarang tidak ditemukan\033[0m")
        return

    item = store.inventory[item_id]
    # hapus
    if delete:
        record = {
            "date": datetime.now().strftime("%Y-%m-%d (%H:%M)"),
            "operator": current_user,
            "item_id": item_id,
            "name": item.name,
            "price": item.price,
            "reason": reason if reason else "Tidak ada alasan",
            "note": note if note else ""}
        with open("inventory_deletions.txt", "a") as f:
            f.write(json.dumps(record) + "\n")

        item.stock_by_warehouse.clear()
        del store.inventory[item_id]
        print(f"\033[32m Barang {item_id} ({item.name}) berhasil dihapus \033[0m")
        return

    # ubah/modif
    changes = {}
    if new_name:
        changes["name"] = (item.name, new_name)
        item.name = new_name
    if new_price is not None:
        changes["price"] = (item.price, new_price)
        item.price = new_price
    if new_category:
        changes["category"] = (item.category, KATEGORI_LIST.get(new_category, new_category))
        item.category = new_category
    if new_confirmed_stock is not None:
        changes["confirmed_stock"] = (item.confirmed_stock, new_confirmed_stock)
        item.confirmed_stock = new_confirmed_stock

    # catat ke log
    if changes:
        record = {
            "date": datetime.now().strftime("%Y-%m-%d (%H:%M)"),
            "operator": current_user,
            "item_id": item_id,
            "name": item.name,
            "changes": changes}
        with open("inventory_log.txt", "a") as f:
            f.write(json.dumps(record) + "\n")

    print(f"\033[32mBarang {item_id} berhasil diperbarui\033[0m")

def add_employee(name: str, role: str, address: str = "", phone: str = "", silent=False):
    # Cek duplikasi nama
    for emp in store.employees.values():
        if emp.name.lower() == name.lower():
            if not silent:
                print("\n\033[31mKaryawan dengan nama ini sudah ada\033[0m")
            return None

    # Generate ID karyawan
    emp_id = store.gen_id("EMP")

    # Buat objek Employee dengan alamat & telepon
    store.employees[emp_id] = Employee(emp_id, name, role, address, phone)

    # Tambahkan ke users (otomatis buat akun login)
    username = name.lower().replace(" ", "")
    password = emp_id
    users[username] = {
        "password": password,
        "employee_id": emp_id,
        "role": role,
        "status": "Aktif",
        "last_login": "-"}
    save_users()

    if not silent:
        print(f"\n\033[32mKaryawan {name} ditambahkan dengan ID {emp_id}\033[0m")
        print(f"\033[33mAkun login: username='{username}', password='{password}' (role: {role})\033[0m")

    return emp_id

def add_lokomotif(name: str, service_type: str, rate_per_day: int, silent=False):
    for lok in store.lokomotif.values():
        if lok.name.lower() == name.lower():
            if not silent:
                print("\n\033[31mLokomotif dengan nama ini sudah ada\033[0m")
            return
    lok_id = store.gen_id("LOK")
    store.lokomotif[lok_id] = Lokomotif(
        id=lok_id,
        name=name,
        service_type=service_type,
        rate_per_day=rate_per_day,
        status="Tersedia")
    if not silent:
        print(f"\n\033[32mLokomotif {name} ditambahkan dengan ID {lok_id}\033[0m")

def add_menu(name: str, stock: int, price: int, silent=False):
    for menu in store.menu.values():
        if menu.name.lower() == name.lower():
            if not silent:
                print("\n\033[31mMenu dengan nama ini sudah ada\033[0m")
            return
    menu_id = store.gen_id("MEN")
    store.menu[menu_id] = MenuItem(menu_id, name, stock, price)
    if not silent:
        print(f"\n\033[32mMenu {name} ditambahkan dengan ID {menu_id}, dengan stok {stock}\033[0m")

def add_warehouse(name: str, address: str, silent=False):
    # cek duplikat
    for w in store.warehouses.values():
        if w.name.lower() == name.lower():
            print(f"\n\033[31mGudang dengan nama '{name}' sudah ada (ID: {w.warehouse_id})\033[0m")
            return
    # generate ID unik
    wid = f"W{len(store.warehouses)+1:03}"
    store.warehouses[wid] = Warehouse(wid, name, address)

    if not silent:
        print(f"\n\033[32mGudang {name} ditambahkan dengan ID {wid}\033[0m")

def add_account():
    global users
    head("BUAT AKUN KARYAWAN")
    # Tampilkan daftar karyawan yang belum punya akun
    print("\n>> Nama Karyawan:")
    available = []
    for emp_id, emp in store.employees.items():
        if not any(u["employee_id"] == emp_id for u in users.values()):
            print(f"{emp_id:<8} | {emp.name:<20} | {emp.role:<10}")
            available.append(emp_id)

    if not available:
        print("\n\033[33mSemua karyawan sudah punya akun\033[0m")
        print("\033[3m*Jika ingin menambah akun baru, pilih menu 'Tambah Karyawan' di modul Karyawan\033[0m")
        return
    else:
        print("\n\033[3mJika karyawan belum terdaftar, pilih menu 'Tambah Karyawan' di modul Karyawan terlebih dahulu\033[0m")

    # Input username
    username = input("\nUsername baru: ").strip().lower()
    if not username:
        print("\n\033[31mUsername tidak boleh kosong\033[0m")
        return
    if username in users:
        print(f"\n\033[31mUsername ini {username} sudah ada\033[0m")
        return
    # Input password
    password = input("Password: ").strip()
    if not password:
        print("\n\033[31mPassword tidak boleh kosong\033[0m")
        return
    # Pilih role
    role_ops = {
        "1": "admin",
        "2": "kasir",
        "3": "service",
        "4": "dapur",
        "5": "pembeli",
        "6": "gudang"}
    print("\n>> Pilih role:")
    for k, v in role_ops.items():
        print(f"{k}. {v.capitalize()}")

    role_choice = input("Role (pilih angka): ").strip()
    if role_choice not in role_ops:
        print("\n\033[31mRole tidak valid\033[0m")
        return
    role = role_ops[role_choice]

    # Pilih karyawan dari daftar
    emp_id = input("\nID Karyawan: ").strip().upper()
    if emp_id not in available:
        print("\n\033[31mID Karyawan tidak valid atau sudah punya akun\033[0m")
        print("\nGunakan menu 'Tambah Karyawan' di modul Karyawan untuk membuat ID baru.")
        return

    # Simpan akun
    users[username] = {
        "password": password,
        "employee_id": emp_id,
        "role": role,
        "status": "Aktif",
        "last_login": "-"}
    save_users()
    print(f"\n\033[32mAkun '{username}' berhasil ditambahkan untuk karyawan {store.employees[emp_id].name} (role: {role})\033[0m")

def hapus_edit_transaksi():
    if current_role != "admin":
        print("\n\033[31mHanya admin yang boleh menghapus/mengedit transaksi\033[0m")
        return
    if not store.sales:
        print("\n\033[33mBelum ada transaksi penjualan\033[0m")
        return

    print("\n\033[34m>> Daftar Transaksi Penjualan:\033[0m")
    # Header tabel
    print(f"{'No':<4} | {'ID':<10} | {'Tanggal':<16} | {'Kasir':<12} | {'Detail':<30} | {'Total':<15} | {'Bayar':<10} | {'Gudang':<8}")
    print("-"*120)
    # Isi tabel
    for idx, sale in enumerate(store.sales, 1):
        detail = "; ".join(f"{store.inventory[i].name if i in store.inventory else i} x{q}" for i, q in sale.items)
        print(f"{idx:<4} | {sale.sale_id:<10} | {sale.date:<16} | {sale.cashier:<12} | {detail:<30} | {format_rupiah(sale.total):<15} | {sale.payment_method:<10} | {sale.warehouse_id:<8}")
    # Pilih transaksi
    idx_choice = input_int("\nPilih nomor transaksi untuk hapus/edit (0=keluar): ", min_val=0)
    if idx_choice == 0:
        return
    if idx_choice > len(store.sales):
        print("\n\033[31mNomor tidak valid\033[0m")
        return

    sale = store.sales[idx_choice - 1]
    action = input("Hapus atau Edit? (h/e): ").strip().lower()

    if action == "h":
        store.sales.remove(sale)
        log_employee_action(current_user, current_role, "Hapus Transaksi", {"sale_id": sale.sale_id, "reason": "Koreksi admin"})
        print(f"\n\033[32mTransaksi {sale.sale_id} berhasil dihapus\033[0m")
    elif action == "e":
        new_payment = input("\nMetode pembayaran baru (kosong=tidak ubah): ").strip()
        if new_payment:
            sale.payment_method = new_payment
        new_total = input("Total baru (kosong=tidak ubah): ").strip()
        if new_total.isdigit():
            sale.total = int(new_total)

        log_employee_action(current_user, current_role, "Edit Transaksi", {"sale_id": sale.sale_id, "reason": "Perubahan admin"})
        print(f"\n\033[32mTransaksi {sale.sale_id} berhasil diedit\033[0m")

def hapus_edit_rental():
    if current_role != "admin":
        print("\n\033[31mHanya admin yang boleh menghapus/mengedit rental\033[0m")
        return

    if not store.rentals:
        print("\n\033[33mBelum ada transaksi rental\033[0m")
        return

    print("\n\033[34m>> Daftar Transaksi Rental:\033[0m")
    print(f"{'No':<4} | {'Customer':<20} | {'Lokomotif':<20} | {'Durasi':<10} | {'Total':<15} | {'Officer':<12} | {'Status':<10}")
    print("-"*100)

    for idx, r in enumerate(store.rentals, 1):
        lok = store.lokomotif.get(r.lokomotif_id)
        nama_lok = lok.name if lok else r.lokomotif_id
        status = "Disewa" if lok and lok.status == "Disewa" else "Selesai"
        print(f"{idx:<4} | {r.customer:<20} | {nama_lok:<20} | {str(r.days)+' hari':<10} | {format_rupiah(r.total_fee):<15} | {r.officer:<12} | {status:<10}")

    idx_choice = input_int("\nPilih nomor transaksi untuk hapus/edit (0=keluar): ", min_val=0)
    if idx_choice == 0:
        return
    if idx_choice > len(store.rentals):
        print("\n\033[31mNomor tidak valid\033[0m")
        return

    r = store.rentals[idx_choice - 1]
    action = input("\nHapus atau Edit? (h/e): ").strip().lower()

    if action == "h":
        # Jika masih disewa, kembalikan status lokomotif ke 'Tersedia'
        if r.lokomotif_id in store.lokomotif and store.lokomotif[r.lokomotif_id].status == "Disewa":
            store.lokomotif[r.lokomotif_id].status = "Tersedia"

        store.rentals.remove(r)
        log_employee_action(current_user, current_role, "Hapus Rental", {"lok_id": r.lokomotif_id, "customer": r.customer, "reason": "Koreksi admin"})
        print(f"\n\033[32mRental {r.lokomotif_id} berhasil dihapus\033[0m")

    elif action == "e":
        old_days = r.days
        old_customer = r.customer

        new_days = input("Durasi baru (kosong=tidak ubah): ").strip()
        if new_days.isdigit() and int(new_days) > 0:
            r.days = int(new_days)
            r.total_fee = r.days * store.lokomotif[r.lokomotif_id].rate_per_day

        new_customer = input("Nama customer baru (kosong=tidak ubah): ").strip()
        if new_customer:
            r.customer = new_customer

        log_employee_action(current_user, current_role, "Edit Rental", {"lok_id": r.lokomotif_id, "old_days": old_days, "new_days": r.days, "old_customer": old_customer, "new_customer": r.customer, "reason": "Perubahan admin"})
        print(f"\n\033[32mRental {r.lokomotif_id} berhasil diedit\033[0m")

''' DASHBOARDS '''
# Dashboard hybrid uv.4.2.14
def dashboard():
    total_sales   = sum(s.total for s in store.sales.values())
    total_service = sum(r.total_fee for r in store.services)
    total_food    = sum(o.total for o in store.food_orders)
    total_rental  = sum(r.total_fee for r in store.rentals)
    grand_total   = total_sales + total_service + total_food + total_rental

    print("\n\033[44m ============== DASHBOARD ============== \033[0m")
    print(f"{'Transaksi':<20} | {'Jumlah':<8} | {'Total':<15}")
    print("-"*50)
    print(f"{'Penjualan Barang':<20} | {len(store.sales):<8} | {format_rupiah(total_sales):<15}")
    print(f"{'Service Lokomotif':<20} | {len(store.services):<8} | {format_rupiah(total_service):<15}")
    print(f"{'Pemesanan Makanan':<20} | {len(store.food_orders):<8} | {format_rupiah(total_food):<15}")
    print(f"{'Rental Lokomotif':<20} | {len(store.rentals):<8} | {format_rupiah(total_rental):<15}")
    print("-"*50)
    print(f"{'TOTAL SEMUA':<20} | {'':<8} | {format_rupiah(grand_total):<15}")

    print("\n\033[34m>> Ringkasan Data\033[0m")
    print(f"{'Inventaris':<12}: {len(store.inventory)} barang")
    print(f"{'Karyawan':<12}: {len(store.employees)} orang")
    print(f"{'Lokomotif':<12}: {len(store.lokomotif)} unit")
    print(f"{'Menu':<12}: {len(store.menu)} item")
    print(f"{'Gudang':<12}: {len(store.warehouses)} lokasi")
    # Detail umum
    laporan_detail()
# Admin
def dashboard_admin():
    print("\n\033[44m ============ DASHBOARD ADMIN ============ \033[0m")

    # Kondisi stok barang
    print("\n\033[34m>> Kondisi Stok Barang\033[0m")
    print(f"{'Nama Barang':<20} | {'Stok':<6} | {'Gudang':<20}")
    print("-"*50)
    low_inv = False
    for it in store.inventory.values():
        total = it.total_stock()
        if total < 5:
            low_inv = True
            gudang_list = [w.name for w in store.warehouses.values() if it.item_id in w.stock]
            gudang_ui = ", ".join(gudang_list) if gudang_list else "-"
            print(f"{it.name:<20} | {total:<6} | {gudang_ui:<20}")
    if not low_inv:
        print("- Semua stok barang aman")

    # Kondisi stok menu makanan
    print("\n\033[34m>> Kondisi Stok Menu Makanan\033[0m")
    print(f"{'Menu':<20} | {'Stok':<6}")
    print("-"*30)
    low_menu = False
    for m in store.menu.values():
        if m.stock < 5:
            low_menu = True
            print(f"{m.name:<20} | {m.stock:<6}")
    if not low_menu:
        print("- Semua stok menu aman")

    # Ringkasan transaksi
    total_sales   = sum(s.total for s in store.sales.values())
    total_service = sum(r.total_fee for r in store.services)
    total_food    = sum(o.total for o in store.food_orders)
    total_rental  = sum(r.total_fee for r in store.rentals)
    grand_total   = total_sales + total_service + total_food + total_rental

    print("\n\033[34m>> Ringkasan Transaksi\033[0m")
    print(f"{'Jenis':<20} | {'Jumlah':<8} | {'Total':<15}")
    print("-"*50)
    print(f"{'Penjualan Barang':<20} | {len(store.sales):<8} | {format_rupiah(total_sales):<15}")
    print(f"{'Service Lokomotif':<20} | {len(store.services):<8} | {format_rupiah(total_service):<15}")
    print(f"{'Pemesanan Makanan':<20} | {len(store.food_orders):<8} | {format_rupiah(total_food):<15}")
    print(f"{'Rental Lokomotif':<20} | {len(store.rentals):<8} | {format_rupiah(total_rental):<15}")
    print("-"*50)
    print(f"{'TOTAL SEMUA':<20} | {'':<8} | {format_rupiah(grand_total):<15}")

    # Ringkasan data
    print("\n\033[34m>> Ringkasan Data\033[0m")
    print(f"{'Inventaris':<12}: {len(store.inventory)} barang")
    print(f"{'Karyawan':<12}: {len(store.employees)} orang")
    print(f"{'Lokomotif':<12}: {len(store.lokomotif)} unit")
    print(f"{'Menu':<12}: {len(store.menu)} item")

    # Laporan Karyawan & Akun
    print("\n\033[34m>> Laporan Karyawan & Akun\033[0m")
    print(f"{'ID (EMP)':<8} | {'Nama':<20} | {'Jabatan':<12} | {'Username':<15} | {'Role Akun':<12}")
    print("-"*75)
    for emp_id, emp in store.employees.items():
        username = "-"
        role_akun = "-"
        for uname, udata in users.items():
            if udata["employee_id"] == emp_id:
                username = uname
                role_akun = udata.get("role", "-")
                break
        print(f"{emp.id:<8} | {emp.name:<20} | {emp.role:<12} | {username:<15} | {role_akun:<12}")

    # Barang terlaris
    counter = {}
    for s in store.sales.values():
        for i, q in s.items:
            it = store.inventory.get(i)
            if it:
                counter[it.name] = counter.get(it.name, 0) + q
            else:
                counter[f"[UNKNOWN:{i}]"] = counter.get(f"[UNKNOWN:{i}]", 0) + q
    top_items(counter, "Barang Terlaris", "unit")

    # Lokomotif terlaris (service)
    lokomotif_count = {}
    for r in store.services:
        lok = store.lokomotif.get(r.lokomotif_id)
        if lok:
            lokomotif_count[lok.name] = lokomotif_count.get(lok.name, 0) + 1
    top_items(lokomotif_count, "Lokomotif Terlaris (service)", "kali diservis")

    # Lokomotif terlaris (rental)
    rental_count = {}
    for r in store.rentals:
        lok = store.lokomotif.get(r.lokomotif_id)
        if lok:
            rental_count[lok.name] = rental_count.get(lok.name, 0) + 1
    top_items(rental_count, "Lokomotif Terlaris (rental)", "kali disewa")

    # Menu favorit
    food_count = {}
    for o in store.food_orders:
        for i, q in o.items:
            m = store.menu.get(i)
            if m:
                food_count[m.name] = food_count.get(m.name, 0) + q
            else:
                food_count[f"[UNKNOWN:{i}]"] = food_count.get(f"[UNKNOWN:{i}]", 0) + q
    top_items(food_count, "Menu Favorit", "porsi")

    # Sparepart terpakai
    print("\n\033[34m>> Sparepart Terpakai\033[0m")
    parts_summary = {}
    for r in store.services:
        for part in r.parts_used:
            parts_summary[part] = parts_summary.get(part, 0) + 1
    if parts_summary:
        print(f"{'Sparepart':<20} | {'Jumlah':<6}")
        print("-"*30)
        for part, count in parts_summary.items():
            print(f"{part:<20} | {count:<6}")
    else:
        print("- Belum ada sparepart terpakai")
# Kasir
def dashboard_kasir():
    print("\n\033[44m ============== DASHBOARD KASIR ============== \033[0m")
    if not store.sales:
        print("\n\033[33mBelum ada transaksi penjualan\033[0m")
        return
    
    total_sales = sum(s.total for s in store.sales)
    print(f"{'Jumlah Transaksi':<20}: {len(store.sales)}")
    print(f"{'Total Penjualan':<20}: {format_rupiah(total_sales)}")

    # Barang terlaris
    counter = {}
    for s in store.sales:
        for i, q in s.items:
            nm = store.inventory[i].name
            counter[nm] = counter.get(nm, 0) + q

    print("\n\033[34m>> Barang Terlaris\033[0m")
    print(f"{'Nama Barang':<20} | {'Jumlah':<6}")
    print("-"*30)
    for nm, qty in counter.items():
        print(f"{nm:<20} | {qty:<6}")
# Service
def dashboard_service():
    print("\n\033[44m =========== DASHBOARD SERVICE ============ \033[0m")
    if not store.services:
        print("\n\033[33mBelum ada transaksi service lokomotif\033[0m")
        return

    total_service = sum(r.total_fee for r in store.services)
    print(f"{'Jumlah Transaksi':<25}: {len(store.services)}")
    print(f"{'Total Pendapatan Service':<25}: {format_rupiah(total_service)}")

    # Lokomotif terlaris
    lokomotif_count = {}
    for r in store.services:
        lok = store.lokomotif.get(r.lokomotif_id)
        if lok:
            lokomotif_count[lok.name] = lokomotif_count.get(lok.name, 0) + 1

    print("\n\033[34m>> Lokomotif Terlaris (Service)\033[0m")
    print(f"{'Nama Lokomotif':<20} | {'Jumlah':<6}")
    print("-"*30)
    for nm, qty in lokomotif_count.items():
        print(f"{nm:<20} | {qty:<6}")

    print("\n\033[34m>> Status Lokomotif\033[0m")
    print(f"{'Nama Lokomotif':<20} | {'Status':<12}")
    print("-"*35)
    for lok in store.lokomotif.values():
        if lok.status == "Tersedia":
            status = "\033[32mTersedia\033[0m"
        elif lok.status == "Diservis":
            status = "\033[33mDiservis\033[0m"
        else:
            status = "\033[36mSelesai\033[0m"
        print(f"{lok.name:<20} | {status:<12}")
# Rental
def dashboard_rental():
    print("\n\033[44m ============ DASHBOARD RENTAL ============ \033[0m")
    if not store.rentals:
        print("\n\033[33mBelum ada transaksi rental\033[0m")
        return

    total_rental = sum(r.total_fee for r in store.rentals)
    active = sum(1 for r in store.rentals if r.status == "Berjalan")
    selesai = sum(1 for r in store.rentals if r.status == "Selesai")

    print(f"{'Jumlah Transaksi Rental':<25}: {len(store.rentals)}")
    print(f"{'Rental Aktif':<25}: {active}")
    print(f"{'Rental Selesai':<25}: {selesai}")
    print(f"{'Total Pendapatan Rental':<25}: {format_rupiah(total_rental)}")

    # Lokomotif paling sering disewa
    rental_count = {}
    for r in store.rentals:
        lok = store.lokomotif.get(r.lokomotif_id)
        if lok:
            rental_count[lok.name] = rental_count.get(lok.name, 0) + 1

    print("\n\033[34m>> Lokomotif Terlaris (Rental)\033[0m")
    print(f"\n{'Nama Lokomotif':<20} | {'Jumlah Disewa':<15}")
    print("-"*40)
    if rental_count:
        for nm, qty in rental_count.items():
            print(f"{nm:<20} | {qty:<15}")
    else:
        print("- Belum ada data")

    # Detail transaksi rental
    print("\n\033[34m>> Detail Transaksi Rental\033[0m")
    print(f"\n{'Customer':<20} | {'Lokomotif':<20} | {'Durasi':<6} | {'Total':<15} | {'Status':<10}")
    print("-"*80)
    for r in store.rentals:
        lok = store.lokomotif.get(r.lokomotif_id)
        nama_lok = lok.name if lok else r.lokomotif_id
        print(f"{r.customer:<20} | {nama_lok:<20} | {r.days:<6} | {format_rupiah(r.total_fee):<15} | {r.status:<10}")
# Dapur
def dashboard_dapur():
    print("\n\033[44m ============ DASHBOARD DAPUR ============ \033[0m")
    if not store.food_orders:
        print("\n\033[33mBelum ada pesanan makanan\033[0m")
        return
    
    total_food = sum(o.total for o in store.food_orders)
    print(f"{'Jumlah Pesanan':<25}: {len(store.food_orders)}")
    print(f"{'Total Pendapatan Makanan':<25}: {format_rupiah(total_food)}")

    # Menu favorit
    food_count = {}
    for o in store.food_orders:
        for i, q in o.items:
            nm = store.menu[i].name
            food_count[nm] = food_count.get(nm, 0) + q

    print("\n\033[34m>> Menu Favorit\033[0m")
    print(f"{'Nama Menu':<20} | {'Jumlah':<6}")
    print("-"*30)
    for nm, qty in food_count.items():
        print(f"{nm:<20} | {qty:<6}")
# Gudang
def dashboard_gudang():
    print("\n\033[44m ============ DASHBOARD GUDANG ============ \033[0m")
    # Ringkasan gudang
    print(f"Jumlah gudang: {len(store.warehouses)}")
    if not store.warehouses:
        print("\n\033[33mBelum ada gudang terdaftar\033[0m")
        return

    # Loop setiap gudang
    for wh in store.warehouses.values():
        print(f"\nGudang {wh.warehouse_id} - {wh.name} (Alamat: {wh.address})")
        print(f"{'ID':<8} | {'Nama Barang':<20} | {'Jumlah':<6} | {'Harga':<15} | {'Status':<12} | {'Total':<15}")
        print("-"*95)

        if not wh.stock:
            print("\n\033[33mTidak ada stok barang di gudang ini\033[0m")
            continue

        found = False
        total_gudang = 0
        for item_id, data in wh.stock.items():
            qty = data.get("qty", 0)
            status = data.get("status", "Baik")
            if qty > 0:
                found = True
                item = store.inventory.get(item_id)
                nama = item.name if item else "Unknown"
                harga = item.price if item else 0
                subtotal = qty * harga
                total_gudang += subtotal
                print(f"{item_id:<8} | {nama:<20} | {qty:<6} | {format_rupiah(harga):<15} | {status:<12} | {format_rupiah(subtotal):<15}")

        if not found:
            print("\033[33mTidak ada stok barang di gudang ini\033[0m")
        else:
            print("-"*95)
            print(f"{'TOTAL NILAI STOK':<73} | {format_rupiah(total_gudang):<15}")

''' MENUS '''
# >> Module menus
# INVENTARIS (clear v.4.2.12)
def inventory_menu():
    global current_role
    while True:
        # Karyawan Gudang
        if current_role == "gudang":
            ops = {
                "1": "Daftar Inventaris",
                "2": "Tambah Barang",
                "3": "Ubah/Hapus Barang",
                "4": "Lihat Riwayat Barang",
                "5": "Minta Konfirmasi Siap Jual",
                "9": "Kembali"}
            choice = input_menu("MENU INVENTARIS (Gudang)", ops)

            # Daftar inventaris
            if choice == "1":
                print_inventory()
                pause()
            # Tambah barang
            elif choice == "2":
                if not check_access("gudang"):
                    return
                name = input("\nNama barang: ").strip()
                jumlah = input_int("Jumlah unit: ", min_val=1)
                harga_beli = input_int("Harga beli per unit: ", min_val=1)
                category_code = pilih_kategori()
                item_id = store.gen_id("INV")

                # Simpan ke inventaris
                store.inventory[item_id] = InventoryItem(
                    item_id=item_id,
                    name=name,
                    price=harga_beli,
                    category=category_code)
                store.inventory[item_id].confirmed_stock = jumlah

                # integrasi gudang pusat
                default_wh = getattr(store, "default_warehouse", "WH01")
                if default_wh not in store.warehouses:
                    store.warehouses[default_wh] = Warehouse(default_wh, "Gudang Utama")

                store.warehouses[default_wh].stock[item_id] = {
                    "qty": jumlah,
                    "status": "Pending",
                    "price": harga_beli,
                    "category": category_code}

                log_warehouse("Barang Masuk Gudang", item_id, extra={"warehouse": default_wh, "qty": jumlah, "price": harga_beli})
                print(f"\n\033[32mBarang {name} otomatis ditambahkan ke gudang {default_wh}\033[0m")

                # Log inventaris
                log_inventory("Tambah Barang", store.inventory[item_id], {"jumlah": jumlah, "harga": harga_beli, "kategori": category_code, "status": "Pending"})
                log_employee_action(current_user, current_role, "Tambah Barang", {"item": name, "qty": jumlah})
            # Ubah/Hapus Barang
            elif choice == "3":
                print_inventory()
                item_query = input("\nID/Nama (gunakan koma): ").strip()
                items = find_item(item_query)
                if not items:
                    print(f"\n\033[31mBarang {item_query} tidak ditemukan\033[0m")
                    continue
                for item in items:
                    ops_edit = {
                        "1": "Ubah Harga",
                        "2": "Ubah Kondisi",
                        "3": "Ubah Stok",
                        "4": "Ubah Nama",
                        "5": "Ubah Kategori",
                        "6": "Hapus Barang"}
                    sub_choice = input_menu(f"Perubahan Data Barang {item.item_id} | {item.name}", ops_edit)

                    # Ubah harga
                    if sub_choice == "1":
                        price = input_int(f"\nHarga baru untuk {item.name}: ", min_val=1)
                        old_price = item.price
                        item.price = price
                        log_inventory("Perubahan Harga Barang", item, {"changes": {"price": [old_price, price]}})
                        print(f"\n\033[32mHarga {item.name} diperbarui dari Rp{old_price:,} ke Rp{price:,}\033[0m")

                    # Ubah kondisi
                    elif sub_choice == "2":
                        kondisi_ops = {"1": "Rusak", "2": "Hilang", "3": "Kadaluarsa"}
                        kondisi_choice = input_menu("Pilih kondisi", kondisi_ops)
                        old_status = item.status
                        item.status = kondisi_ops.get(kondisi_choice, "Pending")
                        log_inventory("Perubahan Kondisi Barang", item, {"changes": {"status": [old_status, item.status]}})
                        print(f"\n\033[32mBarang {item.name} sekarang berstatus {item.status}\033[0m")

                    # Ubah stok
                    elif sub_choice == "3":
                        stok_baru = input_int(f"Stok baru untuk {item.name}: ", min_val=0)
                        old_stok = item.confirmed_stock
                        item.confirmed_stock = stok_baru
                        log_inventory("Perubahan Stok Barang", item, {"changes": {"stok": [old_stok, stok_baru]}})
                        print(f"\n\033[32mStok {item.name} diperbarui dari {old_stok} ke {stok_baru}\033[0m")

                    # Ubah nama
                    elif sub_choice == "4":
                        new_name = input(f"\nNama baru \033[33m{item.name}\033[0m: ").strip()
                        old_name = item.name
                        item.name = new_name
                        log_inventory("Perubahan Nama Barang", item, {"changes": {"name": [old_name, new_name]}})
                        print(f"\n\033[32mNama barang {old_name} diubah menjadi {new_name}\033[0m")

                    # Ubah kategori
                    elif sub_choice == "5":
                        new_category = pilih_kategori()
                        old_category = item.category
                        item.category = new_category
                        log_inventory("Perubahan Kategori Barang", item, {"changes": {"category": [old_category, new_category]}})
                        print(f"\n\033[32mKategori barang {item.name} diubah dari {old_category} ke {new_category}\033[0m")

                    # Hapus barang
                    elif sub_choice == "6":
                        log_inventory("Penghapusan Barang", item, {"price": item.price, "reason": "Hapus Barang"}, filename="inventory_deletions.txt")
                        del store.inventory[item.item_id]
                        print(f"\n\033[32mBarang {item.name} dihapus dari gudang\033[0m")
            # Riwayat barang masuk/keluar
            elif choice == "4": riwayat_barang()
            # Minta konfirmasi siap jual
            elif choice == "5":
                print_inventory()
                item_query = input("\nID/Nama (gunakan koma): ").strip()
                items = find_item(item_query)
                if not items:
                    print(f"\n\033[31mBarang {item_query} tidak ditemukan\033[0m")
                    continue
                for item in items:
                    request = {
                        "date": datetime.now().strftime("%Y-%m-%d"),
                        "user": current_user,
                        "item_id": item.item_id,
                        "name": item.name,
                        "note": "Request konfirmasi Siap Jual"}
                    with open("inventory_requests.txt", "a") as f:
                        f.write(json.dumps(request) + "\n")
                    print(f"\n\033[33mPermintaan konfirmasi {item.name} dikirim ke Admin\033[0m")
            elif choice == "9":
                return

        # Bagian Admin
        elif current_role == "admin":
            ops = {
                "1": "Lihat Riwayat Barang Masuk/Keluar",
                "2": "Review Permintaan Konfirmasi",
                "9": "Kembali"}
            choice = input_menu("MENU INVENTARIS (Admin)", ops)
            if choice == "1":
                riwayat_barang()
            elif choice == "2":
                review_requests()
            elif choice == "9":
                return

# GUDANG (clear v.4.2.13)
def warehouse_menu():
    global current_role
    while True:
        # Karyawan gudang
        if current_role == "gudang":
            h = head("MENU GUDANG (Karyawan Gudang)")
            ops = {
                "1": "Mutasi stok",
                "2": "Konfirmasi kondisi barang",
                "3": "Konfirmasi audit jumlah barang",
                "4": "Lihat stok per gudang",
                "9": "Kembali"}
            choice = input_menu("Menu Gudang (Karyawan)", ops)
            # Mutasi stok antar gudang
            if choice == "1":
                print_inventory()
                item_query = input("\nID/Nama barang (gunakan koma): ").strip()
                items = find_item(item_query)
                if not items:
                    print("\n\033[31mBarang tidak ditemukan\033[0m")
                    continue

                from_wh = input("Gudang asal (ID): ").strip().upper()
                to_wh = input("Gudang tujuan (ID): ").strip().upper()
                qty = input_int("Jumlah transfer: ", min_val=1)

                for item in items:
                    if store.warehouses[from_wh].stock.get(item.item_id, {}).get("qty", 0) < qty:
                        print(f"\033[31mStok {item.name} di gudang asal tidak cukup\033[0m")
                    else:
                        transfer_stock(item.item_id, from_wh, to_wh, qty)
                        log_warehouse("Mutasi Stok", item.item_id, from_wh=from_wh, to_wh=to_wh, qty=qty)
                        log_employee_action(current_user, current_role, "Mutasi Stok", {"item": item.name, "from": from_wh, "to": to_wh, "qty": qty})
                        print(f"\033[32m{qty} unit {item.name} dipindahkan dari {from_wh} ke {to_wh}\033[0m")
            # Konfirmasi status fisik barang
            elif choice == "2":
                print_warehouses()
                wh_input = input("\nID/Nama Gudang: ").strip()
                warehouse = find_warehouse(wh_input)
                if not warehouse:
                    print("\033[31mGudang tidak ditemukan\033[0m")
                    continue
                wh_id = warehouse.warehouse_id

                # tampilkan stok gudang, bukan inventaris global
                print_stock_per_warehouse(wh_id)

                item_query = input("\nID/Nama barang (gunakan koma): ").strip()
                items = find_item(item_query, warehouse_id=wh_id)  # filter sesuai gudang
                if not items:
                    print("\n\033[31mBarang tidak ditemukan\033[0m")
                    continue
                if isinstance(items, InventoryItem):
                    items = [items]

                status_ops = {"1": "Baik", "2": "Rusak", "3": "Hilang", "4": "Kadaluarsa"}
                status_choice = input_menu("Konfirmasi kondisi fisik", status_ops)
                new_status = status_ops.get(status_choice, "Pending")

                for item in items:
                    old_status = store.warehouses[wh_id].stock.get(item.item_id, {}).get("status", "Pending")
                    if item.item_id in store.warehouses[wh_id].stock:
                        store.warehouses[wh_id].stock[item.item_id]["status"] = new_status
                    item.status = new_status

                    log_warehouse("Konfirmasi Status Barang", item.item_id, extra={"warehouse": wh_id, "old_status": old_status, "new_status": new_status})
                    print(f"\033[32mBarang {item.item_id} ({item.name}) di {warehouse.name} sekarang berkondisi {new_status}\033[0m")
            # Konfirmasi stok (audit jumlah)
            elif choice == "3": konfirmasi_stok_gudang()
            # Lihat stok per gudang
            elif choice == "4":
                # Tampilkan daftar gudang dulu
                print_warehouses()
                wh_input = input("\nID/Nama gudang (kosong = semua): ").strip()
                if not wh_input:
                    print_stock_per_warehouse()
                else:
                    warehouse = find_warehouse(wh_input)
                    if not warehouse:
                        print("\n\033[31mGudang tidak ditemukan\033[0m")
                    else:
                        print_stock_per_warehouse(warehouse.warehouse_id)
                pause()
            elif choice == "9":
                return
        # bagian admin
        elif current_role == "admin":
            h = head("MENU GUDANG (Admin)")
            ops = {
                "1": "Daftar gudang",
                "2": "Tambah gudang",
                "3": "Set Default Gudang",
                "4": "Lihat stok per gudang",
                "9": "Kembali"}
            choice = input_menu("Menu Gudang (Admin)", ops)
            # Daftar gudang
            if choice == "1":
                print_warehouses()
                pause()
            # Tambah gudang
            elif choice == "2":
                name = input("\nNama gudang: ").strip()
                address = input("Alamat gudang: ").strip()
                add_warehouse(name, address)
                log_warehouse("Tambah Gudang", item_id="N/A", extra={"name": name, "address": address})
                print(f"\n\033[32mGudang {name} berhasil ditambahkan\033[0m")
            # Set default gudang
            elif choice == "3":
                print_warehouses()
                wh_input = input("\nID/Nama gudang yang ingin dijadikan default: ").strip()
                warehouse = find_warehouse(wh_input)
                if not warehouse:
                    print("\033[31mGudang tidak ditemukan\033[0m")
                else:
                    store.default_warehouse = warehouse.warehouse_id
                    log_warehouse("Set Default Gudang", item_id="N/A", extra={"default": warehouse.warehouse_id})
                    print(f"\n\033[32mGudang {warehouse.name} ({warehouse.warehouse_id}) sekarang menjadi gudang default\033[0m")
            # Lihat stok per gudang
            elif choice == "4":
                print_warehouses()
                wh_input = input("\nID/Nama gudang (kosong = semua): ").strip()
                if not wh_input:
                    print_stock_per_warehouse()
                else:
                    warehouse = find_warehouse(wh_input)
                    if not warehouse:
                        print("\n\033[31mGudang tidak ditemukan\033[0m")
                    else:
                        print_stock_per_warehouse(warehouse.warehouse_id)
                pause()
            elif choice == "9":
                return

# KARYAWAN (clear v.4.1.3)
def employee_menu():
    valid_roles = ["Admin","Kasir","Service","Rental","Dapur","Gudang","Pembeli"]
    while True:
        h = head("KELOLA KARYAWAN")
        ops = {
            "1": "Lihat Karyawan",
            "2": "Tambah Karyawan",
            "3": "Ubah Jabatan",
            "4": "Hapus Karyawan",
            "5": "Cari Karyawan",
            "0": "Kembali"}
        choice = input_menu("Data Karyawan", ops)

        # Lihat Karyawan
        if choice == "1":
            print_employees()
            pause()
        # Tambah Karyawan
        elif choice == "2":
            name = input("Nama: ").strip()
            if not name:
                print("\n\033[31mNama tidak boleh kosong\033[0m")
                continue

            role = input("Jabatan (Admin/Kasir/Service/Rental/Dapur/Gudang/Pembeli): ").strip().capitalize()
            if role not in valid_roles:
                print(f"\n\033[31mRole {role} ini tidak valid. Pilih dari:\033[0m", ", ".join(valid_roles))
                continue

            address = input("Alamat: ").strip()
            phone = input("No. Telepon: ").strip()

            add_employee(name, role, address, phone)
            save_employees()
            print(f"\n\033[32mKaryawan {name} berhasil ditambahkan sebagai {role}\033[0m")

        # Ubah Jabatan
        elif choice == "3":
            print_employees()
            emp_id = input("ID karyawan: ").strip().upper()
            if emp_id not in store.employees:
                print(f"\n\033[31mKaryawwan dengan ID {emp_id} tidak ditemukan\033[0m")
                continue

            role = input("Jabatan baru: ").strip().capitalize()
            if role not in valid_roles:
                print("\033[31mRole tidak valid. Pilih dari:\033[0m", ", ".join(valid_roles))
                continue

            store.employees[emp_id].role = role
            save_employees()
            print(f"\033[32mJabatan karyawan {emp_id} diperbarui menjadi {role}\033[0m")
        # Hapus Karyawan
        elif choice == "4":
            print_employees()
            emp_id = input("ID karyawan: ").strip().upper()
            if emp_id in store.employees:
                confirm = input(f"Yakin hapus karyawan {emp_id}? (y/n): ").lower()
                if confirm == "y":
                    del store.employees[emp_id]
                    save_employees()
                    print("\\n033[32mKaryawan dihapus\033[0m")
                else:
                    print(f"\n\033[33mHapus karyawan dengan ID {emp_id} Dibatalkan\033[0m")
            else:
                print(f"\033[31mKaryawan dengan ID {emp_id} tidak ditemukan\033[0m")
        # Cari Karyawan
        elif choice == "5":
            keyword = input("\nID/Nama Karyawan: ").strip().lower()
            found = False
            print(f"{'ID (EMP)':<8} | {'Nama':<15} | {'Role':<10}")
            print("-"*35)
            for eid, emp in store.employees.items():
                if keyword in eid.lower() or keyword in emp.name.lower():
                    print(f"{eid:<8} | {emp.name:<15} | {emp.role:<10}")
                    found = True
            if not found:
                print(f"\n\033[31mKaryawan {keyword} tidak ditemukan\033[0m")
            pause()
        elif choice == "0":
            return
        
# AKUN (clear v.4.1.5)
def account_menu():
    global current_user, current_role
    if current_user not in users:
        print(f"\n\033[31mAkun '{current_user}' tidak ditemukan atau sudah dihapus\033[0m")
        current_user, current_role = None, None
        return
    while True:
        h = head("MANAJEMEN AKUN")

        if current_role == "admin":
            ops = {
                "1": "Daftar Akun",
                "2": "Tambah Akun",
                "3": "Ubah   Role",
                "4": "Hapus  Akun",
                "5": "Lihat  Profil",
                "6": "Reset  Password",
                "7": "Lupa   Password",
                "8": "Status Akun",
                "9": "Cari   Akun",
                "10": "Edit  Akun",
                "0": "Kembali"}
        else:
            ops = {"1": "Lihat Profil", "2": "Ganti Password", "0": "Kembali"}
            # status akun sbg pemberitahuan
            user_data = users.get(current_user)
            if not user_data:
                print(f"\n\033[31mAkun '{current_user}' tidak ditemukan atau sudah dihapus\033[0m")
                current_user, current_role = None, None
                return
            user_status = user_data.get("status", "Aktif")
            print(f"\n\033[34mStatus akun Anda saat ini: {user_status}\033[0m")
            if user_status == "Nonaktif":
                print("\n\033[31mAkun Anda sedang nonaktif, hubungi admin untuk mengaktifkan kembali\033[0m")
        choice = input_menu("Kelola Akun", ops)
        # akses admin
        if current_role == "admin":
            if choice == "1": list_accounts()
            elif choice == "2": add_account()
            elif choice == "3": change_role()
            elif choice == "4": delete_user()
            elif choice == "5":
                keyword = input("\nID/Nama akun: ").strip()
                if not keyword:
                    print("\n\033[31mInput tidak boleh kosong\033[0m")
                    continue
                emp_id = None
                if keyword.upper() in store.employees:
                    emp_id = keyword.upper()
                else:
                    for eid, emp in store.employees.items():
                        if emp.name.lower() == keyword.lower():
                            emp_id = eid
                            break
                if emp_id:
                    lihat_profil(emp_id, current_user, current_role)
                else:
                    print(f"\n\033[31mAkun {keyword} tidak ditemukan\033[0m")
            elif choice == "6": reset_password()
            elif choice == "7": forgot_password()
            elif choice == "8": set_account_status()
            elif choice == "9":
                keyword = input("\nUsername/nama karyawan: ").strip().lower()
                if not keyword:
                    print("\n\033[31mInput tidak boleh kosong\033[0m")
                    continue
                search_account(keyword)
            elif choice == "10":
                keyword = input("\nID/Nama akun: ").strip()
                emp_id = None
                if keyword.upper() in store.employees:
                    emp_id = keyword.upper()
                else:
                    for eid, emp in store.employees.items():
                        if emp.name.lower() == keyword.lower():
                            emp_id = eid
                            break
                if emp_id:
                    edit_profil(emp_id, current_user, current_role)
                else:
                    print("\n\033[31mKaryawan tidak ditemukan\033[0m")
            elif choice == "0": return

        # akses karyawan biasa
        else:
            if choice == "1":
                emp_id = users[current_user]["employee_id"]
                lihat_profil(emp_id, current_user, current_role)
            elif choice == "2": reset_password()  # hanya untuk akun sendiri
            elif choice == "0": return

# Penjualan (clear v.4.2.8)
def sales_menu():
    while True:
        h = head("KELOLA PENJUALAN")
        if current_role == "admin":
            ops = {
                "1": "Lihat Stok",
                "2": "Transaksi Penjualan",
                "3": "Riwayat Penjualan Barang",
                "4": "Hapus/Edit Transaksi",
                "0": "Kembali"}
        else:
            ops = {
                "1": "Lihat Stok",
                "2": "Transaksi Penjualan",
                "3": "Riwayat Penjualan Barang",
                "0": "Kembali"}
        p = input_menu("Data Penjualan Barang", ops)
        # Stok brng
        if p == "1":
            print_ready_stock()
            pause()
        # Transaksi jualan
        elif p == "2":
            transaksi_penjualan()
        # Riwayat
        elif p == "3":
            if current_role == "admin":
                print_sales_history_barang(store.sales)   
            else:
                own_sales = [s for s in store.sales if s.cashier == current_user]
                print_sales_history_barang(own_sales)
            pause()
        # Hapus/edit
        elif p == "4" and current_role == "admin": hapus_edit_transaksi()
        elif p == "0":
            return
    
# Service (clear v.4.2.8)
def service_menu():
    while True:
        h = head("KELOLA SERVICE LOKOMOTIF")
        ops = {"1": "Lihat lokomotif", "2": "Mulai service", "3": "Selesaikan service", "4": "Riwayat service", "5": "Hapus lokomotif", "0": "Kembali"}
        p = input_menu("Data Service", ops)

        # Daftar Lokomotif
        if p == "1":
            print_lokomotif()
            pause()
        # Mulai service
        elif p == "2":
            if not check_access("service"):
                return

            print_lokomotif()
            lok_id = input("ID lokomotif: ").strip().upper()
            lok = store.lokomotif.get(lok_id)
            if not lok or lok.status != "Tersedia":
                print("\033[31mLokomotif tidak tersedia\033[0m")
                continue

            customer = input("Nama customer: ").strip()
            days = input_int("Durasi (hari): ", min_val=1)

            # pilih sparepart dari inventory
            parts_used, parts_cost = pilih_sparepart()

            jasa = lok.rate_per_day * days
            total_fee = jasa + parts_cost

            start_date = datetime.now()
            end_date = start_date + timedelta(days=days)
            lok.status = "Diservis"

            record = ServiceRecord(
                lokomotif_id=lok_id,
                customer=customer,
                service_type=lok.service_type,
                days=days,
                parts_used=parts_used,
                parts_cost=parts_cost,
                total_fee=total_fee,
                start_date=start_date.strftime("%Y-%m-%d (%H:%M)"),
                end_date=end_date.strftime("%Y-%m-%d (%H:%M)"),
                officer=current_user)
            store.services.append(record)

            # catat ke file log
            log_service("Mulai Service", record)

            # integrasi ke penjualan
            sale_id = store.gen_id("SALE")
            store.sales[sale_id] = {
                "type": "service",
                "ref": record.lokomotif_id,
                "amount": total_fee,
                "date": datetime.now().strftime("%Y-%m-%d")}

            # catat aktivitas karyawan
            log_employee_action(
                current_user,
                current_role,
                "Mulai Service",
                {"lok_id": lok_id, "customer": customer, "days": days, "total_fee": total_fee})

            # tampilkan nota
            tampilkan_nota_service(record, jasa, parts_cost, total_fee)
        # Selesaikan service
        elif p == "3":
            if not check_access("service"):
                return

            if not store.services:
                print("\n\033[33mBelum ada transaksi service\033[0m")
                return

            print("\n>> Transaksi Service:")
            for idx, r in enumerate(store.services, 1):
                lok = store.lokomotif.get(r.lokomotif_id)
                status = "\033[33mDiservis\033[0m" if lok and lok.status == "Diservis" else "\033[32mTersedia/Selesai\033[0m"
                print(f"{idx}. {r.customer} | {lok.name if lok else r.lokomotif_id} | {r.days} hari | {format_rupiah(r.total_fee)} | Status: {status}")

            idx = input_int("Pilih nomor transaksi yang selesai: ", min_val=1, max_val=len(store.services))
            r = store.services[idx - 1]

            # Update status lokomotif
            if r.lokomotif_id in store.lokomotif:
                store.lokomotif[r.lokomotif_id].status = "Selesai"

            # Logging service selesai
            log_service("Selesaikan Service", r)

            # Logging aktivitas karyawan
            log_employee_action(
                current_user,
                current_role,
                "Selesaikan Service",
                {"lok_id": r.lokomotif_id, "customer": r.customer, "total_fee": r.total_fee})

            print("\n\033[32mService ditandai selesai. Status lokomotif diperbarui ke\033[0m \033[32m'Selesai'\033[0m")
        # Riwayat
        elif p == "4":
            if not store.services:
                print("\n\033[33mBelum ada service\033[0m")
            else:
                print("\n>> Riwayat Service:")
                for idx, r in enumerate(store.services, 1):
                    lok = store.lokomotif.get(r.lokomotif_id)
                    print(f"{idx}. Customer      : {r.customer}")
                    print(f"    Lokomotif     : {lok.name if lok else r.lokomotif_id}")
                    print(f"    Jenis Service : {r.service_type}")
                    print(f"    Durasi        : {r.days} hari")
                    print(f"    Tgl Mulai     : {r.start_date}")
                    print(f"    Tgl Selesai   : {r.end_date}")
                    print(f"    Total Biaya   : {format_rupiah(r.total_fee)}\n")
            pause()
        # Hapus lokomotif (hapus plate)
        elif p == "5":
            print_lokomotif()
            lok_id = input("ID lokomotif yang dihapus: ").strip().upper()
            if lok_id in store.lokomotif:
                lok = store.lokomotif[lok_id]
                if lok.status == "Diservis":
                    print("\033[31mLokomotif sedang diservis, tidak bisa dihapus\033[0m")
                    continue
                alasan_ops = {"1": "Rusak berat", "2": "Dijual", "3": "Hilang", "4": "Dokumen kadaluarsa", "5": "Lainnya"}
                alasan_choice = input_menu("Alasan penghapusan", alasan_ops)
                alasan = alasan_ops.get(alasan_choice, "Lainnya")
                note = ""
                if alasan == "Lainnya":
                    note = input("Keterangan tambahan: ").strip()
                confirm = input(f"Yakin hapus lokomotif {lok.name}? (y/n): ").lower()
                if confirm == "y":
                    record = {
                        "date": datetime.now().strftime("%Y-%m-%d (%H:%M)"),
                        "operator": current_user,
                        "lokomotif_id": lok_id,
                        "name": lok.name,
                        "service_type": lok.service_type,
                        "reason": alasan,
                        "note": note
                    }
                    with open("lokomotif_deletions.txt", "a") as f:
                        f.write(json.dumps(record) + "\n")
                    del store.lokomotif[lok_id]
                    print("\033[32mLokomotif berhasil dihapus\033[0m")
                else:
                    print("\033[33mPenghapusan dibatalkan\033[0m")
            else:
                print("\033[31mID tidak ditemukan\033[0m")
        elif p == "0":
            return

# Rental (clear v.4.2.14)
def rental_menu():
    while True:
        h = head("KELOLA RENTAL LOKOMOTIF/ALAT")

        if current_role == "admin":
            ops = {
                "1": "Lihat Lokomotif/Alat",
                "2": "Mulai Rental",
                "3": "Selesaikan Rental",
                "4": "Riwayat Rental",
                "5": "Hapus/Edit Rental",
                "0": "Kembali"}
        else:  # karyawan rental
            ops = {
                "1": "Lihat Lokomotif/Alat",
                "2": "Mulai Rental",
                "3": "Selesaikan Rental",
                "4": "Riwayat Rental",
                "0": "Kembali"}

        p = input_menu("Data Rental", ops)
        # Lihat Lokomotif/Alat
        if p == "1":
            print("\n\033[34m>> Daftar Lokomotif/Alat:\033[0m")
            if current_role == "admin":
                print(f"{'ID':<10} | {'Nama':<25} | {'Status':<15} | {'Tarif/Hari':<15}")
                print("-"*75)
                for lok in store.lokomotif.values():
                    print(f"{lok.id:<10} | {lok.name:<25} | {lok.status:<15} | {format_rupiah(lok.rate_per_day):<15}")
            else:  # karyawan tidak lihat ID
                print(f"{'Nama':<25} | {'Status':<15} | {'Tarif/Hari':<15}")
                print("-"*60)
                for lok in store.lokomotif.values():
                    print(f"{lok.name:<25} | {lok.status:<15} | {format_rupiah(lok.rate_per_day):<15}")
            pause()

        # Mulai Rental
        elif p == "2":
            print("\n\033[34m>> Daftar Lokomotif/Alat:\033[0m")
            if current_role == "admin":
                print(f"{'ID':<10} | {'Nama':<25} | {'Status':<15} | {'Tarif/Hari':<15}")
                print("-"*75)
                for lok in store.lokomotif.values():
                    print(f"{lok.id:<10} | {lok.name:<25} | {lok.status:<15} | {format_rupiah(lok.rate_per_day):<15}")
                wh_input = input("\nMasukkan ID/Nama Lokomotif/Alat: ").strip()
                # admin bisa pakai ID atau nama
                lok = store.lokomotif.get(wh_input.upper())
                if not lok:
                    # cari berdasarkan nama
                    for l in store.lokomotif.values():
                        if l.name.lower() == wh_input.lower():
                            lok = l
                            break
            else:  # karyawan
                print(f"{'Nama':<25} | {'Status':<15} | {'Tarif/Hari':<15}")
                print("-"*60)
                for lok in store.lokomotif.values():
                    print(f"{lok.name:<25} | {lok.status:<15} | {format_rupiah(lok.rate_per_day):<15}")
                wh_input = input("\nMasukkan Nama Lokomotif/Alat: ").strip()
                lok = None
                for l in store.lokomotif.values():
                    if l.name.lower() == wh_input.lower():
                        lok = l
                        break

            if not lok or lok.status != "Tersedia":
                print("\n\033[31mTidak tersedia untuk rental\033[0m")
                return

            customer = input("Nama customer: ").strip()
            days = input_int("Durasi (hari): ", min_val=1)

            total_fee = lok.rate_per_day * days
            start_date = datetime.now()
            end_date = start_date + timedelta(days=days)
            lok.status = "Disewa"

            record = RentalRecord(
                lokomotif_id=lok.id, customer=customer, days=days, total_fee=total_fee,
                start_date=start_date.strftime("%Y-%m-%d (%H:%M)"),
                end_date=end_date.strftime("%Y-%m-%d (%H:%M)"),
                officer=current_user)
            store.rentals.append(record)

            with open("rentals.txt", "a") as f:
                f.write(json.dumps(record.__dict__) + "\n")

            sale_id = store.gen_id("SALE")
            store.sales[sale_id] = {
                "type": "rental",
                "ref": lok.id,
                "amount": total_fee,
                "date": record.start_date}
            log_sale("rental", lok.id, total_fee, {"customer": customer, "days": days})
            log_employee_action(current_user, current_role, "Mulai Rental", {"lok_id": lok.id, "customer": customer, "days": days, "total_fee": total_fee, "reason": "Customer menyewa unit"})
            tampilkan_nota_rental(record)

        # Selesaikan Rental
        elif p == "3":
            if not store.rentals:
                print("\n\033[33mBelum ada transaksi rental\033[0m")
                return
            print("\n\033[34m>> Transaksi Rental Aktif:\033[0m")

            # Filter sesuai role
            if current_role == "admin":
                rentals_to_show = store.rentals
                # Header tabel untuk admin (lihat officer)
                print(f"{'No':<4} | {'Customer':<20} | {'Lokomotif':<20} | {'Durasi':<10} | {'Total':<15} | {'Officer':<12} | {'Status':<10}")
                print("-"*110)
            else:
                rentals_to_show = [r for r in store.rentals if r.officer == current_user]
                # Header tabel untuk karyawan (tanpa officer)
                print(f"{'No':<4} | {'Customer':<20} | {'Lokomotif':<20} | {'Durasi':<10} | {'Total':<15} | {'Status':<10}")
                print("-"*90)

            if not rentals_to_show:
                print("\n\033[33mTidak ada rental aktif untuk Anda\033[0m")
                return
            # Cetak daftar sesuai role
            for idx, r in enumerate(rentals_to_show, 1):
                lok = store.lokomotif.get(r.lokomotif_id)
                nama_lok = lok.name if lok else r.lokomotif_id
                status = "\033[33mDisewa\033[0m" if lok and lok.status == "Disewa" else "\033[32mSelesai\033[0m"

                if current_role == "admin":
                    print(f"{idx:<4} | {r.customer:<20} | {nama_lok:<20} | {str(r.days)+' hari':<10} | {format_rupiah(r.total_fee):<15} | {r.officer:<12} | {status:<10}")
                else:
                    print(f"{idx:<4} | {r.customer:<20} | {nama_lok:<20} | {str(r.days)+' hari':<10} | {format_rupiah(r.total_fee):<15} | {status:<10}")

            idx_choice = input_int("Pilih nomor transaksi yang selesai (0=keluar): ", min_val=0)
            if idx_choice == 0:
                return
            if idx_choice > len(rentals_to_show):
                print("\n\033[31mNomor tidak valid\033[0m")
                return

            r = rentals_to_show[idx_choice - 1]

            # Update status lokomotif → lebih natural ke "Tersedia"
            if r.lokomotif_id in store.lokomotif:
                store.lokomotif[r.lokomotif_id].status = "Tersedia"

            log_sale("rental selesai", r.lokomotif_id, r.total_fee, {"customer": r.customer})
            log_employee_action(current_user, current_role, "Selesaikan Rental", {"lok_id": r.lokomotif_id, "customer": r.customer, "reason": "Rental selesai sesuai durasi"})

            print("\n\033[32mRental ditandai selesai. Status lokomotif diperbarui ke 'Tersedia'\033[0m")
            tampilkan_nota_rental(r)
        
        # Riwayat
        elif p == "4":
            if current_role == "admin":
                print("\n\033[34m>> Riwayat Rental\033[0m")
                if not store.rentals:
                    print("\n\033[33m- KOSONG -\033[0m")
                    return
                # Header tabel
                print(f"{'No':<4} | {'Customer':<20} | {'Lokomotif':<20} | {'Durasi':<10} | {'Total':<15} | {'Officer':<12} | {'Status':<10}")
                print("-"*105)
                # Isi tabel
                for idx, r in enumerate(store.rentals, 1):
                    lok = store.lokomotif.get(r.lokomotif_id)
                    nama_lok = lok.name if lok else r.lokomotif_id
                    status = "\033[33mDisewa\033[0m" if lok and lok.status == "Disewa" else "\033[32mSelesai\033[0m"
                    print(f"{idx:<4} | {r.customer:<20} | {nama_lok:<20} | {str(r.days)+' hari':<10} | "
                        f"{format_rupiah(r.total_fee):<15} | {r.officer:<12} | {status:<10}")
            else:  # Karyawan rental
                print("\n\033[34m>> Riwayat Rental (Anda)\033[0m")
                rentals_user = [r for r in store.rentals if r.officer == current_user]

                if not rentals_user:
                    print("\n\033[33mBelum ada rental oleh Anda\033[0m")
                    return
                # Header tabel 
                print(f"{'No':<4} | {'Customer':<20} | {'Lokomotif':<20} | {'Durasi':<10} | {'Total':<15} | {'Status':<10}")
                print("-"*90)
                # Isi
                for idx, r in enumerate(rentals_user, 1):
                    lok = store.lokomotif.get(r.lokomotif_id)
                    nama_lok = lok.name if lok else r.lokomotif_id
                    status = "\033[33mDisewa\033[0m" if lok and lok.status == "Disewa" else "\033[32mSelesai\033[0m"
                    print(f"{idx:<4} | {r.customer:<20} | {nama_lok:<20} | {str(r.days)+' hari':<10} | "
                        f"{format_rupiah(r.total_fee):<15} | {status:<10}")

        # Hapus/Edit Rental (khusus admin)
        elif p == "5" and current_role == "admin":
            hapus_edit_rental()
        elif p == "0":
            return

# Pesan Makan (clear v.4.2.14)
def food_menu():
    while True:
        h = head("KELOLA PEMESANAN MAKANAN")
        if current_role in ["admin", "dapur"]:
            ops = {
                "1": "Lihat menu",
                "2": "Tambah menu",
                "3": "Buat pesanan",
                "4": "Riwayat Pesanan Makanan",
                "5": "Hapus menu",
                "0": "Kembali"}
        elif current_role == "pembeli":
            ops = {
                "1": "Lihat menu",
                "2": "Buat pesanan",
                "3": "Riwayat Pesanan Makanan",
                "0": "Kembali"}
        else:
            print("\n\033[31mRole tidak berhak mengakses modul makanan\033[0m")
            return

        p = input_menu("Data Pesan Makanan", ops)

        # Lihat menu
        if p == "1":
            if current_role == "pembeli":
                print_menu_items(hide_id=True)   # pembeli tanpa ID
            else:
                print_menu_items()               # admin/dapur dengan ID
            pause()

        # Tambah menu (khusus admin/dapur)
        elif p == "2" and current_role in ["admin", "dapur"]: tambah_makanan()

        # Buat pesanan (pembeli/admin/dapur)
        elif (p == "2" and current_role == "pembeli") or (p == "3" and current_role in ["admin","dapur"]):
            if not check_access("pembeli") and not check_access("dapur"):
                return

            customer_name = input("\nNama customer: ").strip()
            table_number = input("Nomor meja: ").strip()
            cart: List[Tuple[str, int]] = []

            # tampilkan menu sesuai role
            if current_role == "pembeli":
                print_menu_items(hide_id=True)
            else:
                print_menu_items()

            print("\n\033[33mFormat input: NamaMenu (jumlah), pisahkan dengan koma\033[0m")
            print("\033[33mContoh: Nasi Goreng (4), Es Teh Manis (2)\033[0m")

            pesanan = input("\nPesanan: ").strip()
            if pesanan == "":
                print("\n\033[33mKeranjang kosong\033[0m \033[47mBatal\033[0m")
                return

            # parsing input pesanan
            for item_str in pesanan.split(","):
                item_str = item_str.strip()
                if "(" in item_str and ")" in item_str:
                    nama = item_str[:item_str.index("(")].strip()
                    try:
                        qty = int(item_str[item_str.index("(")+1:item_str.index(")")].strip())
                    except ValueError:
                        print(f"\033[31mJumlah tidak valid untuk {nama}\033[0m")
                        continue
                else:
                    print(f"\033[31mFormat salah: {item_str}\033[0m")
                    continue

                # cari menu berdasarkan nama
                found = None
                for mid, item in store.menu.items():
                    if item.name.lower() == nama.lower():
                        found = mid
                        break
                if not found:
                    print(f"\033[31mMenu '{nama}' tidak ditemukan\033[0m")
                    continue

                if qty > store.menu[found].stock:
                    print(f"\033[33mStok {nama} tidak cukup\033[0m")
                    continue

                store.menu[found].stock -= qty
                cart.append((found, qty))

            if not cart:
                print("\n\033[33mKeranjang kosong\033[0m \033[47mBatal\033[0m")
                return
            # Proses pembayaran makanan → catat ke food_orders
            proses_pembayaran_makanan(customer_name, table_number, cart)

        # Riwayat pesanan makanan
        elif (p == "3" and current_role == "pembeli") or (p == "4" and current_role in ["admin","dapur"]):
            if not store.food_orders:
                print("\n\033[33mBelum ada pesanan\033[0m")
            else:
                print("\n\033[34m>> RIWAYAT PESANAN MAKANAN:\033[0m\n")
                # Header tabel
                print(f"{'No':<4} | {'Tanggal':<20} | {'Waiter':<12} | {'Customer':<20} | {'Detail Pesanan':<40} | {'Total':<15}")
                print("-"*120)

                # Isi tabel
                for idx, o in enumerate(store.food_orders, 1):
                    detail = []
                    for mid, qty in o.items:
                        menu_item = store.menu.get(mid)
                        nm = menu_item.name if menu_item else f"[UNKNOWN:{mid}]"
                        detail.append(f"{nm} x{qty}")
                    detail_str = "; ".join(detail)

                    print(f"{idx:<4} | {o.date:<20} | {o.waiter:<12} | {o.customer_name:<20} | {detail_str:<40} | {format_rupiah(o.total):<15}")
            pause()

        # Hapus menu (khusus admin/dapur)
        elif p == "5" and current_role in ["admin", "dapur"]:
            print_menu_items()
            pilihan = input("\nID/Nama menu: ").strip()
            # Cari menu berdasarkan ID
            if pilihan.upper() in store.menu:
                menu_id = pilihan.upper()
            else:
                # Cari menu berdasarkan nama
                found = None
                for mid, item in store.menu.items():
                    if item.name.lower() == pilihan.lower():
                        found = mid
                        break
                if not found:
                    print(f"\033[31mMenu '{pilihan}' tidak ditemukan\033[0m")
                    continue
                menu_id = found

            # Alasan penghapusan
            alasan_ops = {"1": "Kadaluarsa", "2": "Habis", "3": "Discontinue", "4": "Resep berubah", "5": "Lainnya"}
            alasan_choice = input_menu("Alasan penghapusan", alasan_ops)
            alasan = alasan_ops.get(alasan_choice, "Lainnya")
            note = ""
            if alasan == "Lainnya":
                note = input("Keterangan tambahan: ").strip()

            confirm = input(f"\nYakin hapus menu {store.menu[menu_id].name}? (y/n): ").lower()
            if confirm == "y":
                record = {
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "operator": current_user,
                    "menu_id": menu_id,
                    "name": store.menu[menu_id].name,
                    "stock": store.menu[menu_id].stock,
                    "price": store.menu[menu_id].price,
                    "reason": alasan,
                    "note": note}
                with open("menu_deletions.txt", "a") as f:
                    f.write(json.dumps(record) + "\n")
                del store.menu[menu_id]
                print("\n\033[32mMenu berhasil dihapus\033[0m")
            else:
                print("\n\033[33mPenghapusan dibatalkan\033[0m")
        elif p == "0":
            return

# >> Main Menu 
def main_menu():
    global current_user, current_role
    while True:
        if not current_user or not current_role:  # Session safety
            print("\n\033[31mSession tidak valid. Silakan login kembali\033[0m")
            return

        if current_role == "admin":
            ops = {
                "1": "Manajemen Inventaris",
                "2": "Manajemen Karyawan",
                "3": "Manajemen Akun",
                "4": "Manajemen Gudang",
                "5": "Manajemen Rental & Servis",
                "6": "Manajemen Pesan makanan",
                "7": "Manajemen Penjualan",
                "8": "Dashboard Gabungan",
                "9": "Dashboard Admin",
                "0": "Keluar"}
            choice = input_menu("MENU UTAMA (Admin)", ops)

            if choice == "1": inventory_menu()
            elif choice == "2": employee_menu()
            elif choice == "3": account_menu()
            elif choice == "4": warehouse_menu()
            elif choice == "5": rental_service_menu()
            elif choice == "6": food_menu()
            elif choice == "7": sales_menu()
            elif choice == "8": dashboard()
            elif choice == "9": dashboard_admin()
            elif choice == "0":
                logout()
                return

        elif current_role == "kasir":
            ops = {
                "1": "Manajemen Penjualan",
                "2": "Dasbor Role Penjualan",
                "3": "Kelola Akun anda",
                "9": "Logout"}
            choice = input_menu("MENU UTAMA (Kasir)", ops)

            if choice == "1": sales_menu()
            elif choice == "2": dashboard_kasir()
            elif choice == "3": account_menu()
            elif choice == "9": 
                logout()
                return
            elif choice == "0": sys.exit(0)

        elif current_role == "service":
            ops = {
                "1": "Manajemen Servis",
                "2": "Dasbor Role Servis",
                "3": "Kelola Akun anda",
                "9": "Logout"}
            choice = input_menu("MENU UTAMA (Servis)", ops)

            if choice == "1": service_menu()
            elif choice == "2": dashboard_service()
            elif choice == "3": account_menu()
            elif choice == "9": 
                logout()
                return
            elif choice == "0": sys.exit(0)

        elif current_role == "rental":
            ops = {
                "1": "Manajemen Rental",
                "2": "Dasbor Role Rental",
                "3": "Kelola Akun anda",
                "9": "Logout"}
            choice = input_menu("MENU UTAMA (Rental)", ops)

            if choice == "1": rental_menu()
            elif choice == "2": dashboard_rental()
            elif choice == "3": account_menu()
            elif choice == "9": 
                logout()
                return
            elif choice == "0": sys.exit(0)

        elif current_role == "dapur":
            ops = {
                "1": "Manajemen Pemesanan makanan",
                "2": "Dasbor Role Dapur",
                "3": "Kelola Akun anda",
                "9": "Logout"}
            choice = input_menu("MENU UTAMA (Dapur)", ops)

            if choice == "1": food_menu()
            elif choice == "2": dashboard_dapur()
            elif choice == "3": account_menu()
            elif choice == "9": 
                logout()
                return
            elif choice == "0": sys.exit(0)

        elif current_role == "gudang":
            ops = {
                "1": "Manajemen Inventaris",
                "2": "Manajemen Gudang",
                "3": "Dasbor Role Gudang",
                "4": "Kelola Akun anda",
                "9": "Logout"}
            choice = input_menu("MENU UTAMA (Gudang)", ops)

            if choice == "1": inventory_menu()
            elif choice == "2": warehouse_menu()
            elif choice == "3": dashboard_gudang()
            elif choice == "4": account_menu()
            elif choice == "9": 
                logout()
                return
            elif choice == "0": sys.exit(0)

        elif current_role == "pembeli":
            ops = {
                "1": "Lihat Menu Makanan",
                "2": "Pesan Makanan",
                "3": "Lihat Pesanan",
                "9": "Logout"}
            choice = input_menu("MENU UTAMA (Pembeli)", ops)

            if choice == "1": print_menu_items()
            elif choice == "2": food_menu()
            elif choice == "3":
                if not store.food_orders:
                    print("\n\033[33mBelum ada pesanan\033[0m")
                else:
                    print("\n>> Riwayat Pesanan:")
                    for idx, o in enumerate(store.food_orders, 1):
                        detail = [f"{store.menu[mid].name} x{qty}" for mid, qty in o.items]
                        print(f"{idx}. {o.date} | {o.waiter} | {'; '.join(detail)} | Total: {format_rupiah(o.total)}")
                pause()
            elif choice == "9":
                logout()
                return
            elif choice == "0": sys.exit(0)

# >> Start Menu
def start_menu():
    global current_user, current_role
    while True:
        head("SELAMAT DATANG DI APLIKASI AMOT")
        ops = {"1": "Registrasi", "2": "Login", "0": "Keluar"}
        choice = input_menu("LOGIN KE AKUN ANDA", ops)
        if choice == "1":
            register()
        elif choice == "2":
            current_user, current_role = None, None  # reset sebelum login baru
            login()
            if current_user:   # login sukses
                return True    # keluar start_menu, lanjut ke main
        elif choice == "0":
            print("\n\033[32mTerima kasih sudah menggunakan sistem ini\033[0m")
            sys.exit(0)

# >> Main
def main():
    try:
        seed_data()   # isi data awal

        while True:   # loop terus
            if start_menu():   # login sukses
                load_sales()
                load_services()
                load_food_orders()
                main_menu()    # tampilkan menu sesuai role
                # setelah logout, main_menu() return → loop balik ke start_menu()
    except KeyboardInterrupt:
        print("\n\033[41m Program dihentikan oleh user \033[0m")
        sys.exit(0)

''' ENTRY POINT '''
if __name__ == "__main__":
    main()

# NOte
"""
# utk pw
import hashlib
def hash_pw(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest() # ubah text jadi hash(ADMIN123)
# yg dimodif
1. register() --> users[username] = {"password": hash_pw(password), "role": role}
2. login() --> if u in users and users[u]["password"] == hash_pw(p):
                current_user = u
                current_role = users[u]["role"]

# utk auto logout (main_menu)
if time.time() - last_action > 300:  # 5 menit idle
    print("\n\033[31mSession berakhir karena idle\033[0m")
    current_user, current_role = None, None
    return                

# utk stok
def sync_inventory_stock():
    # Sinkronisasi stok inventaris dengan total stok fisik gudang (untuk audit), bukan untuk stok siap jual.
    for item_id, item in store.inventory.items():
        item.total_physical_stock = sum(
            wh.stock.get(item_id, {}).get("qty", 0)
            for wh in store.warehouses.values())

"""