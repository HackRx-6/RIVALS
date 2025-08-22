def smallest_almost_equal_index(s, pattern):
    n, m = len(s), len(pattern)
    for i in range(n - m + 1):
        diff = 0
        for j in range(m):
            if s[i + j] != pattern[j]:
                diff += 1
                if diff > 1:
                    break
        if diff <= 1:
            print(i)
            return
    print(-1)

s = input()
pattern = input()
smallest_almost_equal_index(s, pattern)