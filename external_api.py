import requests

def fetch_current_time():
    """
    Calls WorldTimeAPI to get real date/time.
    Returns ISO string or None on error.
    """
    try:
        url = "https://worldtimeapi.org/api/timezone/America/Toronto"
        r = requests.get(url, timeout=5)
        r.raise_for_status()
        data = r.json()
        return data.get("datetime", None)
    except Exception:
        return None
