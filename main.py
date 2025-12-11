from dotenv import load_dotenv
load_dotenv()

import sys, json, time
from datetime import datetime
from colorama import init, Fore, Style

from app.service.git import check_for_updates
from app.menus.util import clear_screen, pause
from app.client.engsel import get_balance, get_tiering_info
from app.client.famplan import validate_msisdn
from app.menus.payment import show_transaction_history
from app.service.auth import AuthInstance
from app.menus.bookmark import show_bookmark_menu
from app.menus.account import show_account_menu
from app.menus.package import fetch_my_packages, get_packages_by_family, show_package_details
from app.menus.hot import show_hot_menu, show_hot_menu2
from app.service.sentry import enter_sentry_mode
from app.menus.purchase import purchase_by_family
from app.menus.famplan import show_family_info
from app.menus.circle import show_circle_info
from app.menus.notification import show_notification_menu
from app.menus.store.segments import show_store_segments_menu
from app.menus.store.search import show_family_list_menu, show_store_packages_menu
from app.menus.store.redemables import show_redeemables_menu
from app.client.registration import dukcapil

init(autoreset=True)
WIDTH = 60

# ---------- UTILITIES ----------

def progress_bar(current, total, length=20):
    filled = int(length * current / total) if total else 0
    return "[" + "#" * filled + "-" * (length - filled) + "]"

def fetch_with_feedback(func, *args, **kwargs):
    print(Fore.YELLOW + "Fetching data... Please wait", end="", flush=True)
    for _ in range(3):
        time.sleep(0.3)
        print(".", end="", flush=True)
    print()
    return func(*args, **kwargs)

# ---------- MENU DISPLAY ----------

def show_main_menu(profile):
    clear_screen()
    
    expired_at_dt = datetime.fromtimestamp(profile["balance_expired_at"]).strftime("%Y-%m-%d")
    
    # Header Profil
    print(Fore.CYAN + "=" * WIDTH)
    print(Fore.YELLOW + f"Device: {profile.get('device_name','N/A')}".center(WIDTH))
    print(Fore.YELLOW + f"Nomor: {profile['number']} | Type: {profile['subscription_type']}".center(WIDTH))
    print(Fore.GREEN + f"Pulsa: Rp {profile['balance']} | Aktif sampai: {expired_at_dt}".center(WIDTH))
    
    # Tier & Points
    tier_info = profile.get("point_info", "Points: N/A | Tier: N/A")
    if "Tier" in tier_info:
        try:
            tier_num = int(tier_info.split("Tier:")[1].strip())
        except:
            tier_num = 0
        bar = progress_bar(tier_num, 10)
        tier_info += f" {bar}"
    print(Fore.MAGENTA + tier_info.center(WIDTH))
    
    # Status Langganan
    subscription_status = profile.get("subscription_status","N/A")
    status_color = Fore.GREEN if subscription_status=="ACTIVE" else Fore.RED
    print(status_color + f"Status: {subscription_status}".center(WIDTH))
    
    # Prio / Flex Balance
    prio_balance = profile.get("prio_flex_balance", {}).get("remaining",0)
    print(Fore.CYAN + f"Prio/Flex Balance: {prio_balance}".center(WIDTH))
    
    print(Fore.CYAN + "=" * WIDTH)
    
    # Menu items
    menu_items = [
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
    
    for key, desc in menu_items:
        # Highlight HOT menu
        if "HOT" in desc:
            print(Fore.RED + f"{key}. {desc}")
        else:
            print(Fore.BLUE + f"{key}. {desc}")
    
    print(Fore.CYAN + "-" * WIDTH)
    return input(Fore.LIGHTYELLOW_EX + "Pilih menu: ")

# ---------- MAIN LOOP ----------

def main():
    while True:
        active_user = AuthInstance.get_active_user()
        if active_user:
            # Ambil balance & tier
            balance_data = fetch_with_feedback(get_balance, AuthInstance.api_key, active_user["tokens"]["id_token"])
            balance_remaining = balance_data.get("remaining", 0)
            balance_expired_at = balance_data.get("expired_at", int(time.time()))
            
            point_info = "Points: N/A | Tier: N/A"
            if active_user["subscription_type"] == "PREPAID":
                tier_data = fetch_with_feedback(get_tiering_info, AuthInstance.api_key, active_user["tokens"])
                tier = tier_data.get("tier", 0)
                points = tier_data.get("current_point", 0)
                point_info = f"Points: {points} | Tier: {tier}"
            
            # Profil lengkap termasuk raw info
            profile = {
                "number": active_user["number"],
                "subscriber_id": active_user["subscriber_id"],
                "subscription_type": active_user["subscription_type"],
                "balance": balance_remaining,
                "balance_expired_at": balance_expired_at,
                "point_info": point_info,
                "device_name": active_user.get("device_name","N/A"),
                "subscription_status": balance_data.get("subscription_status","N/A"),
                "prio_flex_balance": balance_data.get("prio_flex_balance", {}),
            }
            
            choice = show_main_menu(profile)
            
            # Menu Handling
            if choice == "1":
                sel_user = show_account_menu()
                if sel_user:
                    AuthInstance.set_active_user(sel_user)
            elif choice == "2":
                fetch_my_packages()
            elif choice == "3":
                show_hot_menu()
            elif choice == "4":
                show_hot_menu2()
            elif choice == "5":
                option_code = input("Enter option code (or '99' to cancel): ")
                if option_code != "99":
                    show_package_details(AuthInstance.api_key, active_user["tokens"], option_code, False)
            elif choice == "6":
                family_code = input("Enter family code (or '99' to cancel): ")
                if family_code != "99":
                    get_packages_by_family(family_code)
            elif choice == "7":
                family_code = input("Enter family code (or '99' to cancel): ")
                if family_code == "99": continue
                start_option = input("Start purchasing from option number (default 1): ")
                try: start_option = int(start_option)
                except: start_option = 1
                use_decoy = input("Use decoy package? (y/n): ").lower() == 'y'
                pause_on_success = input("Pause on each successful purchase? (y/n): ").lower() == 'y'
                delay_sec = input("Delay seconds between purchases (0 for no delay): ")
                try: delay_sec = int(delay_sec)
                except: delay_sec = 0
                purchase_by_family(family_code, use_decoy, pause_on_success, delay_sec, start_option)
            elif choice == "8":
                show_transaction_history(AuthInstance.api_key, active_user["tokens"])
            elif choice == "9":
                show_family_info(AuthInstance.api_key, active_user["tokens"])
            elif choice == "10":
                show_circle_info(AuthInstance.api_key, active_user["tokens"])
            elif choice == "11":
                is_ent = input("Is enterprise store? (y/n): ").lower() == 'y'
                show_store_segments_menu(is_ent)
            elif choice == "12":
                is_ent = input("Is enterprise? (y/n): ").lower() == 'y'
                show_family_list_menu(profile['subscription_type'], is_ent)
            elif choice == "13":
                is_ent = input("Is enterprise? (y/n): ").lower() == 'y'
                show_store_packages_menu(profile['subscription_type'], is_ent)
            elif choice == "14":
                is_ent = input("Is enterprise? (y/n): ").lower() == 'y'
                show_redeemables_menu(is_ent)
            elif choice == "00":
                show_bookmark_menu()
            elif choice == "99":
                print(Fore.RED + "Exiting application...")
                sys.exit(0)
            elif choice.lower() == "r":
                msisdn = input("Enter msisdn (628xxxx): ")
                nik = input("Enter NIK: ")
                kk = input("Enter KK: ")
                res = dukcapil(AuthInstance.api_key, msisdn, kk, nik)
                print(json.dumps(res, indent=2))
                pause()
            elif choice.lower() == "v":
                msisdn = input("Enter msisdn (628xxxx): ")
                res = validate_msisdn(AuthInstance.api_key, active_user["tokens"], msisdn)
                print(json.dumps(res, indent=2))
                pause()
            elif choice.lower() == "n":
                show_notification_menu()
            elif choice.lower() == "s":
                enter_sentry_mode()
            else:
                print(Fore.RED + "Invalid choice. Please try again.")
                pause()
        else:
            sel_user = show_account_menu()
            if sel_user:
                AuthInstance.set_active_user(sel_user)
            else:
                print(Fore.RED + "No user selected or failed to load user.")

# ---------- ENTRY POINT ----------

if __name__ == "__main__":
    try:
        print(Fore.CYAN + "Checking for updates...")
        if check_for_updates():
            pause()
        main()
    except KeyboardInterrupt:
        print(Fore.RED + "\nExiting application...")