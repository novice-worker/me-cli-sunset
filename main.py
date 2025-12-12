# Library standar
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

# Tentukan WIDTH sesuai terminal, maksimal 80
columns, _ = shutil.get_terminal_size(fallback=(80, 20))
WIDTH = min(columns, 80)

# Menu options
MENU_OPTIONS = [
    ("1", "Login/Ganti akun"),
    ("2", "Lihat Paket Saya"),
    ("3", "Beli Paket 🔥 HOT 🔥"),
    ("4", "Beli Paket 🔥 HOT-2 🔥"),
    ("5", "Beli Paket Berdasarkan Option Code"),
    ("6", "Beli Paket Berdasarkan Family Code"),
    ("7", "Beli Semua Paket di Family Code (loop)"),
    ("8", "Riwayat Transaksi"),
    ("9", "Family Plan/Akrab Organizer"),
    ("10", "Circle"),
    ("11", "Store Segments"),
    ("12", "Store Family List"),
    ("13", "Store Packages"),
    ("14", "Redemables"),
    ("R", "Register"),
    ("N", "Notifikasi"),
    ("V", "Validate msisdn"),
    ("00", "Bookmark Paket"),
    ("99", "Tutup aplikasi")
]

# Fungsi menampilkan header profil
def show_profile_header(profile):
    print("=" * WIDTH)
    expired_at_dt = datetime.fromtimestamp(profile["balance_expired_at"]).strftime("%d-%m-%Y")
    print(f"Nomor: {profile['number']} | Type: {profile['subscription_type']}".center(WIDTH))
    print(f"Pulsa: Rp {profile['balance']} | Aktif sampai: {expired_at_dt}".center(WIDTH))
    print(f"{profile['point_info']}".center(WIDTH))
    print("=" * WIDTH)

# Fungsi utama menampilkan menu
def show_main_menu(profile):
    clear_screen()
    show_profile_header(profile)

    print("Menu:")
    for key, desc in MENU_OPTIONS:
        print(f"{key}. {desc}")
    
    print("-" * WIDTH)

def main():
    while True:
        # --- a. Periksa pengguna aktif ---
        active_user = AuthInstance.get_active_user()

        if active_user:
            # Ambil info user
            balance_info = get_balance(active_user)
            tiering_info = get_tiering_info(active_user)

            # Buat profile dictionary
            profile = {
                "number": active_user["number"],
                "subscription_type": active_user["subscription_type"],
                "balance": balance_info["balance"],
                "balance_expired_at": balance_info["expired_at"],
                "point_info": tiering_info.get("points", "0")
            }
        else:
            # Jika tidak ada user aktif, tampilkan menu login/account
            show_account_menu()
            continue  # Kembali ke loop utama setelah login

        # --- b. Tampilkan menu ---
        show_main_menu(profile)
        choice = input("Pilih menu: ").strip()

        # --- c. Routing pilihan menu ---
        if choice == "1":
            show_account_menu()
        elif choice == "2":
            fetch_my_packages()
        elif choice == "3":
            show_hot_menu()
        elif choice == "4":
            show_hot_menu2()
        elif choice == "5":
            show_package_details()
        elif choice == "6":
            get_packages_by_family()
        elif choice == "7":
            purchase_by_family(start_option=True, decoy=True, pause_time=1, delay=0.5)
        elif choice == "8":
            show_transaction_history()
        elif choice == "9":
            show_family_info()
        elif choice == "10":
            show_circle_info()
        elif choice == "11":
            show_store_segments_menu(is_enterprise=True)
        elif choice == "12":
            show_family_list_menu(profile['subscription_type'], is_enterprise=True)
        elif choice == "13":
            show_store_packages_menu(profile['subscription_type'], is_enterprise=True)
        elif choice == "14":
            show_redeemables_menu(is_enterprise=True)
        elif choice == "00":
            show_bookmark_menu()
        elif choice.upper() == "R":
            dukcapil()
        elif choice.upper() == "V":
            validate_msisdn()
        elif choice.upper() == "N":
            show_notification_menu()
        elif choice.upper() == "S":
            enter_sentry_mode()
        elif choice == "99":
            print("Keluar aplikasi...")
            sys.exit(0)
        else:
            print("Pilihan tidak valid!")
            pause()