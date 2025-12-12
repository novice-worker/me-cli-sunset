from app.menus.util import clear_screen
from app.client.engsel import get_notification_detail, dashboard_segments
from app.service.auth import AuthInstance

WIDTH = 55

def show_notification_menu():
    in_notification_menu = True
    while in_notification_menu:
        clear_screen()
        print("Fetching notifications...")
        
        api_key = AuthInstance.api_key
        tokens = AuthInstance.get_active_tokens()
        
        notifications_res = dashboard_segments(api_key, tokens)
        if not notifications_res:
            print("No notifications found.")
            return
        
        notifications = notifications_res.get("data", {}).get("notification", {}).get("data", [])
        if not notifications:
            print("No notifications available.")
            return
        
from datetime import datetime

# Mapping bulan ke bahasa Indonesia
bulan_id = {
    1: "Januari", 2: "Februari", 3: "Maret", 4: "April",
    5: "Mei", 6: "Juni", 7: "Juli", 8: "Agustus",
    9: "September", 10: "Oktober", 11: "November", 12: "Desember"
}

print("=" * WIDTH)
print("Notifications:")
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

    status = "READ" if is_read else "UNREAD"
    if not is_read:
        unread_count += 1

    print(f"{idx + 1}. [{status}] {formatted_time}")
    print(f"- {full_message}")
    print("-" * WIDTH)

print(f"Total notifications: {len(notifications)} | Unread: {unread_count}")
print("=" * WIDTH))
        print(f"Total notifications: {len(notifications)} | Unread: {unread_count}")
        print("=" * WIDTH)
        print("1. Read All Unread Notifications")
        print("00. Back to Main Menu")
        print("=" * WIDTH)
        choice = input("Enter your choice: ")
        if choice == "1":
            for notification in notifications:
                if notification.get("is_read", False):
                    continue
                notification_id = notification.get("notification_id")
                detail = get_notification_detail(api_key, tokens, notification_id)
                if detail:
                    print(f"Mark as READ notification ID: {notification_id}")
            input("Press Enter to return to the notification menu...")
        elif choice == "00":
            in_notification_menu = False
        else:
            print("Invalid choice. Please try again.")
