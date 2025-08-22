def almost_equal_substring(s, pattern):
    n, m = len(s), len(pattern)
    min_index = -1
    for i in range(n - m + 1):
        diff = 0
        for j in range(m):
            if s[i + j] != pattern[j]:
                diff += 1
                if diff > 1:
                    break
        if diff <= 1:
            return i
    return -1

s = input()
pattern = input()
print(almost_equal_substring(s, pattern))