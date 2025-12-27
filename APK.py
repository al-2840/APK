"""
Aplikasi       : APLIKASI MANAJEMEN OPERASIONAL TERPADU (AMOT) - Versi 4.0 (target max fix, MAJOR.MINOR.PATCH)
Fitur          : Mengelola inventaris, karyawan, penjualan, service mobil, dan pemesanan makanan, semuanya terintegrasi dengan laporan ringkas di dashboard.
Penulis        : 2840 & 2835
Versi (update) : 3.7
"""
import sys, time, ast, json
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Tuple

''' DATA LAYER '''
# Data (10 item per module)
def seed_data():
    # Gudang
    add_warehouse("Pusat", "Jl. Malang No.1", silent=True)
    add_warehouse("Cabang 1", "Jl. Ahmad Yani No.25", silent=True)
    add_warehouse("Cabang 2", "Jl. Cempaka No.15", silent=True)

    # Inventaris dengan stok awal
    add_inventory("Oli Mesin", 75000, "1", stok_awal=10, silent=True)
    add_inventory("Filter Udara", 120000, "1", stok_awal=5, silent=True)
    add_inventory("Ban Lokomotif", 1500000, "1", stok_awal=2, silent=True)
    add_inventory("Kampas Rem", 250000, "1", stok_awal=8, silent=True)
    add_inventory("Busi", 35000, "1", stok_awal=20, silent=True)
    add_inventory("Cat Body Merah", 200000, "2", stok_awal=3, silent=True)
    add_inventory("Cat Body Biru", 200000, "2", stok_awal=4, silent=True)
    add_inventory("Toolkit Mekanik", 500000, "2", stok_awal=6, silent=True)
    add_inventory("Dongkrak Hidrolik", 1250000, "2", stok_awal=1, silent=True)
    add_inventory("Solar", 10000, "3", stok_awal=100, silent=True)

    # Karyawan
    add_employee("Andi", "Kasir", silent=True)
    add_employee("Budi", "Service", silent=True)
    add_employee("Citra", "Dapur", silent=True)
    add_employee("Dewi", "Admin", silent=True)
    add_employee("Eko", "Gudang", silent=True)
    add_employee("Fajar", "Kasir", silent=True)
    add_employee("Gina", "Service", silent=True)
    add_employee("Hadi", "Dapur", silent=True)
    add_employee("Indra", "Admin", silent=True)
    add_employee("Joko", "Gudang", silent=True)

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

    # Menu
    add_menu("Nasi Goreng", 20, 25000, silent=True)
    add_menu("Mie Ayam", 25, 20000, silent=True)
    add_menu("Soto Banjar", 15, 30000, silent=True)
    add_menu("Ayam Bakar", 20, 35000, silent=True)
    add_menu("Ikan Bakar", 15, 40000, silent=True)
    add_menu("Es Teh Manis", 50, 5000, silent=True)
    add_menu("Es Jeruk", 40, 8000, silent=True)
    add_menu("Kopi Hitam", 30, 10000, silent=True)
    add_menu("Teh Tarik", 25, 12000, silent=True)
    add_menu("Jus Alpukat", 20, 15000, silent=True)
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
    username = input("Username yang dihapus: ").strip()
    if username in users:
        confirm = input(f"\n\033[33mYakin ingin menghapus akun '\033[32m{username}\033[33m'? (y/n):\033[0m ").strip().lower() # f: prefiks agar {} ter render
        if confirm == "y":
            del users[username]
            save_users()
            print(f"\n\033[32mAkun '{username}' berhasil dihapus\033[0m")
            if current_user == username:
                current_user, current_role = None, None
                print("\n\033[31mAnda telah logout karena akun dihapus\033[0m")
        else:
            print("\n\033[33mPenghapusan dibatalkan\033[0m")
    else:
        print("\n\033[33mUsername tidak ditemukan\033[0m")

''' HELPERS '''
KATEGORI_LIST = {"1": "Suku Cadang", "2": "Peralatan", "3": "Bahan Bakar"}
def pilih_kategori(prompt="Pilih kategori (1-3): "):
    while True:
        print("\n\033[34m>>> PILIH KATEGORI\033[0m")
        for key, value in KATEGORI_LIST.items():
            print(f"{key}. {value}")

        pilih = input(prompt).strip()
        if pilih in KATEGORI_LIST:
            return pilih   # return kode kategori ("1", "2", "3")
        print("\n\033[31mPilihan kategori tidak valid\033[0m")

# format duit
def format_rupiah(n: int) -> str:
    s = f" {n:,}".replace(",", ".")
    return f"Rp {s}" 
# Pencarian ID/Nama
def find_item(query: str):
    query = query.strip().upper()
    # Cari berdasarkan ID
    if query in store.inventory:
        return store.inventory[query]
    # Cari berdasarkan nama
    for it in store.inventory.values():
        if it.name.upper() == query:
            return it
    return None
# sorting pergudang
def inventory_per_gudang():
    print("\n\033[34m>> INVENTARIS PER GUDANG:\033[0m")
    for wh in store.warehouses.values():
        print(f"\nGudang {wh.warehouse_id} | {wh.name} | Alamat: {wh.address}")
        print("-" * 50)
        found = False
        for item in sorted(store.inventory.values(), key=lambda x: x.name):
            qty = item.stock_by_warehouse.get(wh.warehouse_id, 0)
            if qty > 0:
                found = True
                print(f"{item.item_id} | {item.name} | Stok: {qty} unit | Harga Beli: {format_rupiah(item.price)} | Kondisi: {item.status}")
        if not found:
            print("\033[33mTidak ada stok barang di gudang ini\033[0m")
# UI Header
def head(prompt):
    print(f"\n\033[44m {prompt} \033[0m")
    print_line()
# UI line
def print_line():
    print("\033[34m" + "="*40 + "\033[0m")
# Menu input 
def input_menu(title: str, options: dict):
    while True:
        print(f"\n\033[34m\033[4m ===> {title} ֍ \033[0m\033[0m")
        for key, desc in options.items():
            print(f"{key}. {desc}")
        val = input("Pilih: ").strip()
        if val in options:
            return val
        print(f"\033[31m Pilihan tidak valid. Pilih {', '.join(options.keys())} \033[0m")
# Validasi input angka
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
# Pause (animasi loading)
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
# inventaris per gudang
def print_inventory_by_category():
    print("\n\033[34m>>> INVENTARIS PER KATEGORI\033[0m")
    for code, cat in KATEGORI_LIST.items():
        print(f"\nKategori {code} - {cat}")
        print("-" * 50)
        found = False
        for it in store.inventory.values():
            if it.category == code:   # simpan kategori sebagai kode
                found = True
                print(f"{it.item_id} | {it.name} | Harga: Rp {it.price:,} | Kondisi: {it.status} | Stok Aman: {it.confirmed_stock}")
        if not found:
            print("\033[33mTidak ada barang di kategori ini\033[0m")
# Chek per role akses
def check_access(required_role):
    if current_role != required_role:
        print(f"\033[31mAkses ditolak: hanya {required_role} yang bisa menjalankan menu ini\033[0m")
        return False
    return True
# pencatatan aktivitas karyawan
def log_employee_action(user, role, action, extra=None, filename="employee_log.txt"):
    record = {
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "user": user,
        "role": role,
        "action": action}
    if extra:
        record.update(extra)
    with open(filename, "a") as f:
        f.write(json.dumps(record) + "\n")
# pencatatan inventaris
def log_inventory(action, item, extra=None, filename="inventory_log.txt"):
    record = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "user": current_user,
        "item_id": item.item_id,
        "name": item.name,
        "action": action}
    if extra:
        record.update(extra)
    with open(filename, "a") as f:
        f.write(json.dumps(record) + "\n")
# pencatatan gudang
def log_warehouse(action, item_id, from_wh=None, to_wh=None, qty=None, extra=None, filename="warehouse_log.txt"):
    record = {
        "date": datetime.now().strftime("%Y-%m-%d"),
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
# Pencatatan servis
def log_service(action, record, filename="services.txt"):
    data = {
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "user": current_user,
        "action": action,
        **record.__dict__
    }
    with open(filename, "a") as f:
        f.write(json.dumps(data) + "\n")
# pencatatan penjualan
def log_sale(sale_type, ref_id, amount, extra=None, filename="sales.txt"):
    record = {
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "user": current_user,
        "role": current_role,
        "type": sale_type,
        "ref": ref_id,
        "amount": amount
    }
    if extra:
        record.update(extra)
    with open(filename, "a") as f:
        f.write(json.dumps(record) + "\n")
# inventaris
def print_inventory():
    print("\n\033[34m>> INVENTARIS BARANG:\033[0m")
    if not store.inventory:
        print("\033[31m- KOSONG -\033[0m")
        return
    for it in store.inventory.values():
        # Warna kondisi
        if it.status in ["Rusak", "Hilang"]:
            status_ui = f"\033[31m{it.status}\033[0m"
        elif it.status == "Pending":
            status_ui = f"\033[33m{it.status}\033[0m"
        elif it.status == "Siap Jual":
            status_ui = f"\033[32m{it.status}\033[0m"
        else:
            status_ui = it.status

        print(f"- {it.item_id} | {it.name} | Jumlah Unit: {it.confirmed_stock} | Harga Beli: {format_rupiah(it.price)} | Kategori: {it.category} | Kondisi: {status_ui}")
# Review Permintaan (to Admin)
def review_requests():
    print("\n\033[34m>>> REVIEW PERMINTAAN KONFIRMASI\033[0m")
    try:
        with open("inventory_requests.txt", "r") as f:
            lines = f.readlines()
        if not lines:
            print("\033[33mTidak ada permintaan konfirmasi\033[0m")
            return
        for idx, line in enumerate(lines, 1):
            req = json.loads(line)
            print(f"{idx}. {req['date']} | User: {req['user']} | Barang: {req['name']} ({req['item_id']})")
        idx_choice = input_int("Pilih nomor untuk approve (0=keluar): ", min_val=0)
        if idx_choice == 0: return
        req = json.loads(lines[idx_choice-1])
        item = store.inventory.get(req['item_id'])
        if item and item.confirmed_stock > 0 and item.price > 0:
            item.status = "Siap Jual"
            print(f"\033[32mBarang {item.name} dikonfirmasi SIAP JUAL oleh Admin\033[0m")
        else:
            print(f"\033[31mBarang {req['name']} tidak valid (stok/harga belum ada)\033[0m")
    except FileNotFoundError:
        print("\033[33mBelum ada file permintaan\033[0m")
# Riwayat 
def riwayat_barang():
    print("\n\033[34m>>> LIHAT RIWAYAT BARANG\033[0m")
    ops = {
        "1": "Semua Riwayat",
        "2": "Filter berdasarkan Tanggal",
        "3": "Filter berdasarkan Kategori"
    }
    choice = input_menu("Opsi Riwayat", ops)

    if choice == "1":
        tampilkan_riwayat()
    elif choice == "2":
        tanggal = input("Masukkan tanggal (YYYY-MM-DD): ").strip()
        tampilkan_riwayat(filter_date=tanggal)
    elif choice == "3":
        category_code = pilih_kategori()
        tampilkan_riwayat(filter_category=category_code)
# barang masuk/keluar
def tampilkan_riwayat(filter_date=None, filter_category=None):
    print("\n\033[34m>> Riwayat Barang Masuk\033[0m")
    try:
        with open("inventory_log.txt", "r") as f:
            for line in f:
                rec = json.loads(line)
                if filter_date and rec["date"] != filter_date:
                    continue
                if filter_category and rec["kategori"] != filter_category:
                    continue
                print(f"{rec['date']} | {rec['name']} | Jumlah: {rec['jumlah']} | Harga: {rec['harga']} | Kategori: {rec['kategori']}")
    except FileNotFoundError:
        print("\033[33mBelum ada riwayat barang masuk\033[0m")

    print("\n\033[34m>> Riwayat Barang Dihapus\033[0m")
    try:
        with open("inventory_deletions.txt", "r") as f:
            for line in f:
                rec = json.loads(line)
                if filter_date and rec["date"] != filter_date:
                    continue
                if filter_category and rec["kategori"] != KATEGORI_LIST.get(filter_category, filter_category):
                    continue
                print(f"{rec['date']} | {rec['name']} | Harga: {rec['price']} | Reason: {rec['reason']}")
    except FileNotFoundError:
        print("\033[33mBelum ada riwayat barang dihapus\033[0m")
# karyawan
def print_employees():
    print("\n\033[34m>> KARYAWAN:\033[0m")
    if not store.employees:
        print("\033[31m- KOSONG -\033[0m")
        return
    for emp in store.employees.values():
        print(f"- {emp.id} | {emp.name} | Jabatan: {emp.role}")
# service
def print_lokomotif():
    print("\n\033[34m>> LOKOMOTIF / UNIT SERVICE:\033[0m")
    if not store.lokomotif:
        print("\033[31m- KOSONG -\033[0m")
        return
    for lok in store.lokomotif.values():
        status_color = "\033[32mTersedia\033[0m" if lok.status == "Tersedia" else ("\033[33mDiservis\033[0m" if lok.status == "Diservis" else "\033[36mSelesai\033[0m")
        print(f"- {lok.id} | {lok.name} | Jenis: {lok.service_type} | Tarif/Hari: {format_rupiah(lok.rate_per_day)} | Status: {status_color}")
# pesan makanan
def print_menu_items():
    print("\n\033[34m>> MENU MAKANAN:\033[0m ")
    if not store.menu:
        print("\033[31m- KOSONG -\033[0m")
        return
    for m in store.menu.values():
        print(f"- {m.id} | {m.name} | Harga: {format_rupiah(m.price)} | Stok: {m.stock}")
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
            print("\033[31mID tidak ditemukan\033[0m")
            continue
        qty = input_int("Jumlah: ", min_val=1)
        if qty > store.inventory[part_id].stock:
            print("\033[31mStok tidak cukup\033[0m")
            continue
        # kurangi stok
        store.inventory[part_id].stock -= qty
        parts_used.append(f"{store.inventory[part_id].name} x{qty}")
        parts_cost += store.inventory[part_id].price * qty
    return parts_used, parts_cost
# Nota servis
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
# Nota makann
def tampilkan_nota_makanan(order, store):
    print("\n\033[30m=== NOTA PEMBELIAN MAKANAN PT.AMOT \033[0m")
    print(f"Customer      : {order.customer_name}")
    print(f"Meja          : {order.table_number}")
    print(f"Waiter        : {order.waiter}")
    print(f"Tanggal Pesan : {order.date}")

    # detail pesanan
    detail = [f"{store.menu[mid].name} x{q}" for mid, q in order.items]
    print(f"Pesanan       : {'; '.join(detail)}")
    print(f"Total Biaya   : {format_rupiah(order.total)}")
# Nota rental
def tampilkan_nota_rental(record):
    print("\n\033[30m=== NOTA RENTAL PT.AMOT \033[0m")
    print(f"Customer      : {record.customer}")
    print(f"Lokomotif     : {record.lokomotif_id}")
    print(f"Durasi        : {record.days} hari")
    print(f"Tgl Mulai     : {record.start_date}")
    print(f"Tgl Selesai   : {record.end_date}")
    print(f"Total Biaya   : {format_rupiah(record.total_fee)}")
    print(f"Officer       : {record.officer}")
# Tambahan validasi input agar tidak crash
def safe_input(prompt: str) -> str:
    try:
        return input(prompt).strip()
    except (EOFError, KeyboardInterrupt):
        print("\n\033[31m Input dibatalkan \033[0m")
        return ""
# Refactor dashboard UV.3.3
def top_items(counter: dict, label: str, unit: str = ""):
    """Cetak daftar item terlaris dari counter dict"""
    if counter:
        print(f"\n\033[4m>> {label}:\033[0m")
        for nm, qty in sorted(counter.items(), key=lambda x: x[1], reverse=True):
            print(f"- {nm}: {qty} {unit}")
    else:
        print(f"\n\033[33mBelum ada data {label.lower()}\033[0m")
# Update stok
def adjust_stock(item_id: str, warehouse_id: str, delta: int, silent=False):
    # Validasi item dan gudang
    if item_id not in store.inventory:
        if not silent:
            print("\033[31mItem tidak ditemukan\033[0m")
        return
    if warehouse_id not in store.warehouses:
        if not silent:
            print("\033[31mGudang tidak ditemukan\033[0m")
        return

    item = store.inventory[item_id]
    current = item.stock_by_warehouse.get(warehouse_id, 0)
    new_stock = current + delta

    # Validasi stok tidak boleh negatif
    if new_stock < 0:
        if not silent:
            print(f"\033[31mStok {item.name} di {store.warehouses[warehouse_id].name} tidak cukup (tersedia {current})\033[0m")
        return

    # Update stok fisik di gudang
    item.stock_by_warehouse[warehouse_id] = new_stock

    if not silent:
        wh_name = store.warehouses[warehouse_id].name
        print(f"\033[32mStok {item.name} di {wh_name} sekarang {new_stock}\033[0m")
# Mutasi antar gudang
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

    # Lakukan mutasi stok
    item.stock_by_warehouse[from_wh] = current_stock - qty
    item.stock_by_warehouse[to_wh] = item.stock_by_warehouse.get(to_wh, 0) + qty

    # Catat log mutasi
    log_warehouse(
        "Mutasi Stok",
        item_id,
        from_wh=from_wh,
        to_wh=to_wh,
        qty=qty)

    print(f"\033[32mTransfer {qty} unit {item.name} dari {store.warehouses[from_wh].name} ke {store.warehouses[to_wh].name}\033[0m")
'---------------------------------------------------------------------------------------------------------- part 1 -------------------------------------------'

''' MODELS '''
@dataclass
class Employee:
    id: str
    name: str
    role: str
@dataclass
class Lokomotif:
    id: str
    name: str
    service_type: str      # contoh: "Perbaikan Mesin", "Overhaul", "Pengecatan"
    rate_per_day: int      # biaya service per hari
    status: str = "Tersedia"   # "Tersedia", "Diservis", "Selesai"
@dataclass
class MenuItem:
    id: str
    name: str
    price: int
    stock: int
@dataclass 
class Sale:
    items: List[Tuple[str, int]]
    total: int
    date: str
    cashier: str
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
class RentalRecord:
    lokomotif_id: str
    customer: str
    days: int
    total_fee: int
    start_date: str
    end_date: str
    officer: str
    status: str = "Berjalan" # default saat mulai rental
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
class Store:
    def __init__(self):
        self.inventory: Dict[str, InventoryItem] = {}
        self.employees: Dict[str, Employee] = {}
        self.lokomotif: Dict[str, Lokomotif] = {}
        self.menu: Dict[str, MenuItem] = {}
        self.sales: List[Sale] = []
        self.services: List[ServiceRecord] = []
        self.food_orders: List[FoodOrder] = []
        self.warehouses: Dict[str, Warehouse] = {}
        self.counters = {"INV": 0, "EMP": 0, "LOK": 0, "MEN": 0}

    def gen_id(self, prefix: str) -> str:
        self.counters[prefix] += 1
        return f"{prefix}{self.counters[prefix]:04d}"
store = Store()
'---------------------------------------------------------------------------------------------------------- part 2 -------------------------------------------'

''' USER MANAGEMENT '''
current_user = None
current_role = None

# Load & Save Users
def load_users():
    try:
        with open("users.json", "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_users():
    with open("users.json", "w") as f:
        json.dump(users, f, indent=2)

# Inisialisasi users
users = load_users()

# Tambahkan default admin jika belum ada
if "admin" not in users:
    # admin default terhubung ke employee Dewi (misalnya EMP0004 dari seed_data)
    emp_id = "EMP0004"
    users["admin"] = {"password": "123", "employee_id": emp_id}
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
    role_ops = {"1": "admin","2": "kasir","3": "service","4": "dapur","5": "pembeli","6": "gudang"}
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

    # Buat employee baru
    emp_id = store.gen_id("EMP")
    store.employees[emp_id] = Employee(emp_id, username.capitalize(), role)

    # Simpan user dengan employee_id
    users[username] = {"password": password, "employee_id": emp_id}
    save_users()

    print(f"\n\033[32mRegistrasi berhasil sebagai \033[36m{username}\033[0m \033[33m(role: {role})\033[0m")

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
            emp_id = users[u]["employee_id"]
            emp = store.employees.get(emp_id)
            if emp:
                current_user = emp.name
                current_role = emp.role.lower()
                print(f"\n\033[32mLogin berhasil sebagai \033[33m{current_user}\033[32m (role: {current_role})\033[0m")
                return
        else:
            print("\n\033[31mLogin gagal. Coba lagi\033[0m")

# Loader untuk transaksi
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
                    store.sales.append(Sale(rec["items"], int(rec["total"]), rec["date"], rec["cashier"]))
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
                print("\033[31mBarang dengan nama ini sudah ada\033[0m")
            return

    # Buat ID baru
    item_id = store.gen_id("INV")
    item = InventoryItem(item_id, name, price, category)
    item.confirmed_stock = stok_awal   # stok awal dari parameter
    store.inventory[item_id] = item

    # Catat ke log
    record = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "user": current_user if not silent else "system",
        "item_id": item_id,
        "name": name,
        "jumlah": item.confirmed_stock,
        "harga": price,
        "kategori": KATEGORI_LIST.get(category, category),
        "status": "Pending"
    }
    with open("inventory_log.txt", "a") as f:
        f.write(json.dumps(record) + "\n")

    if not silent:
        print(f"\033[32mBarang {name} ditambahkan dengan ID {item_id}\033[0m")

def edit_inventory(item_id: str, new_name: str = None, new_price: int = None,
                new_category: str = None, new_confirmed_stock: int = None,
                delete: bool = False, reason: str = None, note: str = None):
    if item_id not in store.inventory:
        print("\033[31mBarang tidak ditemukan\033[0m")
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
            "note": note if note else ""
        }
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

def add_employee(name: str, role: str, silent=False):
    # Cek duplikasi nama
    for emp in store.employees.values():
        if emp.name.lower() == name.lower():
            if not silent:
                print("\033[31mKaryawan dengan nama ini sudah ada\033[0m")
            return

    # Generate ID karyawan
    emp_id = store.gen_id("EMP")
    store.employees[emp_id] = Employee(emp_id, name, role)

    # Tambahkan ke users (otomatis buat akun login)
    username = name.lower().replace(" ", "")   # username default = nama kecil tanpa spasi
    password = emp_id                          # password default = ID karyawan
    users[username] = {"password": password, "employee_id": emp_id}

    if not silent:
        print(f"\033[32mKaryawan {name} ditambahkan dengan ID {emp_id}\033[0m")
        print(f"\033[33mAkun login: username='{username}', password='{password}' (role: {role})\033[0m")

def add_lokomotif(name: str, service_type: str, rate_per_day: int, silent=False):
    for lok in store.lokomotif.values():
        if lok.name.lower() == name.lower():
            if not silent:
                print("\033[31mLokomotif dengan nama ini sudah ada\033[0m")
            return
    lok_id = store.gen_id("LOK")
    store.lokomotif[lok_id] = Lokomotif(
        id=lok_id,
        name=name,
        service_type=service_type,
        rate_per_day=rate_per_day,
        status="Tersedia"
    )
    if not silent:
        print(f"\033[32mLokomotif {name} ditambahkan dengan ID {lok_id}\033[0m")

def add_menu(name: str, stock: int, price: int, silent=False):
    for menu in store.menu.values():
        if menu.name.lower() == name.lower():
            if not silent:
                print("\033[31mMenu dengan nama ini sudah ada\033[0m")
            return
    menu_id = store.gen_id("MEN")
    store.menu[menu_id] = MenuItem(menu_id, name, stock, price)
    if not silent:
        print(f"\033[32mMenu {name} ditambahkan dengan ID {menu_id}, stok awal {stock}\033[0m")

def add_warehouse(name: str, address: str, silent=False):
    # cek duplikat
    for w in store.warehouses.values():
        if w.name.lower() == name.lower():
            print(f"\033[31mGudang dengan nama '{name}' sudah ada (ID: {w.warehouse_id})\033[0m")
            return

    # generate ID unik
    wid = f"W{len(store.warehouses)+1:03}"
    store.warehouses[wid] = Warehouse(wid, name, address)

    if not silent:
        print(f"\033[32mGudang {name} ditambahkan dengan ID {wid}\033[0m")
'---------------------------------------------------------------------------------------------------------- part 3 -------------------------------------------'

''' DASHBOARDS '''
# Dashboard hybrid uv.3.3
# dashboard utama
def dashboard():  # (UV.1.5)
    total_sales = sum(s.total for s in store.sales)
    total_service = sum(r.total_fee for r in store.services)
    total_food = sum(o.total for o in store.food_orders)

    print("\n\033[44m=========== DASHBOARD ===========\033[0m")
    print(f"- Penjualan Barang   : {len(store.sales)} | Total: {format_rupiah(total_sales)}")
    print(f"- Service Lokomotif  : {len(store.services)} | Total: {format_rupiah(total_service)}")
    print(f"- Pemesanan Makanan  : {len(store.food_orders)} | Total: {format_rupiah(total_food)}")
    print(f"\nInventaris: {len(store.inventory)} | Karyawan: {len(store.employees)} | Lokomotif: {len(store.lokomotif)} | Menu: {len(store.menu)}")

    laporan_detail()
# Admin
def dashboard_admin():
    print("\n\033[44m=========== DASHBOARD ===========\033[0m")

    # Kondisi stok barang
    print("\n\033[34m>> Kondisi Stok Barang\033[0m")
    low_inv = False
    for it in store.inventory.values():
        if it.total_stock() < 5:   # pakai total stok dari semua gudang
            low_inv = True
            print(f"- {it.name}: stok tinggal {it.total_stock()} unit")
    if not low_inv:
        print("- Semua stok barang aman")

    # Kondisi stok menu makanan
    print("\n\033[34m>> Kondisi Stok Menu Makanan\033[0m")
    low_menu = False
    for m in store.menu.values():
        if m.stock < 5:
            low_menu = True
            print(f"- {m.name}: stok tinggal {m.stock} porsi")
    if not low_menu:
        print("- Semua stok menu aman")

    # Ringkasan transaksi
    total_sales = sum(s.total for s in store.sales)
    total_service = sum(r.total_fee for r in store.services)
    total_food = sum(o.total for o in store.food_orders)
    total_rental = sum(r.total_fee for r in store.rentals)

    print(f"- Penjualan Barang   : {len(store.sales)} transaksi | Total: {format_rupiah(total_sales)}")
    print(f"- Service Lokomotif  : {len(store.services)} transaksi | Total: {format_rupiah(total_service)}")
    print(f"- Pemesanan Makanan  : {len(store.food_orders)} pesanan | Total: {format_rupiah(total_food)}")
    print(f"- Rental Lokomotif   : {len(store.rentals)} transaksi | Total: {format_rupiah(total_rental)}")
    print(f"- Inventaris         : {len(store.inventory)} barang")
    print(f"- Karyawan           : {len(store.employees)} orang")
    print(f"- Lokomotif          : {len(store.lokomotif)} unit")
    print(f"- Menu Makanan       : {len(store.menu)} item")

    # Laporan detail gabungan
    print("\n\033[44m=========== LAPORAN DETAIL ===========\033[0m")

    # Barang terlaris
    counter = {}
    for s in store.sales:
        for i, q in s.items:
            it = store.inventory.get(i)
            if it:
                counter[it.name] = counter.get(it.name, 0) + q
    top_items(counter, "Barang terlaris", "unit")

    # Lokomotif terlaris (service)
    lokomotif_count = {}
    for r in store.services:
        lok = store.lokomotif.get(r.lokomotif_id)
        if lok:
            lokomotif_count[lok.name] = lokomotif_count.get(lok.name, 0) + 1
    top_items(lokomotif_count, "Lokomotif terlaris (service)", "kali diservis")

    # Lokomotif terlaris (rental)
    rental_count = {}
    for r in store.rentals:
        lok = store.lokomotif.get(r.lokomotif_id)
        if lok:
            rental_count[lok.name] = rental_count.get(lok.name, 0) + 1
    top_items(rental_count, "Lokomotif terlaris (rental)", "kali disewa")

    # Sparepart terpakai
    print("\n\033[34m>> Sparepart Terpakai\033[0m")
    parts_summary = {}
    for r in store.services:
        for part in r.parts_used:
            parts_summary[part] = parts_summary.get(part, 0) + 1
    if parts_summary:
        for part, count in parts_summary.items():
            print(f"- {part}: {count} kali dipakai")
    else:
        print("- Belum ada sparepart terpakai")

    # Menu favorit
    food_count = {}
    for o in store.food_orders:
        for i, q in o.items:
            m = store.menu.get(i)
            if m:
                food_count[m.name] = food_count.get(m.name, 0) + q
    top_items(food_count, "Menu favorit", "porsi")
# Kasir
def dashboard_kasir():
    print("\n\033[44m============== DASHBOARD ==============\033[0m")
    if not store.sales:
        print("\n\033[33mBelum ada transaksi penjualan\033[0m")
        return
    
    # Total transaksi & total penjualan
    total_sales = sum(s.total for s in store.sales)
    print(f"Jumlah transaksi: {len(store.sales)}")
    print(f"Total penjualan: {format_rupiah(total_sales)}")

    # Barang terlaris
    counter = {}
    for s in store.sales:
        for i, q in s.items:
            nm = store.inventory[i].name
            counter[nm] = counter.get(nm, 0) + q

    top_items(counter, "Barang terlaris", "unit")
# Service
def dashboard_service():
    print("\n\033[44m========== DASHBOARD ===========\033[0m")
    if not store.services:
        print("\n\033[33mBelum ada transaksi service lokomotif\033[0m")
        return

    total_service = sum(r.total_fee for r in store.services)
    print(f"Jumlah transaksi service: {len(store.services)}")
    print(f"Total pendapatan service: {format_rupiah(total_service)}")

    lokomotif_count = {}
    for r in store.services:
        lok = store.lokomotif.get(r.lokomotif_id)
        if lok:
            lokomotif_count[lok.name] = lokomotif_count.get(lok.name, 0) + 1
    top_items(lokomotif_count, "Lokomotif terlaris", "kali diservis")

    print("\n\033[4m> Status Lokomotif:\033[0m")
    for lok in store.lokomotif.values():
        status = "\033[32mTersedia\033[0m" if lok.status == "Tersedia" else ("\033[33mDiservis\033[0m" if lok.status == "Diservis" else "\033[36mSelesai\033[0m")
        print(f"- {lok.name}: {status}")
# Rental
def dashboard_rental():
    print("\n\033[44m=========== DASHBOARD RENTAL ===========\033[0m")
    if not store.rentals:
        print("\033[33mBelum ada transaksi rental\033[0m")
        return

    total_rental = sum(r.total_fee for r in store.rentals)
    active = sum(1 for r in store.rentals if r.status == "Berjalan")
    selesai = sum(1 for r in store.rentals if r.status == "Selesai")

    print(f"Jumlah transaksi rental : {len(store.rentals)}")
    print(f"Rental aktif            : {active}")
    print(f"Rental selesai          : {selesai}")
    print(f"Total pendapatan rental : {format_rupiah(total_rental)}")

    # Lokomotif paling sering disewa
    rental_count = {}
    for r in store.rentals:
        lok = store.lokomotif.get(r.lokomotif_id)
        if lok:
            rental_count[lok.name] = rental_count.get(lok.name, 0) + 1
    top_items(rental_count, "Lokomotif terlaris (rental)", "kali disewa")
# Dapur
def dashboard_dapur():
    print("\n\033[44m=========== DASHBOARD ===========\033[0m")
    if not store.food_orders:
        print("\n\033[33mBelum ada pesanan makanan\033[0m")
        return
    
    # Total pesanan & total pendapatan makanan
    total_food = sum(o.total for o in store.food_orders)
    print(f"Jumlah pesanan: {len(store.food_orders)}")
    print(f"Total pendapatan makanan: {format_rupiah(total_food)}")

    # Menu favorit (paling sering dipesan)
    food_count = {}
    for o in store.food_orders:
        for i, q in o.items:
            nm = store.menu[i].name
            food_count[nm] = food_count.get(nm, 0) + q

    top_items(food_count, "Menu favorit", "porsi")
# Gudang
def dashboard_gudang():
    print("\n\033[44m=========== DASHBOARD GUDANG ===========\033[0m")
    # Ringkasan gudang
    print(f"Jumlah gudang: {len(store.warehouses)}")
    if not store.warehouses:
        print("\033[33mBelum ada gudang terdaftar\033[0m")
        return

    # Loop setiap gudang
    for wh in store.warehouses.values():
        print(f"\nGudang {wh.warehouse_id} | {wh.name} | Alamat: {wh.address}")
        print("-" * 50)

        # Cari barang yang punya stok di gudang ini
        found = False
        for item in store.inventory.values():
            qty = item.stock_by_warehouse.get(wh.warehouse_id, 0)
            if qty > 0:
                found = True
                print(f"{item.item_id} | {item.name} | Stok: {qty} unit | Harga: {format_rupiah(item.price)} | Status: {item.status}")
        if not found:
            print("\033[33mTidak ada stok barang di gudang ini\033[0m")
'---------------------------------------------------------------------------------------------------------- part 4 -------------------------------------------'

''' MENUS '''
# >> Module menus
# INVENTARIS (clear v.3.7)
def inventory_menu():
    global current_role
    while True:
        # bagian gudang/inventaris
        if current_role == "gudang":
            ops = {
                "1": "Tambah Barang",
                "2": "Ubah/Hapus Barang",
                "3": "Lihat Riwayat Barang",
                "4": "Minta Konfirmasi Siap Jual",
                "9": "Kembali"}
            choice = input_menu("MENU INVENTARIS (Inventaris)", ops)

            # Tambah barang
            if choice == "1":
                if not check_access("gudang"):
                    return
                name = input("Nama barang: ").strip()
                jumlah = input_int("Jumlah unit: ", min_val=1)
                harga_beli = input_int("Harga beli per unit: ", min_val=1)
                category_code = pilih_kategori()
                item_id = store.gen_id("INV")

                store.inventory[item_id] = InventoryItem(
                    item_id=item_id,
                    name=name,
                    price=harga_beli,
                    category=category_code)
                store.inventory[item_id].confirmed_stock = jumlah

                log_inventory(
                    "Tambah Barang",
                    store.inventory[item_id],
                    {"jumlah": jumlah, "harga": harga_beli, "kategori": category_code, "status": "Pending"})
                log_employee_action(current_user, current_role, "Tambah Barang", {"item": name, "qty": jumlah})

                print(f"\033[32mBarang {name} ditambahkan ke gudang\033[0m")
            # Ubah/Hapus barang
            elif choice == "2":
                print_inventory()
                item_query = input("\nID/Nama (gunakan koma): ").strip()
                items = find_item(item_query)   # fungsi pencarian banyak ID/Nama

                if not items:
                    print("\033[31mBarang tidak ditemukan\033[0m")
                    continue

                for item in items:
                    ops_edit = {
                        "1": "Ubah Harga",
                        "2": "Ubah Kondisi",
                        "3": "Ubah Stok",
                        "4": "Hapus Barang"}
                    sub_choice = input_menu(f"Perubahan Data Barang {item.item_id} | {item.name}", ops_edit)

                    # Ubah harga
                    if sub_choice == "1":
                        price = input_int(f"Harga baru untuk {item.name}: ", min_val=1)
                        old_price = item.price
                        item.price = price
                        log_inventory(
                            "Perubahan Harga Barang",
                            item,
                            {"changes": {"price": [old_price, price]}})
                        print(f"\033[32mHarga {item.name} diperbarui dari Rp{old_price:,} ke Rp{price:,}\033[0m")
                    # Ubah kondisi
                    elif sub_choice == "2":
                        kondisi_ops = {"1": "Rusak", "2": "Hilang", "3": "Kadaluarsa"}
                        kondisi_choice = input_menu("Pilih kondisi", kondisi_ops)
                        old_status = item.status
                        item.status = kondisi_ops.get(kondisi_choice, "Pending")
                        log_inventory(
                            "Perubahan Kondisi Barang",
                            item,
                            {"changes": {"status": [old_status, item.status]}})
                        print(f"\033[32mBarang {item.name} sekarang berstatus {item.status}\033[0m")
                    # Ubah stok
                    elif sub_choice == "3":
                        stok_baru = input_int(f"Stok baru untuk {item.name}: ", min_val=0)
                        old_stok = item.confirmed_stock
                        item.confirmed_stock = stok_baru
                        log_inventory(
                            "Perubahan Stok Barang",
                            item,
                            {"changes": {"stok": [old_stok, stok_baru]}}
                        )
                        print(f"\033[32mStok {item.name} diperbarui dari {old_stok} ke {stok_baru}\033[0m")
                    # Hapus barang
                    elif sub_choice == "4":
                        log_inventory(
                            "Penghapusan Barang",
                            item,
                            {"price": item.price, "reason": "Hapus Barang"},
                            filename="inventory_deletions.txt")
                        print(f"\033[32mBarang {item.name} dihapus dari gudang\033[0m")
            # riwayat barang masuk/keluar
            elif choice == "3":
                riwayat_barang()
            # Minta konfirmasi siap jual
            elif choice == "4":
                print_inventory()
                item_query = input("\nID/Nama (gunakan koma): ").strip()
                items = find_item(item_query)

                if not items:
                    print("\033[31mBarang tidak ditemukan\033[0m")
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
                    print(f"\033[33mPermintaan konfirmasi {item.name} dikirim ke Admin\033[0m")
            elif choice == "9":
                return

        # bagian admin
        elif current_role == "admin":
            ops = {"1": "Lihat Riwayat Barang Masuk/Keluar", "2": "Review Permintaan Konfirmasi", "9": "Kembali"}
            choice = input_menu("MENU INVENTARIS (Admin)", ops)

            if choice == "1":
                riwayat_barang()
            elif choice == "2":
                review_requests()
            elif choice == "9":
                return

# GUDANG
def warehouse_menu():
    while True:
        h = head("KELOLA GUDANG")
        ops = {
            "1": "Daftar gudang",
            "2": "Tambah gudang",
            "3": "Mutasi stok",
            "4": "Konfirmasi status barang",
            "5": "Lihat stok per gudang",
            "0": "Kembali"}
        choice = input_menu("Menu Gudang", ops)
        # Daftar gudang
        if choice == "1":
            print("\nDaftar Gudang:")
            for w in store.warehouses.values():
                print(f"- {w.warehouse_id}: {w.name} (Alamat: {w.address})")
            pause()
        # Tambah gudang
        elif choice == "2":
            name = input("Nama gudang: ").strip()
            address = input("Alamat gudang: ").strip()

            add_warehouse(name, address)

            # Catat log penambahan gudang
            log_warehouse(
                "Tambah Gudang",
                item_id="N/A",   # karena ini gudang baru, bukan barang
                extra={"name": name, "address": address})

            print(f"\033[32mGudang {name} berhasil ditambahkan\033[0m")
        # Mutasi stok
        elif choice == "3":
            if not check_access("gudang"):
                return

            print_inventory()
            item_query = input("\nID/Nama barang: ").strip()
            item = find_item(item_query)
            if not item:
                print("\033[31mBarang tidak ditemukan\033[0m")
                continue

            from_wh = input("Gudang asal (ID): ").strip().upper()
            to_wh = input("Gudang tujuan (ID): ").strip().upper()
            qty = input_int("Jumlah transfer: ", min_val=1)

            if store.warehouses[from_wh].stock.get(item.item_id, 0) < qty:
                print("\033[31mStok di gudang asal tidak cukup\033[0m")
            else:
                transfer_stock(item.item_id, from_wh, to_wh, qty)

                # Catat log gudang
                log_warehouse(
                    "Mutasi Stok",
                    item.item_id,
                    from_wh=from_wh,
                    to_wh=to_wh,
                    qty=qty)

                # Catat aktivitas karyawan
                log_employee_action(
                    current_user,
                    current_role,
                    "Mutasi Stok",
                    {"item": item.name, "from": from_wh, "to": to_wh, "qty": qty})

                print(f"\033[32m{qty} unit {item.name} dipindahkan dari {from_wh} ke {to_wh}\033[0m")
        # Konfir kondisi
        elif choice == "4":
            print_inventory()
            item_query = input("\nID/Nama barang: ").strip()
            item = find_item(item_query)
            if not item:
                print("\033[31mBarang tidak ditemukan\033[0m")
                continue

            status_ops = {"1": "Siap Jual", "2": "Disimpan", "3": "Rusak", "4": "Hilang", "5": "Kadaluarsa", "6": "Pending"}
            status_choice = input_menu("Konfirmasi kondisi", status_ops)
            old_status = item.status
            item.status = status_ops.get(status_choice, "Disimpan")

            # Catat log perubahan status
            log_warehouse(
                "Konfirmasi Status Barang",
                item.item_id,
                extra={"old_status": old_status, "new_status": item.status})

            # UI warna kondisi
            if item.status in ["Rusak", "Hilang"]:
                status_ui = f"\033[31m{item.status}\033[0m"
            elif item.status == "Pending":
                status_ui = f"\033[33m{item.status}\033[0m"
            elif item.status == "Siap Jual":
                status_ui = f"\033[32m{item.status}\033[0m"
            else:
                status_ui = item.status

            print(f"\033[32mBarang {item.item_id} ({item.name}) sekarang berkondisi {status_ui}\033[0m")
        # stok per gudang
        elif choice == "5":
            dashboard_gudang()
            pause()
        elif choice == "0":
            return

# Karyawan (PERLU TAMBHAN)
def employee_menu():
    while True:
        h = head("KELOLA KARYAWAN")
        ops = {"1": "Lihat karyawan", "2": "Tambah karyawan", "3": "Ubah jabatan", "4": "Hapus Karyawan","0": "Kembali"}
        choice = input_menu("Data Karyawan", ops)
        # Karyawan
        if choice == "1":
            print_employees()
            pause()
        # Tambah
        elif choice == "2":
            name = input("Nama: ").strip()
            if not name:
                print("\033[31mNama tidak boleh kosong\033[0m")
                continue
            role = input("Jabatan: ").strip()
            if not role:
                print("\033[31mJabatan tidak boleh kosong\033[0m")
                continue
            add_employee(name, role)
            print(f"\n\033[32mKaryawan {name} berhasil ditambahkan\033[0m")
        # Ubah
        elif choice == "3":
            print_employees()
            emp_id = input("ID karyawan: ").strip().upper()
            if emp_id not in store.employees:
                print(f"\n\033[31mID {emp_id} tidak ditemukan\033[0m")
                continue
            role = input("Jabatan baru: ").strip()
            store.employees[emp_id].role = role
            print(f"\033[32mJabatan {role} telah diperbarui\033[0m")
        # Hapus 
        elif choice == "4":
            emp_id = input("ID karyawan: ").strip().upper()
            if emp_id in store.employees:
                del store.employees[emp_id]
                print("\033[32mKaryawan dihapus\033[0m")
            else:
                print(f"\n\033[31mKaryawan dengan ID {emp_id} tidak ditemukan\033[0m")
        elif choice == "0":
            return

# Penjualan (PERLU TAMBHAN)
def sales_menu():
    if not check_access("kasir"):
        return

    while True:
        h = head("KELOLA PENJUALAN")
        ops = {
            "1": "Lihat Stok",
            "2": "Transaksi Penjualan",
            "3": "Riwayat Penjualan",
            "0": "Kembali"}
        p = input_menu("Data Penjualan", ops)
        # Stok
        if p == "1":
            print("\n\033[34m>> Barang Siap Jual:\033[0m")
            for item in store.inventory.values():
                if item.status == "Siap Jual" and item.confirmed_stock > 0:
                    print(f"- {item.item_id}: {item.name} | Harga: {format_rupiah(item.price)} | Stok aman: {item.confirmed_stock}")
            pause()
        # Transaksi penjualan
        elif p == "2":
            cart = []
            while True:
                print('\033[33m\033[3m*enter jika selesai\033[0m')
                query = input("\nID/Nama barang: ").strip()
                if query == "":
                    break
                item = find_item(query)
                if not item:
                    print(f"\n\033[31mBarang {query} tidak ada\033[0m")
                    continue
                if item.status != "Siap Jual" or item.confirmed_stock <= 0:
                    print("\n Barang \033[33mbelum dikonfirmasi\033[0m untuk dijual")
                    continue
                qty = input_int("Jumlah: ", min_val=1)
                if qty > item.confirmed_stock:
                    print("\033[33mStok aman kurang\033[0m")
                    continue
                cart.append((item.item_id, qty))

            if not cart:
                print("\n\033[31mKeranjang kosong. Ulangi input barang\033[0m")
                continue

            total = sum(store.inventory[i].price * q for i, q in cart)
            for i, q in cart:
                store.inventory[i].confirmed_stock -= q  # kurangi stok aman

            sale = Sale(cart, total, datetime.now().strftime("%Y-%m-%d (%H:%M)"), current_user)
            store.sales.append(sale)
            # Catat ke file log penjualan
            log_sale("barang", "MULTI", total, {"items": cart})
            # Catat aktivitas karyawan
            log_employee_action(
                current_user,
                current_role,
                "Transaksi Penjualan",
                {"items": cart, "total": total})

            print(f"\n\033[32mTransaksi berhasil. Total: {format_rupiah(total)}\033[0m")
        # Riwayat
        elif p == "3":
            if not store.sales:
                print("\n\033[33mBelum ada penjualan\033[0m")
            else:
                print("\n\033[34m>> Riwayat Penjualan:\033[0m")
                for idx, sale in enumerate(store.sales, 1):
                    detail = []
                    for item_id, qty in sale.items:
                        it = store.inventory.get(item_id)
                        nm = it.name if it else item_id
                        detail.append(f"{nm} x{qty}")
                    print(f"{idx}. {'; '.join(detail)} | Total: {format_rupiah(sale.total)}")
            pause()
        elif p == "0":
            return

# Service (PERLU TAMBHAN)
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

# Rental
def rental_menu():
    if not check_access("rental"):
        return

    while True:
        h = head("KELOLA RENTAL LOKOMOTIF/ALAT")
        ops = {
            "1": "Lihat Lokomotif/Alat",
            "2": "Mulai Rental",
            "3": "Selesaikan Rental",
            "4": "Riwayat Rental",
            "0": "Kembali"}
        p = input_menu("Data Rental", ops)
        # Lihat daftar
        if p == "1":
            print("\n\033[34m>> Daftar Lokomotif/Alat:\033[0m")
            for lok in store.lokomotif.values():
                print(f"- {lok.lok_id}: {lok.name} | Status: {lok.status} | Tarif: {format_rupiah(lok.rate_per_day)}")
            pause()
        # Mulai rental
        elif p == "2":
            lok_id = input("ID Lokomotif/Alat: ").strip().upper()
            lok = store.lokomotif.get(lok_id)
            if not lok or lok.status != "Tersedia":
                print("\033[31mTidak tersedia untuk rental\033[0m")
                continue

            customer = input("Nama customer: ").strip()
            days = input_int("Durasi (hari): ", min_val=1)

            total_fee = lok.rate_per_day * days
            start_date = datetime.now()
            end_date = start_date + timedelta(days=days)
            lok.status = "Disewa"

            record = RentalRecord(
                lokomotif_id=lok_id,
                customer=customer,
                days=days,
                total_fee=total_fee,
                start_date=start_date.strftime("%Y-%m-%d (%H:%M)"),
                end_date=end_date.strftime("%Y-%m-%d (%H:%M)"),
                officer=current_user)
            store.rentals.append(record)

            # Catat ke file
            with open("rentals.txt", "a") as f:
                f.write(json.dumps(record.__dict__) + "\n")

            # Integrasi ke penjualan
            sale_id = store.gen_id("SALE")
            store.sales[sale_id] = {
                "type": "rental",
                "ref": lok_id,
                "amount": total_fee,
                "date": record.start_date}
            log_sale("rental", lok_id, total_fee, {"customer": customer, "days": days})

            # Logging aktivitas karyawan
            log_employee_action(
                current_user,
                current_role,
                "Mulai Rental",
                {"lok_id": lok_id, "customer": customer, "days": days, "total_fee": total_fee})

            # Cetak nota rental
            tampilkan_nota_rental(record)
        # Selesaikan rental
        elif p == "3":
            if not store.rentals:
                print("\n\033[33mBelum ada transaksi rental\033[0m")
                continue
            print("\n>> Transaksi Rental:")
            for idx, r in enumerate(store.rentals, 1):
                lok = store.lokomotif.get(r.lokomotif_id)
                status = "\033[33mDisewa\033[0m" if lok and lok.status == "Disewa" else "\033[32mSelesai\033[0m"
                print(f"{idx}. {r.customer} | {lok.name if lok else r.lokomotif_id} | {r.days} hari | {format_rupiah(r.total_fee)} | Status: {status}")

            idx = input_int("Pilih nomor transaksi yang selesai: ", min_val=1, max_val=len(store.rentals))
            r = store.rentals[idx - 1]
            if r.lokomotif_id in store.lokomotif:
                store.lokomotif[r.lokomotif_id].status = "Selesai"

            log_sale("rental selesai", r.lokomotif_id, r.total_fee, {"customer": r.customer})
            log_employee_action(current_user, current_role, "Selesaikan Rental", {"lok_id": r.lokomotif_id, "customer": r.customer})

            print("\n\033[32mRental ditandai selesai. Status lokomotif diperbarui ke 'Selesai'\033[0m")
        # Riwayat rental
        elif p == "4":
            if not store.rentals:
                print("\n\033[33mBelum ada rental\033[0m")
            else:
                print("\n>> Riwayat Rental:")
                for idx, r in enumerate(store.rentals, 1):
                    lok = store.lokomotif.get(r.lokomotif_id)
                    print(f"{idx}. Customer: {r.customer} | Lokomotif: {lok.name if lok else r.lokomotif_id} | Durasi: {r.days} hari | Total: {format_rupiah(r.total_fee)}")
            pause()
        elif p == "0":
            return

# Pesan Makan (PERLU TAMBHAN)
def food_menu():
    while True:
        h = head("KELOLA PEMESANAN")
        if current_role in ["admin", "dapur"]:
            ops = {"1": "Lihat menu", "2": "Buat pesanan", "3": "Riwayat pesanan", "4": "Hapus menu", "0": "Kembali"}
        elif current_role == "pembeli":
            ops = {"1": "Lihat menu", "2": "Buat pesanan", "3": "Riwayat pesanan", "0": "Kembali"}
        else:
            print("\033[31mRole tidak berhak mengakses modul makanan\033[0m")
            return

        p = input_menu("Data Pesan Makanan", ops)
        # Daftar menu
        if p == "1":
            print_menu_items()
            pause()
        # Buat pesanan
        elif p == "2":
            if not check_access("pembeli") and not check_access("dapur"):
                return

            customer_name = input("Nama customer: ").strip()
            table_number = input("Nomor meja: ").strip()

            cart: List[Tuple[str, int]] = []
            while True:
                print_menu_items()
                print("\n\033[33m\033[3m*Enter untuk selesai\033[0m\033[0m")
                menu_id = input("ID Menu: ").strip().upper()
                if menu_id == "":
                    break
                if menu_id not in store.menu:
                    print(f"\n\033[31mID {menu_id} tidak ditemukan\033[0m")
                    continue
                qty = input_int("Jumlah: ", min_val=1)
                if qty > store.menu[menu_id].stock:
                    print("\n\033[33mStok menu tidak cukup\033[0m")
                    continue
                store.menu[menu_id].stock -= qty
                cart.append((menu_id, qty))

            if not cart:
                print("\033[33mKeranjang kosong\033[0m \033[47mBatal\033[0m")
                return

            total = sum(store.menu[mid].price * q for mid, q in cart)

            order = FoodOrder(
                items=cart,
                total=total,
                date=datetime.now().strftime("%Y-%m-%d (%H:%M)"),
                waiter=current_user,
                customer_name=customer_name,
                table_number=table_number
            )
            store.food_orders.append(order)

            # Catat ke file food_orders
            with open("food_orders.txt", "a") as f:
                f.write(json.dumps(order.__dict__) + "\n")

            # Integrasi ke penjualan
            sale_id = store.gen_id("SALE")
            store.sales[sale_id] = {
                "type": "food",
                "ref": order.customer_name,
                "amount": total,
                "date": order.date
            }
            log_sale("food", order.customer_name, total, {"items": cart, "table": table_number})

            # Logging aktivitas karyawan
            log_employee_action(
                current_user,
                current_role,
                "Buat Pesanan Food",
                {"customer": customer_name, "table": table_number, "items": cart, "total": total})

            # Cetak nota
            tampilkan_nota_makanan(order, store)
        # Riwayat
        elif p == "3":
            if not store.food_orders:
                print("\n\033[33mBelum ada pesanan\033[0m")
            else:
                print("\n>> Riwayat Pesanan:")
                for idx, o in enumerate(store.food_orders, 1):
                    detail = []
                    for menu_id, qty in o.items:
                        m = store.menu.get(menu_id)
                        nm = m.name if m else menu_id
                        detail.append(f"{nm} x{qty}")
                    print(f"{idx}. {o.date} | {o.waiter} | {'; '.join(detail)} | Total: {format_rupiah(o.total)}")
            pause()
        # Hapus menu + alasn
        elif p == "4":
            print_menu_items()
            menu_id = input("ID menu yang dihapus: ").strip().upper()
            if menu_id in store.menu:
                alasan_ops = {"1": "Kadaluarsa", "2": "Habis", "3": "Discontinue", "4": "Resep berubah", "5": "Lainnya"}
                alasan_choice = input_menu("Alasan penghapusan", alasan_ops)
                alasan = alasan_ops.get(alasan_choice, "Lainnya")
                note = ""
                if alasan == "Lainnya":
                    note = input("Keterangan tambahan: ").strip()
                confirm = input(f"Yakin hapus menu {store.menu[menu_id].name}? (y/n): ").lower()
                if confirm == "y":
                    record = {
                        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "operator": current_user,
                        "menu_id": menu_id,
                        "name": store.menu[menu_id].name,
                        "stock": store.menu[menu_id].stock,
                        "price": store.menu[menu_id].price,
                        "reason": alasan,
                        "note": note
                    }
                    with open("menu_deletions.txt", "a") as f:
                        f.write(json.dumps(record) + "\n")
                    del store.menu[menu_id]
                    print("\033[32mMenu berhasil dihapus\033[0m")
                else:
                    print("\033[33mPenghapusan dibatalkan\033[0m")
            else:
                print("\033[31mID tidak ditemukan\033[0m")
        elif p == "0":
            return

# Laporan (PERLU TAMBHAN)
def laporan_detail():
    head("LAPORAN DETAIL")

    # Barang terlaris
    counter = {}
    for s in store.sales:
        for i, q in s.items:
            it = store.inventory.get(i)
            if it:
                key = it.name
            else:
                key = i  # fallback ke ID kalau barang sudah dihapus
            counter[key] = counter.get(key, 0) + q
    top_items(counter, "Barang terlaris", "unit")

    # Lokomotif terlaris
    lokomotif_count = {}
    for r in store.services:
        lok = store.lokomotif.get(r.lokomotif_id)
        if lok:
            lokomotif_count[lok.name] = lokomotif_count.get(lok.name, 0) + 1
    top_items(lokomotif_count, "Lokomotif terlaris", "kali diservis")

    # Menu favorit
    food_count = {}
    for o in store.food_orders:
        for i, q in o.items:
            m = store.menu.get(i)
            if m:
                food_count[m.name] = food_count.get(m.name, 0) + q
            else:
                food_count[i] = food_count.get(i, 0) + q  # fallback ke ID
    top_items(food_count, "Menu favorit", "porsi")
'---------------------------------------------------------------------------------------------------------- part 5.2 -------------------------------------------'

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
                "3": "Manajemen Penjualan",
                "4": "Servis Mobil",
                "5": "Manajemen Gudang",
                "6": "Dasbor Gabungan",
                "7": "Hapus Akun",
                "8": "Review Permintaan Konfirmasi",
                "9": "Keluar"}
            choice = input_menu("MENU UTAMA (Admin)", ops)
            if choice == "1": inventory_menu()
            elif choice == "2": employee_menu()
            elif choice == "3": sales_menu()
            elif choice == "4": service_menu()
            elif choice == "5": warehouse_menu()
            elif choice == "6": dashboard()
            elif choice == "7": delete_user()
            elif choice == "8": review_requests()
            elif choice == "9":
                current_user, current_role = None, None
                print("\n\033[32mBerhasil keluar \033[0m")
                return
            elif choice == "0": sys.exit(0)

        elif current_role == "kasir":
            ops = {
                "1": "Penjualan Barang",
                "2": "Dasbor Penjualan",
                "9": "Keluar"}
            choice = input_menu("MENU UTAMA (Kasir)", ops)
            if choice == "1": sales_menu()
            elif choice == "2": dashboard_kasir()
            elif choice == "9":
                current_user, current_role = None, None
                print("\n\033[32mBerhasil keluar\033[0m")
                return
            elif choice == "0": sys.exit(0)

        elif current_role == "service":
            ops = {
                "1": "Servis Mobil",
                "2": "Dasbor Servis",
                "9": "Keluar"}
            choice = input_menu("MENU UTAMA (Servis)", ops)
            if choice == "1": service_menu()
            elif choice == "2": dashboard_service()
            elif choice == "9":
                current_user, current_role = None, None
                print("\n\033[32mBerhasil keluar\033[0m")
                return
            elif choice == "0": sys.exit(0)

        elif current_role == "rental":
            ops = {
                "1": "Kelola Rental Lokomotif/Alat",
                "2": "Dasbor Rental",
                "9": "Keluar"}
            choice = input_menu("MENU UTAMA (Rental)", ops)
            if choice == "1":
                rental_menu()     
            elif choice == "2":
                dashboard_rental()
            elif choice == "9":
                current_user, current_role = None, None
                print("\n\033[32mBerhasil keluar\033[0m")
                return
            elif choice == "0":
                sys.exit(0)

        elif current_role == "dapur":
            ops = {
                "1": "Menu Makanan",
                "2": "Dasbor Dapur",
                "9": "Keluar"}
            choice = input_menu("MENU UTAMA (Dapur)", ops)
            if choice == "1": food_menu()
            elif choice == "2": dashboard_dapur()
            elif choice == "9":
                current_user, current_role = None, None
                print("\n\033[32mLogout berhasil\033[0m")
                return
            elif choice == "0": sys.exit(0)

        elif current_role == "gudang":
            ops = {
                "1": "Kelola Inventaris",
                "2": "Kelola Gudang",
                "3": "Dasbor Gudang",
                "9": "Keluar"}
            choice = input_menu("MENU UTAMA (Gudang)", ops)
            if choice == "1":
                inventory_menu()
            elif choice == "2":
                warehouse_menu()   # menu gudang, tapi logika ubah status "Siap Jual" diarahkan ke request
            elif choice == "3":
                dashboard_gudang()
                pause()
            elif choice == "9":
                current_user, current_role = None, None
                print("\n\033[32mBerhasil keluar\033[0m")
                return
            elif choice == "0":
                sys.exit(0)

        elif current_role == "pembeli":
            ops = {
                "1": "Lihat Menu Makanan",
                "2": "Pesan Makanan",
                "3": "Lihat Pesanan",
                "9": "Keluar"}
            choice = input_menu("MENU UTAMA (Pembeli)", ops)
            if choice == "1": print_menu_items()
            elif choice == "2": food_menu()
            elif choice == "3": laporan_detail()  # atau tampilkan pesanan pembeli
            elif choice == "9":
                current_user, current_role = None, None
                print("\n\033[32mBerhasil keluar\033[0m")
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
        if start_menu():       # login
            seed_data()        # isi data
            load_sales()
            load_services()
            load_food_orders()
            main_menu()        # menu utama
    except KeyboardInterrupt:
        print("\n\033[41m Program dihentikan oleh user \033[0m")
        sys.exit(0)

''' ENTRY POINT '''
if __name__ == "__main__":
    main()
'---------------------------------------------------------------------------------------------------------- part 5.3 -------------------------------------------'

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


"""