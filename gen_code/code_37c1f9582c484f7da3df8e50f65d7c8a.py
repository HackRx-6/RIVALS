s = 'ababbababa'
pattern = 'bacaba'

def find_almost_equal(s, pattern):
    n, m = len(s), len(pattern)
    for i in range(n - m + 1):
        sub = s[i:i+m]
        diff = sum(1 for a, b in zip(sub, pattern) if a != b)
        if diff <= 1:
            return i
    return -1

print(find_almost_equal(s, pattern))