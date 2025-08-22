s = 'ababbababa'
pattern = 'bacaba'
result = -1
for i in range(len(s) - len(pattern) + 1):
    mismatch = 0
    for j in range(len(pattern)):
        if s[i+j] != pattern[j]:
            mismatch += 1
        if mismatch > 1:
            break
    if mismatch <= 1:
        result = i
        break
print(result)