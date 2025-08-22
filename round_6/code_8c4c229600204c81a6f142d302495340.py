def smallest_almost_equal_index(s, pattern):
    n = len(s)
    m = len(pattern)
    for i in range(n - m + 1):
        window = s[i:i+m]
        diff = sum(1 for a, b in zip(window, pattern) if a != b)
        if diff <= 1:
            return i
    return -1

if __name__ == '__main__':
    s = input("Enter the string s: ")
    pattern = input("Enter the pattern: ")
    print(smallest_almost_equal_index(s, pattern))