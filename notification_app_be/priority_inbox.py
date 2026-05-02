import requests
from datetime import datetime

# Your auth token
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJNYXBDbGFpbXMiOnsiYXVkIjoiaHR0cDovLzIwLjI0NC41Ni4xNDQvZXZhbHVhdGlvbi1zZXJ2aWNlIiwiZW1haWwiOiI4MTQ3MjMxMDQxNDNAdHJwLnNybXRyaWNoeS5lZHUuaW4iLCJleHAiOjE3Nzc3MDM3OTQsImlhdCI6MTc3NzcwMjg5NCwiaXNzIjoiQWZmb3JkIE1lZGljYWwgVGVjaG5vbG9naWVzIFByaXZhdGUgTGltaXRlZCIsImp0aSI6ImEyNzBlNmMyLTc2MTUtNDQyOS1iNzY3LWQ4MTI3Yjg1ZWY1YSIsImxvY2FsZSI6ImVuLUlOIiwibmFtZSI6InNoYWZlZWsgYWhtZWQiLCJzdWIiOiJiZWE0MjYyYS0xYjQ3LTRmYzYtOWVjNi04NDc1M2NjYTI2NGIifSwiZW1haWwiOiI4MTQ3MjMxMDQxNDNAdHJwLnNybXRyaWNoeS5lZHUuaW4iLCJuYW1lIjoic2hhZmVlayBhaG1lZCIsInJvbGxObyI6IjgxNDcyMzEwNDE0MyIsImFjY2Vzc0NvZGUiOiJRa2JweEgiLCJjbGllbnRJRCI6ImJlYTQyNjJhLTFiNDctNGZjNi05ZWM2LTg0NzUzY2NhMjY0YiIsImNsaWVudFNlY3JldCI6InB1V3JHSmpoUVdhV2NoaHMifQ.QZJW4KD7-R534c5d3x6TZikrbcHGcDGiLMfrmPfygb4"

# API URL
API_URL = "http://20.207.122.201/evaluation-service/notifications"

# Type weights — Placement highest priority
WEIGHTS = {
    "Placement": 3,
    "Result": 2,
    "Event": 1
}

# Logging middleware
def Log(stack, level, package, message):
    try:
        response = requests.post(
            "http://20.207.122.201/evaluation-service/logs",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {TOKEN}"
            },
            json={
                "stack": stack,
                "level": level,
                "package": package,
                "message": message
            }
        )
        return response.json()
    except Exception as e:
        print(f"Logging error: {e}")

# Fetch notifications from API
def fetch_notifications():
    try:
        Log("backend", "info", "service", "Fetching notifications from API")
        response = requests.get(
            API_URL,
            headers={
                "Authorization": f"Bearer {TOKEN}"
            }
        )
        data = response.json()
        Log("backend", "info", "service", f"Fetched {len(data['notifications'])} notifications")
        return data["notifications"]
    except Exception as e:
        Log("backend", "error", "service", f"Failed to fetch notifications: {str(e)}")
        return []

# Calculate priority score
def calculate_score(notification):
    try:
        type_weight = WEIGHTS.get(notification["Type"], 0)
        timestamp = datetime.strptime(notification["Timestamp"], "%Y-%m-%d %H:%M:%S")
        recency_score = timestamp.timestamp()
        # Multiply weight by large number so type always dominates recency
        score = (type_weight * 1e12) + recency_score
        return score
    except Exception as e:
        Log("backend", "error", "service", f"Score calculation failed: {str(e)}")
        return 0

# Get top N priority notifications
def get_priority_notifications(n=10):
    try:
        Log("backend", "info", "service", f"Getting top {n} priority notifications")
        notifications = fetch_notifications()

        if not notifications:
            Log("backend", "warn", "service", "No notifications found")
            return []

        # Score and sort notifications
        scored = []
        for notification in notifications:
            score = calculate_score(notification)
            scored.append((score, notification))

        # Sort by score descending
        scored.sort(key=lambda x: x[0], reverse=True)

        # Get top N
        top_n = [notification for score, notification in scored[:n]]

        Log("backend", "info", "service", f"Returning top {len(top_n)} priority notifications")
        return top_n

    except Exception as e:
        Log("backend", "error", "service", f"Priority inbox failed: {str(e)}")
        return []

# Main
if __name__ == "__main__":
    print("=== Priority Inbox — Top 10 Notifications ===\n")
    top_notifications = get_priority_notifications(n=10)

    for i, notification in enumerate(top_notifications, 1):
        print(f"{i}. [{notification['Type']}] {notification['Message']} — {notification['Timestamp']}")
