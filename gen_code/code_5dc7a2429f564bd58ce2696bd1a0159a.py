s = input("Enter string s: ")
pattern = input("Enter pattern: ")
n, m = len(s), len(pattern)
res = -1
for i in range(n - m + 1):
    diff = 0
    for j in range(m):
        if s[i + j] != pattern[j]:
            diff += 1
            if diff > 1:
                break
    if diff <= 1:
        res = i
        break
print(res)