from plyer import notification

def show_toast(message):
    notification.notify(
        title="RecoverEase",
        message=message,
        timeout=5
    )
