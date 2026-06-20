import os

def handle_system_lock(command):
    print("Executing SYSTEM_LOCK...")
    os.system("rundll32.exe user32.dll,LockWorkStation")
    return "Locking your system"

def handle_system_shutdown(command):
    print("Executing SYSTEM_SHUTDOWN...")
    os.system("shutdown /s /t 5")
    return "Shutting down system in 5 seconds"

def handle_system_restart(command):
    print("Executing SYSTEM_RESTART...")
    os.system("shutdown /r /t 5")
    return "Restarting system in 5 seconds"
