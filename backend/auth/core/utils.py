import re
from typing import Optional

def mask_email(email: str) -> str:
    """
    Маскирует email адрес.
    Пример: user@example.com -> u***r@example.com
    """
    if not email or "@" not in email:
        return email
    
    try:
        name, domain = email.split("@")
        if len(name) <= 2:
            return f"{name[0]}***@{domain}"
        return f"{name[0]}***{name[-1]}@{domain}"
    except Exception:
        return "***@***"

def mask_ip(ip: Optional[str]) -> str:
    """
    Маскирует IP адрес.
    Пример: 192.168.1.1 -> 192.168.***.***
    """
    if not ip:
        return "unknown"
    
    # IPv4
    if "." in ip:
        parts = ip.split(".")
        if len(parts) == 4:
            return f"{parts[0]}.{parts[1]}.***.***"
    
    # IPv6 или другие форматы
    if ":" in ip:
        return f"{ip[:4]}:***:***:***"
        
    return "***.***.***.***"
