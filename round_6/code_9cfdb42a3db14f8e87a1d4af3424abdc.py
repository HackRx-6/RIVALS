def is_almost_equal(sub, pattern):
    diff = 0
    for a, b in zip(sub, pattern):
        if a != b:
            diff += 1
            if diff > 1:
                return False
    return diff == 1 or diff == 0

s = input("Enter string s: ")
pattern = input("Enter pattern: ")

n, m = len(s), len(pattern)
result = -1
for i in range(n - m + 1):
    if is_almost_equal(s[i:i+m], pattern):
        result = i
        break

print(result)