s = input()
pattern = input()
min_index = -1
n, m = len(s), len(pattern)
for i in range(n - m + 1):
    mismatch = 0
    for j in range(m):
        if s[i + j] != pattern[j]:
            mismatch += 1
            if mismatch > 1:
                break
    if mismatch <= 1:
        min_index = i
        break
print(min_index)