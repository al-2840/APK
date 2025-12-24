"""
Aplikasi       : APLIKASI MANAJEMEN OPERASIONAL TERPADU (AMOT) - Versi 4.0 (target max fix, MAJOR.MINOR.PATCH)
Fitur          : Mengelola inventaris, karyawan, penjualan, service mobil, dan pemesanan makanan, semuanya terintegrasi dengan laporan ringkas di dashboard.
Penulis        : 2840 & 2835
Versi (update) : 3.2
"""
import sys, time, ast, json
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Tuple

''' DATA LAYER '''
# Data master (10 item per module)
def seed_data():
    # Gudang
    add_warehouse("Pusat", "Jl. Malang No.1")
    add_warehouse("Cabang 1", "Jl. Ahmad Yani No.25")
    add_warehouse("Cabang 2", "Jl. Cempaka No.15")

    # Inventory (stok otomatis masuk ke Gudang Pusat W001)
    add_inventory("Oli Mesin", 50, 75000)
    add_inventory("Filter Udara", 30, 120000)
    add_inventory("Ban Lokomotif", 20, 1500000)
    add_inventory("Kampas Rem", 40, 250000)
    add_inventory("Busi", 100, 35000)
    add_inventory("Cat Body Merah", 25, 200000)
    add_inventory("Cat Body Biru", 25, 200000)
    add_inventory("Toolkit Mekanik", 15, 500000)
    add_inventory("Dongkrak Hidrolik", 10, 1250000)
    add_inventory("Solar", 200, 10000)

    # Employees
    add_employee("Andi", "Kasir")
    add_employee("Budi", "Service")
    add_employee("Citra", "Dapur")
    add_employee("Dewi", "Admin")
    add_employee("Eko", "Gudang")
    add_employee("Fajar", "Kasir")
    add_employee("Gina", "Service")
    add_employee("Hadi", "Dapur")
    add_employee("Indra", "Admin")
    add_employee("Joko", "Gudang")

    # Lokomotif
    add_lokomotif("Unit Mesin A", "Perbaikan Mesin", 350000)
    add_lokomotif("Unit Mesin B", "Overhaul", 450000)
    add_lokomotif("Unit Cat 1", "Pengecatan", 300000)
    add_lokomotif("Unit Mesin C", "Perbaikan Mesin", 375000)
    add_lokomotif("Unit Mesin D", "Overhaul", 600000)
    add_lokomotif("Unit Cat 2", "Pengecatan", 350000)
    add_lokomotif("Unit Mesin E", "Perbaikan Mesin", 400000)
    add_lokomotif("Unit Mesin F", "Overhaul", 500000)
    add_lokomotif("Unit Cat 3", "Pengecatan", 325000)
    add_lokomotif("Unit Mesin G", "Perbaikan Mesin", 420000)

    # Menu
    add_menu("Nasi Goreng", 20, 25000)
    add_menu("Mie Ayam", 25, 20000)
    add_menu("Soto Banjar", 15, 30000)
    add_menu("Ayam Bakar", 20, 35000)
    add_menu("Ikan Bakar", 15, 40000)
    add_menu("Es Teh Manis", 50, 5000)
    add_menu("Es Jeruk", 40, 8000)
    add_menu("Kopi Hitam", 30, 10000)
    add_menu("Teh Tarik", 25, 12000)
    add_menu("Jus Alpukat", 20, 15000)

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
# format duit
def format_rupiah(n: int) -> str:
    s = f" {n:,}".replace(",", ".")
    return f"Rp {s}"
# 
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
# >> UI Helpers
# inventaris
def print_inventory():
    print("\n\033[34m>> INVENTARIS BARANG:\033[0m")
    if not store.inventory:
        print("\033[31m- KOSONG -\033[0m")
        return
    for it in store.inventory.values():
        print(f"- {it.item_id} | {it.name} | Stok: {it.stock} | Harga: {format_rupiah (it.price)}")
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
# Header
def head(prompt):
    print(f"\n\033[44m =========== {prompt} =========== \033[0m")
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
# Refactor dashboard UV.3.3
def top_items(counter: dict, label: str, unit: str = ""):
    """Cetak daftar item terlaris dari counter dict"""
    if counter:
        print(f"\n\033[4m>> {label}:\033[0m")
        for nm, qty in sorted(counter.items(), key=lambda x: x[1], reverse=True):
            print(f"- {nm}: {qty} {unit}")
    else:
        print(f"\n\033[33mBelum ada data {label.lower()}\033[0m")

def adjust_stock(item_id: str, warehouse_id: str, delta: int):
    if item_id not in store.inventory or warehouse_id not in store.warehouses:
        print("\033[31mItem atau gudang tidak ditemukan\033[0m")
        return
    current = store.inventory[item_id].stock_by_warehouse.get(warehouse_id, 0)
    new_stock = current + delta
    if new_stock < 0:
        print("\033[31mStok tidak boleh negatif\033[0m")
        return
    store.inventory[item_id].stock_by_warehouse[warehouse_id] = new_stock
    print(f"\033[32mStok {store.inventory[item_id].name} di {store.warehouses[warehouse_id].name} sekarang {new_stock}\033[0m")

def transfer_stock(item_id: str, from_wh: str, to_wh: str, qty: int):
    if item_id not in store.inventory or from_wh not in store.warehouses or to_wh not in store.warehouses:
        print("\033[31mItem atau gudang tidak ditemukan\033[0m")
        return
    if store.inventory[item_id].stock_by_warehouse.get(from_wh, 0) < qty:
        print("\033[31mStok di gudang asal tidak cukup\033[0m")
        return
    adjust_stock(item_id, from_wh, -qty)
    adjust_stock(item_id, to_wh, qty)
    print(f"\033[32mTransfer {qty} unit {store.inventory[item_id].name} dari {store.warehouses[from_wh].name} ke {store.warehouses[to_wh].name}\033[0m")
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

@dataclass  # (UV.1.1)
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

class InventoryItem:
    def __init__(self, item_id: str, name: str, price: int, stock: int = 0, category: str = "Umum"):
        self.item_id = item_id
        self.name = name
        self.price = price
        self.stock = stock                 # stok umum (dipakai oleh menu penjualan)
        self.category = category           # contoh: "Suku Cadang", "Peralatan", "Bahan Bakar"
        self.stock_by_warehouse: Dict[str, int] = {}  # stok per gudang
        self.stock_by_warehouse: Dict[str, int] = {}
        self.status = "Pending"            # "Pending", "Siap Jual", "Rusak/Hilang", "Disimpan"

    def total_stock(self) -> int:
        # jika stok per gudang dipakai, hitung totalnya; jika kosong, pakai stok umum
        return sum(self.stock_by_warehouse.values()) if self.stock_by_warehouse else self.stock

class Warehouse:
    def __init__(self, warehouse_id: str, name: str, address: str):
        self.warehouse_id = warehouse_id
        self.name = name
        self.address = address

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
# >> Data user uv.3.0
users = {
    "admin": {"password": "123", "role": "admin"},
    "1": {"password": "1", "role": "kasir"},
    "2": {"password": "2", "role": "service"},
    "3": {"password": "3", "role": "dapur"},
    "4": {"password": "4", "role": "pembeli"},
    "": {""}}

current_user = None
current_role = None

# coba load users dari file
try:
    with open("users.json", "r") as f:
        users = json.load(f)
except FileNotFoundError:
    pass

# => Utility
def save_users():
    with open("users.json", "w") as f:
        json.dump(users, f)
# => Registrasi
def register():
    print("\n\033[44m=========== REGISTRASI ===========\033[0m")
    print("\033[3m\033[33m*ketik 0 untuk kembali\033[0m\n")
    username = input("Buat username: ").strip()
    if username == "0":
        return
    if not username:
        print("\n\033[31mUsername tidak boleh kosong\033[0m")
        return
    if username in users:
        print("\n\033[31mUsername sudah dipakai\033[0m")
        return

    password = input("Buat password: ").strip()
    if password == "0":
        return
    if not password:
        print("\033[31mPassword tidak boleh kosong\033[0m")
        return
    # kode unik ke role
    role_ops = {"1": "admin","2": "kasir","3": "service","4": "dapur","5": "pembeli"}
    print("\n>> Pilih role:")
    for k, v in role_ops.items():
        print(f"{k}. {v.capitalize()}")
    while True:
        role_choice = input("Role \033[33m(pilih angka)\033[0m: ").strip()
        if role_choice == "0":
            return  # balik ke start_menu
        if role_choice in role_ops:
            role = role_ops[role_choice]
            break
        else:
            print("\033[31mPilihan tidak valid. Coba lagi\033[0m")

    users[username] = {"password": password, "role": role}
    save_users()
    print(f"\n\033[32mRegistrasi berhasil sebagai \033[36m{username}\033[0m \033[33m(role: {role}\033[0m)\033[0m")
# => Login
def login():
    global current_user, current_role
    while True:
        print("\n\033[44m=========== LOGIN SISTEM ===========\033[0m")
        print("\033[3m\033[33m*ketik 0 untuk kembali\033[0m\033[0m\n")
        u = input("Username: ").strip()
        if u == "0":
            return  # balik ke start_menu
        p = input("Password: ").strip()
        if u in users and users[u]["password"] == p:
            current_user = u
            current_role = users[u]["role"]
            print(f"\n\033[32mLogin berhasil sebagai \033[33m{u} \033[32m(role: \033[33m{current_role}\033[32m)\033[0m")
            return
        else:
            print("\n\033[31mLogin gagal. Coba lagi\033[0m")

def load_sales():
    try:
        with open("sales.txt", "r") as f:
            for line in f:
                try:
                    rec = json.loads(line)
                    store.sales.append(Sale(rec["items"], int(rec["total"]), rec["date"], rec["cashier"]))
                except Exception:
                    print(f"\033[33mBaris log sales rusak, dilewati: {line.strip()}\033[0m")
    except FileNotFoundError:
        pass

def load_services():
    try:
        with open("services.txt", "r") as f:
            for line in f:
                try:
                    rec = json.loads(line)
                    store.services.append(ServiceRecord(
                        lokomotif_id=rec["lokomotif_id"],
                        customer=rec["customer"],
                        service_type=rec.get("service_type", "Umum"),
                        days=int(rec["days"]),
                        total_fee=int(rec.get("total_fee", rec.get("total", 0))),
                        start_date=rec.get("start_date", rec.get("date", "")),
                        end_date=rec.get("end_date", ""),
                        officer=rec.get("officer", "")
                    ))
                except Exception:
                    print(f"\033[33mBaris log services rusak, dilewati: {line.strip()}\033[0m")
    except FileNotFoundError:
        pass

def load_food_orders():
    try:
        with open("food_orders.txt", "r") as f:
            for line in f:
                try:
                    rec = json.loads(line)
                    store.food_orders.append(FoodOrder(rec["items"], int(rec["total"]), rec["date"], rec["waiter"]))
                except Exception:
                    print(f"\033[33mBaris log food_orders rusak, dilewati: {line.strip()}\033[0m")
    except FileNotFoundError:
        pass

''' CRUD MODULES '''
def add_inventory(name: str, stock: int, price: int, category: str = "Umum"):
    # Cek duplikat nama barang
    for it in store.inventory.values():
        if it.name.lower() == name.lower():
            print("\033[31mBarang dengan nama ini sudah ada\033[0m")
            return

    # Buat ID baru
    item_id = store.gen_id("INV")
    item = InventoryItem(item_id, name, price, 0, category)  # stok awal 0
    store.inventory[item_id] = item

    # Kalau Gudang Pusat ada, stok langsung masuk ke sana
    if "W001" in store.warehouses:
        adjust_stock(item_id, "W001", stock)
    else:
        # fallback: kalau gudang belum ada, stok disimpan di field umum
        item.stock = stock

    print(f"\033[32mBarang {name} ditambahkan dengan ID {item_id}, stok awal {stock}\033[0m")

def edit_inventory(item_id: str, new_name: str = None, new_price: int = None,
                new_category: str = None, new_stock: int = None,
                delete: bool = False, reason: str = None, note: str = None):
    if item_id not in store.inventory:
        print("\033[31mBarang tidak ditemukan\033[0m")
        return

    item = store.inventory[item_id]

    # Jika delete=True, hapus barang
    if delete:
        # catat ke log penghapusan
        record = {
            "date": datetime.now().strftime("%Y-%m-%d (%H:%M)"),
            "operator": current_user,
            "item_id": item_id,
            "name": item.name,
            "stock": item.stock,
            "price": item.price,
            "reason": reason if reason else "Tidak ada alasan",
            "note": note if note else ""
        }
        with open("inventory_deletions.txt", "a") as f:
            f.write(json.dumps(record) + "\n")

        # kosongkan stok gudang
        item.stock_by_warehouse.clear()

        # hapus dari inventaris
        del store.inventory[item_id]
        print(f"\033[32m Barang {item_id} ({item.name}) berhasil dihapus \033[0m")
        return

    # Update nama
    if new_name:
        item.name = new_name

    # Update harga
    if new_price is not None:
        item.price = new_price

    # Update kategori
    if new_category:
        item.category = new_category

    # Update stok (sinkron ke Gudang Pusat)
    if new_stock is not None:
        if "W001" in store.warehouses:
            current = item.stock_by_warehouse.get("W001", 0)
            delta = new_stock - current
            adjust_stock(item_id, "W001", delta)
        else:
            item.stock = new_stock

    # Sinkronisasi stok umum dengan total stok di semua gudang
    item.stock = sum(item.stock_by_warehouse.values())

    print(f"\033[32mBarang {item_id} berhasil diperbarui\033[0m")

def add_employee(name: str, role: str):
    for emp in store.employees.values():
        if emp.name.lower() == name.lower():
            print("\033[31mKaryawan dengan nama ini sudah ada\033[0m")
            return
    emp_id = store.gen_id("EMP")
    store.employees[emp_id] = Employee(emp_id, name, role)

def add_lokomotif(name: str, service_type: str, rate_per_day: int):
    # cek duplikasi nama unit
    for lok in store.lokomotif.values():
        if lok.name.lower() == name.lower():
            print("\033[31mLokomotif dengan nama ini sudah ada\033[0m")
            return
    lok_id = store.gen_id("LOK")
    store.lokomotif[lok_id] = Lokomotif(
        id=lok_id,
        name=name,
        service_type=service_type,
        rate_per_day=rate_per_day,
        status="Tersedia")

def add_menu(name: str, stock: int, price: int):
    for menu in store.menu.values():
        if menu.name.lower() == name.lower():
            print("\033[31mMneu dengan nama ini sudah ada\033[0m")
            return
    menu_id = store.gen_id("MEN")
    store.menu[menu_id] = MenuItem(menu_id, name, stock, price)

def add_warehouse(name: str, address: str):
    wid = f"W{len(store.warehouses)+1:03}"
    store.warehouses[wid] = Warehouse(wid, name, address)
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
# Admin
def dashboard_admin():
    print("\n\033[44m=========== DASHBOARD ===========\033[0m")

    # Kondisi stok barang
    print("\n\033[34m>> Kondisi Stok Barang\033[0m")
    low_inv = False
    for it in store.inventory.values():
        if it.stock < 5:
            low_inv = True
            print(f"- {it.name}: stok tinggal {it.stock}")
    if not low_inv:
        print("- Semua stok barang aman")

    # Kondisi stok menu makanan
    print("\n\033[34m>> Kondisi Stok Menu Makanan\033[0m")
    low_menu = False
    for m in store.menu.values():
        if m.stock < 5:
            low_menu = True
            print(f"- {m.name}: stok tinggal {m.stock}")
    if not low_menu:
        print("- Semua stok menu aman")

    # Ringkasan transaksi
    total_sales = sum(s.total for s in store.sales)
    total_service = sum(r.total_fee for r in store.services)
    total_food = sum(o.total for o in store.food_orders)
    print(f"- Penjualan Barang   : {len(store.sales)} transaksi | Total: {format_rupiah(total_sales)}")
    print(f"- Service Lokomotif  : {len(store.services)} transaksi | Total: {format_rupiah(total_service)}")
    print(f"- Pemesanan Makanan  : {len(store.food_orders)} pesanan | Total: {format_rupiah(total_food)}")
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

    # Lokomotif terlaris
    lokomotif_count = {}
    for r in store.services:
        lok = store.lokomotif.get(r.lokomotif_id)
        if lok:
            lokomotif_count[lok.name] = lokomotif_count.get(lok.name, 0) + 1
    top_items(lokomotif_count, "Lokomotif terlaris", "kali diservis")

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
# Gudang
def dashboard_gudang():
    print("\n\033[44m=========== DASHBOARD GUDANG ===========\033[0m")

    # Ringkasan gudang
    print(f"Jumlah gudang: {len(store.warehouses)}")
    if not store.warehouses:
        print("\033[33mBelum ada gudang terdaftar\033[0m")
    else:
        for w in store.warehouses.values():
            print(f"- {w.warehouse_id}: {w.name} ({w.address})")

    # Ringkasan stok per gudang
    print("\n\033[34m>> Stok per Gudang\033[0m")
    for item in store.inventory.values():
        print(f"\n{item.name}:")
        if not item.stock_by_warehouse:
            print("  - Belum ada distribusi stok")
        else:
            for wid, qty in item.stock_by_warehouse.items():
                wh = store.warehouses.get(wid)
                wh_name = wh.name if wh else wid
                print(f"  - {wh_name}: {qty} unit")
'---------------------------------------------------------------------------------------------------------- part 4 -------------------------------------------'

''' MENUS '''
# >> Module menus
# Inventaris
def inventory_menu():
    while True:
        h = head("KELOLA INVENTARIS")
        ops = {
            "1": "Lihat Inventaris",
            "2": "Tambah barang",
            "3": "Update stok (via Gudang)",
            "4": "Update harga",
            "5": "Hapus barang",
            "0": "Kembali"}
        choice = input_menu("Data Inventaris", ops)

        if choice == "1":
            print_inventory()
            pause()
        elif choice == "2":
            name = input("Nama barang: ").strip()
            stock = input_int("Stok awal: ", min_val=0)
            price = input_int("Harga per unit: ", min_val=0)
            add_inventory(name, stock, price)
            print(f"\n\033[33mBarang {name} berhasil ditambahkan\033[0m")
        elif choice == "3":
            print("\033[33mUpdate stok hanya bisa dilakukan lewat menu Gudang untuk konfirmasi.\033[0m")
            pause()
        elif choice == "4":   # update harga
            print_inventory()
            item_id = input("ID barang: ").strip().upper()
            if item_id not in store.inventory:
                print("\n\033[31mID tidak ditemukan\033[0m")
                continue
            price = input_int("Harga baru: ", min_val=0)
            store.inventory[item_id].price = price
            print("\n\033[32mHarga diperbarui\033[0m")
        elif choice == "5":   # hapus barang + alasan uv.3.4
            print_inventory()
            item_id = input("ID barang yang dihapus: ").strip().upper()
            if item_id in store.inventory:
                alasan_ops = {"1": "Rusak", "2": "Hilang", "3": "Kadaluarsa", "4": "Lainnya"}
                alasan_choice = input_menu("Alasan penghapusan", alasan_ops)
                alasan = alasan_ops.get(alasan_choice, "Lainnya")
                note = ""
                if alasan == "Lainnya":
                    note = input("Keterangan tambahan: ").strip()
                confirm = input(f"Yakin hapus {store.inventory[item_id].name}? (y/n): ").lower()
                if confirm == "y":
                    # catat ke log
                    record = {
                        "date": datetime.now().strftime("%Y-%m-%d (%H:%M)"),
                        "operator": current_user,
                        "item_id": item_id,
                        "name": store.inventory[item_id].name,
                        "stock": store.inventory[item_id].stock,
                        "price": store.inventory[item_id].price,
                        "reason": alasan,
                        "note": note
                    }
                    with open("inventory_deletions.txt", "a") as f:
                        f.write(json.dumps(record) + "\n")

                    # kosongkan stok di gudang
                    store.inventory[item_id].stock_by_warehouse.clear()

                    # hapus dari inventaris
                    del store.inventory[item_id]
                    print("\033[32mBarang berhasil dihapus\033[0m")
                else:
                    print("\033[33mPenghapusan dibatalkan\033[0m")
            else:
                print("\033[31mID tidak ditemukan\033[0m")
        elif choice == "0":
            return
# Gudang
def warehouse_menu():
    while True:
        h = head("KELOLA GUDANG")
        ops = {
            "1": "Daftar gudang",
            "2": "Tambah gudang",
            "3": "Mutasi stok antar gudang",
            "4": "Konfirmasi status barang",
            "5": "Lihat stok per gudang",
            "0": "Kembali"}
        choice = input_menu("Menu Gudang", ops)
        if choice == "1":
            print("\nDaftar Gudang:")
            for w in store.warehouses.values():
                print(f"- {w.warehouse_id}: {w.name} ({w.address})")
            pause()
        elif choice == "2":
            name = input("Nama gudang: ").strip()
            address = input("Alamat gudang: ").strip()
            add_warehouse(name, address)
        elif choice == "3":
            item_id = input("\nID barang: ").strip().upper()
            from_wh = input("Gudang asal (ID): ").strip().upper()
            to_wh = input("Gudang tujuan (ID): ").strip().upper()
            qty = input_int("Jumlah transfer: ", min_val=1)
            transfer_stock(item_id, from_wh, to_wh, qty)
        elif choice == "4":   # konfirmasi status barang
            print_inventory()
            item_id = input("\nID barang: ").strip().upper()
            if item_id not in store.inventory:
                print(f"\033[31mID \033[32m{item_id} \033[33mtidak ditemukan\033[0m")
                continue

            status_ops = {"1": "Siap Jual", "2": "Disimpan", "3": "Rusak/Hilang"}
            status_choice = input_menu("Konfirmasi status", status_ops)
            status = status_ops.get(status_choice, "\033[32mDisimpan\033[0m")

            store.inventory[item_id].status = status
            print(f"\033[32mBarang {item_id} sekarang berstatus {status}\033[0m")
        elif choice == "5":   # lihat stok per gudang
            dashboard_gudang()
            pause()

        elif choice == "0":
            return
# Karyawan
def employee_menu():
    while True:
        h = head("KELOLA KARYAWAN")
        ops = {"1": "Lihat karyawan", "2": "Tambah karyawan", "3": "Ubah jabatan", "4": "Hapus Karyawan","0": "Kembali"}
        choice = input_menu("Data Karyawan", ops)
        if choice == "1":
            print_employees()
            pause()
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
        elif choice == "3":
            print_employees()
            emp_id = input("ID karyawan: ").strip().upper()
            if emp_id not in store.employees:
                print(f"\n\033[31mID {emp_id} tidak ditemukan\033[0m")
                continue
            role = input("Jabatan baru: ").strip()
            store.employees[emp_id].role = role
            print(f"\033[32mJabatan {role} telah diperbarui\033[0m")
        elif choice == "4":
            emp_id = input("ID karyawan: ").strip().upper()
            if emp_id in store.employees:
                del store.employees[emp_id]
                print("\033[32mKaryawan dihapus\033[0m")
            else:
                print("\033[31mID tidak ditemukan\033[0m")
        elif choice == "0":
            return
'---------------------------------------------------------------------------------------------------------- part 4.1 -------------------------------------------'

# Penjualan
def sales_menu():
    while True:
        h = head("KELOLA PENJUALAN")
        ops = {"1": "Lihat inventaris", "2": "Buat transaksi penjualan", "3": "Lihat riwayat penjualan", "0": "Kembali"}
        p = input_menu("Data Penjualan", ops)
        if p == "1":
            print_inventory()
            pause()
        elif p =="2": # (UV.3.3)
            cart=[]
            while True:
                print('\033[33m\033[3m*enter jika selesai\033[0m')
                item_id=input("\nID barang: ").strip().upper()
                if item_id=="": break
                if item_id not in store.inventory: print(f"\n\033[31mID {item_id} tidak ada\033[0m"); continue
                qty=input_int("Jumlah: ",min_val=1)
                if qty>store.inventory[item_id].stock: print("\n\033[33mStok kurang\033[0m"); continue
                cart.append((item_id,qty))
            if not cart: print("\n\033[31mKeranjang kosong. Ulangi input barang\033[0m"); continue

            total=sum(store.inventory[i].price*q for i,q in cart)
            for i,q in cart: store.inventory[i].stock-=q

            sale=Sale(cart,total,datetime.now().strftime("%Y-%m-%d (%H:%M)"),current_user)
            store.sales.append(sale)

            # Simpan ke file
            with open("sales.txt", "a") as f:
                record = {
                    "date": sale.date,
                    "cashier": sale.cashier,
                    "items": sale.items,
                    "total": sale.total}
                f.write(json.dumps(record) + "\n")
            print(f"Transaksi berhasil. Total: {format_rupiah(total)}")
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
# Service
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
            print_lokomotif()
            lok_id = input("ID lokomotif: ").strip().upper()
            lok = store.lokomotif.get(lok_id)
            if not lok or lok.status != "Tersedia":
                print("\033[31mLokomotif tidak tersedia\033[0m")
                continue

            customer = input("Nama customer: ").strip()
            days = input_int("Durasi (hari): ", min_val=1)

            # pilih sparepart dari inventory
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
                store.inventory[part_id].stock -= qty
                parts_used.append(f"{store.inventory[part_id].name} x{qty}")
                parts_cost += store.inventory[part_id].price * qty

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

            with open("services.txt", "a") as f:
                f.write(json.dumps(record.__dict__) + "\n")

            print("\n\033[30m=== NOTA SERVICE PT.AMOT \033[0m")
            print(f"Customer      : {customer}")
            print(f"Lokomotif     : {lok.name} (ID: {lok_id})")
            print(f"Jenis Service : {lok.service_type}")
            print(f"Tgl Mulai     : {record.start_date}")
            print(f"Tgl Selesai   : {record.end_date}")
            print(f"Sparepart     : {', '.join(parts_used) if parts_used else '-'}")
            print(f"Biaya Sparepart: {format_rupiah(parts_cost)}")
            print(f"Biaya Jasa    : {format_rupiah(jasa)}")
            print(f"Total Biaya   : {format_rupiah(total_fee)}")
        # Selesaikan service
        elif p == "3":
            if not store.services:
                print("\n\033[33mBelum ada transaksi service\033[0m")
                continue
            print("\n>> Transaksi Service:")
            for idx, r in enumerate(store.services, 1):
                lok = store.lokomotif.get(r.lokomotif_id)
                status = "\033[33mDiservis\033[0m" if lok and lok.status == "Diservis" else "\033[32mTersedia/Selesai\033[0m"
                print(f"{idx}. {r.customer} | {lok.name if lok else r.lokomotif_id} | {r.days} hari | {format_rupiah(r.total_fee)} | Status: {status}")
            idx = input_int("Pilih nomor transaksi yang selesai: ", min_val=1, max_val=len(store.services))
            r = store.services[idx - 1]
            if r.lokomotif_id in store.lokomotif:
                store.lokomotif[r.lokomotif_id].status = "Selesai"
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
'---------------------------------------------------------------------------------------------------------- part 4.2 -------------------------------------------'

# Pesan Makan 
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
                # langsung kurangi stok
                store.menu[menu_id].stock -= qty
                cart.append((menu_id, qty))

            if not cart:
                print("\033[33mKeranjang kosong\033[0m \033[47mBatal\033[0m")
                return

            total = sum(store.menu[mid].price * q for mid, q in cart)

            # Buat objek FoodOrder dengan field tambahan
            order = FoodOrder(
                items=cart,
                total=total,
                date=datetime.now().strftime("%Y-%m-%d (%H:%M)"),
                waiter=current_user,
                customer_name=customer_name,
                table_number=table_number
            )
            store.food_orders.append(order)

            # Simpan ke file dalam format JSON
            with open("food_orders.txt", "a") as f:
                f.write(json.dumps(order.__dict__) + "\n")

            # Cetak nota
            print("\n\033[30m=== NOTA PEMBELIAN MAKANAN PT.AMOT \033[0m")
            print(f"Customer      : {order.customer_name}")
            print(f"Meja          : {order.table_number}")
            print(f"Waiter        : {order.waiter}")
            print(f"Tanggal Pesan : {order.date}")
            detail = [f"{store.menu[mid].name} x{q}" for mid, q in order.items]
            print(f"Pesanan       : {'; '.join(detail)}")
            print(f"Total Biaya   : {format_rupiah(order.total)}")
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
# Laporan
def laporan_detail():
    head("LAPORAN DETAIL")

    # Barang terlaris
    counter = {}
    for s in store.sales:
        for i, q in s.items:
            it = store.inventory.get(i)
            if it:
                counter[it.name] = counter.get(it.name, 0) + q
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
    top_items(food_count, "Menu favorit", "porsi")
'---------------------------------------------------------------------------------------------------------- part 4.3 -------------------------------------------'

# >> Main Menu 
def main_menu():
    global current_user, current_role
    while True:
        if not current_user or not current_role:  # Session safety
            print("\n\033[31mSession tidak valid. Silakan login kembali.\033[0m")
            return
        if current_role == "admin":
            ops = {
                "1": "Inventaris Barang",
                "2": "Manajemen Karyawan",
                "3": "Penjualan Barang",
                "4": "Service Mobil",
                "5": "Pemesanan Makanan",
                "6": "Gudang",
                "7": "Dashboard Hybrid",
                "8": "Hapus Akun",
                "9": "Logout"}
            choice = input_menu("MENU UTAMA (Admin)", ops)
            if choice == "1": inventory_menu()
            elif choice == "2": employee_menu()
            elif choice == "3": sales_menu()
            elif choice == "4": service_menu()
            elif choice == "5": food_menu()
            elif choice == "6": warehouse_menu()
            elif choice == "7": dashboard()
            elif choice == "8": delete_user()
            elif choice == "9":
                current_user, current_role = None, None
                print("\n\033[32m Logout berhasil \033[0m")
                return
            elif choice == "0": sys.exit(0)

        elif current_role == "kasir":
            ops = {
                "1": "Penjualan Barang",
                "2": "Dashboard Penjualan",
                "9": "Logout"}
            choice = input_menu("MENU UTAMA (Kasir)", ops)
            if choice == "1": sales_menu()
            elif choice == "2": dashboard_kasir()
            elif choice == "9":
                current_user, current_role = None, None
                print("\n\033[32mLogout berhasil\033[0m")
                return
            elif choice == "0": sys.exit(0)

        elif current_role == "service":
            ops = {
                "1": "Service Mobil",
                "2": "Dashboard Service",
                "9": "Logout"
            }
            choice = input_menu("MENU UTAMA (Service)", ops)
            if choice == "1": service_menu()
            elif choice == "2": dashboard_service()
            elif choice == "9":
                current_user, current_role = None, None
                print("\n\033[32mLogout berhasil\033[0m")
                return
            elif choice == "0": sys.exit(0)

        elif current_role == "dapur":
            ops = {
                "1": "Menu Makanan",
                "2": "Dashboard Dapur",
                "9": "Logout"
            }
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
                "1": "Lihat Inventaris Barang",
                "2": "Kelola Gudang",
                "3": "Dashboard Gudang",
                "9": "Logout"}
            choice = input_menu("MENU UTAMA (Gudang)", ops)
            if choice == "1":
                # hanya lihat inventaris
                print_inventory()
                pause()
            elif choice == "2":
                warehouse_menu()   # menu gudang
            elif choice == "3":
                dashboard_gudang()
                pause()
            elif choice == "9":
                current_user, current_role = None, None
                print("\n\033[32mLogout berhasil\033[0m")
                return
            elif choice == "0":
                sys.exit(0)

        elif current_role == "pembeli":
            ops = {
                "1": "Lihat Menu Makanan",
                "2": "Pesan Makanan",
                "3": "Lihat Pesanan",
                "9": "Logout"
            }
            choice = input_menu("MENU UTAMA (Pembeli)", ops)
            if choice == "1": print_menu_items()
            elif choice == "2": food_menu()
            elif choice == "3": laporan_detail()  # atau tampilkan pesanan pembeli
            elif choice == "9":
                current_user, current_role = None, None
                print("\n\033[32mLogout berhasil\033[0m")
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
                return True    # keluar dari start_menu, lanjut ke main
        elif choice == "0":
            print("\n\033[32mTerima kasih sudah menggunakan sistem ini\033[0m")
            sys.exit(0)

# >> Main
def main():
    try:
        if start_menu():       # login dulu
            seed_data()        # baru isi data
            load_sales()
            load_services()
            load_food_orders()
            main_menu()        # masuk ke menu utama
    except KeyboardInterrupt:
        print("\n\033[41m Program dihentikan oleh user \033[0m")
        sys.exit(0)

''' ENTRY POINT '''
if __name__ == "__main__":
    main()
'---------------------------------------------------------------------------------------------------------- part 4.4 -------------------------------------------'

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