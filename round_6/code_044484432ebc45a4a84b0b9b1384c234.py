def smallest_almost_equal_index(s, pattern):
    n, m = len(s), len(pattern)
    for i in range(n - m + 1):
        window = s[i:i+m]
        diff = sum(1 for a, b in zip(window, pattern) if a != b)
        if diff <= 1:
            return i
    return -1

# Example usage
s = input("Enter string s: ")
pattern = input("Enter pattern: ")
result = smallest_almost_equal_index(s, pattern)
print(result)