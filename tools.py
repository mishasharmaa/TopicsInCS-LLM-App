import datetime

def get_version_and_date(previous_version=None):
    today = datetime.date.today()
    base = today.strftime("%Y.%m.%d")

    if previous_version and previous_version.startswith(base):
        # Same-day release → bump suffix
        try:
            suffix = int(previous_version.split(".")[-1]) + 1
        except:
            suffix = 1
    else:
        suffix = 1

    return f"{base}.{suffix}", today.isoformat()
