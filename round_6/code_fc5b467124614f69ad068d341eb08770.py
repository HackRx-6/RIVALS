def smallest_almost_equal_index(s, pattern):
    n = len(s)
    m = len(pattern)
    min_index = -1
    for i in range(n-m+1):
        substring = s[i:i+m]
        diff = 0
        for a, b in zip(substring, pattern):
            if a != b:
                diff += 1
        if diff <= 1:
            min_index = i
            break
    return min_index

if __name__ == "__main__":
    s = input("Enter the string s: ")
    pattern = input("Enter the pattern: ")
    print(smallest_almost_equal_index(s, pattern))