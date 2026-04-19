from pathlib import Path

def minDropNumbr(n, h):
    dp = [0] * (n + 1)
    moves = 0

    while dp[n] < h:
        moves += 1
        for k in range(n, 0, -1):
            dp[k] = dp[k] + dp[k - 1] + 1
    return moves

def main():
    data = Path("input.txt").read_text(encoding="utf-8").splitlines()

    for line in data:
        line = line.strip()
        if not line:
            continue
        parts = line.replace(",", " ").split()
        if len(parts) != 2:
            continue
        n, h = map(int, parts)
        print(minDropNumbr(n, h))

if __name__ == "__main__":
    main()
