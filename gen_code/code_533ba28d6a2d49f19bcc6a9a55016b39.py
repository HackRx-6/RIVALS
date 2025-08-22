s = input("Enter the string s: ")
pattern = input("Enter the pattern: ")

n = len(s)
m = len(pattern)
result = -1

for i in range(n - m + 1):
    substring = s[i:i+m]
    diff = sum(1 for a, b in zip(substring, pattern) if a != b)
    if diff <= 1:
        result = i
        break

print(result)