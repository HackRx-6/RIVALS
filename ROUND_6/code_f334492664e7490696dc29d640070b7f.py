def smallest_almost_equal_index(s, pattern):
    min_index = -1
    n, m = len(s), len(pattern)
    for i in range(n - m + 1):
        substring = s[i:i+m]
        diff = sum(1 for a, b in zip(substring, pattern) if a != b)
        if diff <= 1:
            min_index = i
            break
    return min_index

if __name__ == "__main__":
    s = input("Enter the string s: ")
    pattern = input("Enter the pattern: ")
    print(smallest_almost_equal_index(s, pattern))