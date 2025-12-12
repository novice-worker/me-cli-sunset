from app.menus.util import clear_screen
from app.client.engsel import get_notification_detail, dashboard_segments
from app.service.auth import AuthInstance
from datetime import datetime

WIDTH = 55

def show_notification_menu():
    # Mapping bulan ke bahasa Indonesia
    bulan_id = {
        1: "Januari", 2: "Februari", 3: "Maret", 4: "April",
        5: "Mei", 6: "Juni", 7: "Juli", 8: "Agustus",
        9: "September", 10: "Oktober", 11: "November", 12: "Desember"
    }

    in_notification_menu = True
    while in_notification_menu:
        clear_screen()
        print("Sedang mengambil notifikasi terbaru...")

        api_key = AuthInstance.api_key
        tokens = AuthInstance.get_active_tokens()
        notifications_res = dashboard_segments(api_key, tokens)

        if not notifications_res:
            print("Tidak ditemukan notifikasi apapun.")
            return

        notifications = notifications_res.get("data", {}).get("notification", {}).get("data", [])
        if not notifications:
            print("Belum ada notifikasi untuk akun Anda.")
            return

        print("=" * WIDTH)
        print("NOTIFIKASI TERBARU:")
        print("=" * WIDTH)

        unread_count = 0
        for idx, notification in enumerate(notifications):
            is_read = notification.get("is_read", False)
            full_message = notification.get("full_message", "")
            raw_time = notification.get("timestamp", "")

            # Parse ISO 8601 jadi datetime object
            try:
                dt = datetime.fromisoformat(raw_time.replace("Z", "+00:00"))
                formatted_time = f"{dt.day} {bulan_id[dt.month]} {dt.year} {dt.hour:02d}.{dt.minute:02d}"
            except ValueError:
                formatted_time = raw_time  # fallback jika parsing gagal

            status = "SUDAH DIBACA" if is_read else "BARU"
            if not is_read:
                unread_count += 1

            print(f"{idx + 1}. [{status}] {formatted_time}")
            print(f"- {full_message}")
            print("-" * WIDTH)

        print(f"Total notifikasi: {len(notifications)} | Notifikasi baru: {unread_count}")
        print("=" * WIDTH)
        print("1. Tandai semua notifikasi baru sebagai dibaca")
        print("00. Kembali ke menu utama")
        print("=" * WIDTH)

        choice = input("Silakan pilih menu: ")
        if choice == "1":
            for notification in notifications:
                if notification.get("is_read", False):
                    continue
                notification_id = notification.get("notification_id")
                detail = get_notification_detail(api_key, tokens, notification_id)
                if detail:
                    print(f"Notifikasi ID {notification_id} berhasil ditandai sebagai dibaca.")
            input("Tekan Enter untuk kembali ke menu notifikasi...")
        elif choice == "00":
            in_notification_menu = False
        else:
            print("Pilihan tidak valid, silakan coba lagi.")