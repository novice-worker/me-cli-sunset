# ================= Library & Import =================
import sys
import json
import shutil
from datetime import datetime
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Service internal
from app.service.git import check_for_updates
from app.service.auth import AuthInstance
from app.service.sentry import enter_sentry_mode

# Client internal
from app.client.engsel import get_balance, get_tiering_info
from app.client.famplan import validate_msisdn
from app.client.registration import dukcapil

# Utility
from app.menus.util import clear_screen, pause

# Menu utama
from app.menus.payment import show_transaction_history
from app.menus.bookmark import show_bookmark_menu
from app.menus.account import show_account_menu
from app.menus.package import fetch_my_packages, get_packages_by_family, show_package_details
from app.menus.hot import show_hot_menu, show_hot_menu2
from app.menus.purchase import purchase_by_family
from app.menus.famplan import show_family_info
from app.menus.circle import show_circle_info
from app.menus.notification import show_notification_menu

# Menu store
from app.menus.store.segments import show_store_segments_menu
from app.menus.store.search import show_family_list_menu, show_store_packages_menu
from app.menus.store.redemables import show_redeemables_menu

# ================= Konfigurasi =================
# Tentukan lebar tampilan sesuai terminal, maksimal 80
columns, _ = shutil.get_terminal_size(fallback=(80, 20))
WIDTH = min(columns, 80)

# Menu options (Bahasa Indonesia)
MENU_OPTIONS = [
    ("1", "Login / Ganti Akun"),
    ("2", "Lihat Paket Saya"),
    ("3", "Beli Paket 🔥 HOT 🔥"),
    ("4", "Beli Paket 🔥 HOT-2 🔥"),
    ("5", "Beli Paket Berdasarkan Kode Opsi"),
    ("6", "Beli Paket Berdasarkan Kode Family"),
    ("7", "Beli Semua Paket di Family Code (loop)"),
    ("8", "Riwayat Transaksi"),
    ("9", "Family Plan / Akrab Organizer"),
    ("10", "Circle"),
    ("11", "Store Segments"),
    ("12", "Store Family List"),
    ("13", "Store Packages"),
    ("14", "Redemables"),
    ("R", "Register"),
    ("N", "Notifikasi"),
    ("V", "Validasi MSISDN"),
    ("00", "Bookmark Paket"),
    ("99", "Tutup Aplikasi")
]

# ================= Helper Functions =================
def tanya_ya_tidak(prompt):
    return input(f"{prompt} (y/n): ").strip().lower() == 'y'

def tanya_angka(prompt, default=0):
    try:
        return int(input(f"{prompt}: ").strip())
    except ValueError:
        return default

# ================= Header & Menu =================
def tampilkan_header(profile):
    print("=" * WIDTH)
    expired_at_dt = datetime.fromtimestamp(profile["balance_expired_at"]).strftime("%d-%m-%Y")
    print(f"Nomor: {profile['number']} | Tipe: {profile['subscription_type']}".center(WIDTH))
    print(f"Pulsa: Rp {profile['balance']} | Aktif sampai: {expired_at_dt}".center(WIDTH))
    print(f"{profile['point_info']}".center(WIDTH))
    print("=" * WIDTH)

def tampilkan_menu(profile):
    clear_screen()
    tampilkan_header(profile)
    print("Menu:")
    for key, desc in MENU_OPTIONS:
        print(f"{key}. {desc}")
    print("-" * WIDTH)

# ================= Main Loop =================
def main():
    while True:
        pengguna_aktif = AuthInstance.get_active_user()

        if pengguna_aktif:
            # Ambil info balance & tiering
            balance_info = get_balance(pengguna_aktif)
            saldo_tersisa = balance_info.get("balance")
            expired_at = balance_info.get("expired_at")
            
            point_info = "Points: N/A | Tier: N/A"
            if pengguna_aktif["subscription_type"] == "PREPAID":
                tiering_data = get_tiering_info(pengguna_aktif)
                tier = tiering_data.get("tier", 0)
                current_point = tiering_data.get("current_point", 0)
                point_info = f"Points: {current_point} | Tier: {tier}"

            profile = {
                "number": pengguna_aktif["number"],
                "subscriber_id": pengguna_aktif.get("subscriber_id"),
                "subscription_type": pengguna_aktif["subscription_type"],
                "balance": saldo_tersisa,
                "balance_expired_at": expired_at,
                "point_info": point_info
            }

            # Tampilkan menu
            tampilkan_menu(profile)
            pilihan = input("Pilih menu: ").strip()

            # ================= Routing Menu =================
            if pilihan.lower() == "t":
                pause()
            elif pilihan == "1":
                nomor_terpilih = show_account_menu()
                if nomor_terpilih:
                    AuthInstance.set_active_user(nomor_terpilih)
                else:
                    print("Tidak ada pengguna dipilih atau gagal memuat user.")
                continue
            elif pilihan == "2":
                fetch_my_packages()
            elif pilihan == "3":
                show_hot_menu()
            elif pilihan == "4":
                show_hot_menu2()
            elif pilihan == "5":
                kode_opsi = input("Masukkan kode opsi (atau '99' untuk batal): ")
                if kode_opsi != "99":
                    show_package_details(kode_opsi)
            elif pilihan == "6":
                kode_family = input("Masukkan kode family (atau '99' untuk batal): ")
                if kode_family != "99":
                    get_packages_by_family(kode_family)
            elif pilihan == "7":
                kode_family = input("Masukkan kode family (atau '99' untuk batal): ")
                if kode_family != "99":
                    start_option = tanya_angka("Mulai pembelian dari nomor opsi (default 1)", 1)
                    pakai_decoy = tanya_ya_tidak("Gunakan paket decoy?")
                    pause_setelah_berhasil = tanya_ya_tidak("Pause setelah setiap pembelian sukses?")
                    delay_detik = tanya_angka("Delay antar pembelian (detik, 0 jika tanpa delay)", 0)
                    purchase_by_family(kode_family, pakai_decoy, pause_setelah_berhasil, delay_detik, start_option)
            elif pilihan == "8":
                show_transaction_history()
            elif pilihan == "9":
                show_family_info()
            elif pilihan == "10":
                show_circle_info()
            elif pilihan == "11":
                is_enterprise = tanya_ya_tidak("Apakah store enterprise?")
                show_store_segments_menu(is_enterprise)
            elif pilihan == "12":
                is_enterprise = tanya_ya_tidak("Apakah enterprise?")
                show_family_list_menu(profile['subscription_type'], is_enterprise)
            elif pilihan == "13":
                is_enterprise = tanya_ya_tidak("Apakah enterprise?")
                show_store_packages_menu(profile['subscription_type'], is_enterprise)
            elif pilihan == "14":
                is_enterprise = tanya_ya_tidak("Apakah enterprise?")
                show_redeemables_menu(is_enterprise)
            elif pilihan == "00":
                show_bookmark_menu()
            elif pilihan.lower() == "r":
                msisdn = input("Masukkan MSISDN (628xxxx): ")
                nik = input("Masukkan NIK: ")
                kk = input("Masukkan KK: ")
                res = dukcapil(msisdn, kk, nik)
                print(json.dumps(res, indent=2))
                pause()
            elif pilihan.lower() == "v":
                msisdn = input("Masukkan MSISDN yang ingin divalidasi (628xxxx): ")
                res = validate_msisdn(msisdn)
                print(json.dumps(res, indent=2))
                pause()
            elif pilihan.lower() == "n":
                show_notification_menu()
            elif pilihan.lower() == "s":
                enter_sentry_mode()
            elif pilihan == "99":
                print("Keluar aplikasi...")
                sys.exit(0)
            else:
                print("Pilihan tidak valid! Silakan coba lagi.")
                pause()
        else:
            # Tidak ada pengguna aktif
            nomor_terpilih = show_account_menu()
            if nomor_terpilih:
                AuthInstance.set_active_user(nomor_terpilih)
            else:
                print("Tidak ada pengguna dipilih atau gagal memuat user.")

# ================= Entry Point =================
if __name__ == "__main__":
    try:
        print("Memeriksa pembaruan...")
        perlu_update = check_for_updates()
        if perlu_update:
            pause()
        main()
    except KeyboardInterrupt:
        print("\nKeluar dari aplikasi.")