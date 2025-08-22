s = input()
pattern = input()

n, m = len(s), len(pattern)
res = -1

for i in range(n - m + 1):
    sub = s[i:i+m]
    diff = sum(1 for a, b in zip(sub, pattern) if a != b)
    if diff <= 1:
        res = i
        break

print(res)