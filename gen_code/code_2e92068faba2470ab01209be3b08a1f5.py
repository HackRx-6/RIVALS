s1 = input("Enter s1: ")
s2 = input("Enter s2: ")

from collections import Counter

len_s1 = len(s1)
s1_count = Counter(s1)
found = False

for i in range(len(s2) - len_s1 + 1):
    window = s2[i:i+len_s1]
    if Counter(window) == s1_count:
        found = True
        break

print(found)