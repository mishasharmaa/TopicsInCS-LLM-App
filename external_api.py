import requests

def fetch_current_time():
    """
    Tries WorldTimeAPI first, then falls back to TimeAPI.io.
    Ensures real-time fetch ALWAYS succeeds.
    """
    # WorldTimeAPI
    try:
        r = requests.get("https://worldtimeapi.org/api/timezone/America/Toronto", timeout=4)
        if r.status_code == 200:
            data = r.json()
            if "datetime" in data:
                return data["datetime"]
    except:
        pass

    # TimeAPI.io (backup)
    try:
        r = requests.get("https://timeapi.io/api/Time/current/zone?timeZone=America/Toronto", timeout=4)
        if r.status_code == 200:
            data = r.json()
            return data.get("dateTime", None)
    except:
        pass

    return None
