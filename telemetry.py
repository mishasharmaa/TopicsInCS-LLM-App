import time

def log_request(pathway: str, latency: float, tokens: int = 0):
    with open("telemetry.log", "a") as f:
        f.write(f"{time.time()}, pathway={pathway}, latency={latency}, tokens={tokens}\n")
