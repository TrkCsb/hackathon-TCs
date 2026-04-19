from pathlib import Path

def nextMagicNum(n: int) -> int:
    beginning = str(n + 1)
    length, half = len(beginning), (len(beginning) + 1) // 2

    def pal(p, n):
        return int(p + p[::-1]) if n % 2 == 0 else int(p + p[-2::-1])

    if (c := pal(beginning[:half], length)) >= n + 1:
        return c

    p = str(int(beginning[:half]) + 1)
    if len(p) > half:
        h2 = (length + 2) // 2
        return pal(str(10 ** (h2 - 1)), length + 1)
    return pal(p, length)


def main():
    for line in Path("input.txt").read_text(encoding="utf-8").splitlines():
        if start := line.strip():
            b, e = start.split("^") if "^" in start else (start, None)
            print(nextMagicNum(int(b) ** int(e) if e else int(b)))

if __name__ == "__main__":
    main()
