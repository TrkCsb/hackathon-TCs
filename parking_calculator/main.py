from pathlib import Path
from datetime import datetime
import math

def calculate_fee(mins: int) -> int:
    if mins <= 30:
        return 0
    days, rem = divmod(mins, 1440)
    fee = days * 10000
    if rem > 30:
        h = math.ceil((rem - 30) / 60)
        fee += min(h, 3) * 300 + max(h - 3, 0) * 500
    return fee

def format_duration(mins: int) -> str:
    parts = []
    if mins // 60: parts.append(f"{mins // 60} óra")
    if mins % 60:  parts.append(f"{mins % 60} perc")
    return " ".join(parts) or "0 perc"

def process_line(line: str) -> str:
    try:
        p = line.split()
        start = datetime.strptime(" ".join(p[1:3]), "%Y-%m-%d %H:%M:%S")
        end   = datetime.strptime(" ".join(p[3:5]), "%Y-%m-%d %H:%M:%S")
        if end < start:
            return "HIBA"
        mins = int((end - start).total_seconds() // 60)
        return f"{format_duration(mins)} parkolás → {calculate_fee(mins)} Ft"
    except:
        return "HIBA"

def main():
    lines = Path("input.txt").read_text(encoding="utf-8").splitlines()
    results = [process_line(l.strip()) for l in lines
               if l.strip() and "RENDSZAM" not in l and "=" not in l]
    print("\n".join(results))

if __name__ == "__main__":
    main()
    