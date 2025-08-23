from math import factorial
from collections import Counter

def kth_palindromic_permutation(s, k):
    def count_palindromes(counts):
        half_counts = [v // 2 for v in counts.values()]
        total = sum(half_counts)
        denom = 1
        for c in half_counts:
            denom *= factorial(c)
        return factorial(total) // denom

    counts = Counter(s)
    odd_chars = [c for c, v in counts.items() if v % 2 == 1]
    if len(odd_chars) > 1:
        return ""
    half = []
    for c in sorted(counts):
        half.extend([c] * (counts[c] // 2))
    n = len(half)
    used = Counter()
    res = []
    k -= 1
    while len(res) < n:
        for c in sorted(counts):
            if used[c] < counts[c] // 2:
                used[c] += 1
                temp_counts = Counter()
                for ch in counts:
                    temp_counts[ch] = counts[ch] // 2 - used[ch]
                if min(temp_counts.values(), default=0) < 0:
                    used[c] -= 1
                    continue
                num = count_palindromes(Counter({ch: used[ch] for ch in counts}))
                if k < num:
                    res.append(c)
                    break
                else:
                    k -= num
                    used[c] -= 1
    first_half = ''.join(res)
    mid = ''
    for c in counts:
        if counts[c] % 2 == 1:
            mid = c
            break
    return first_half + mid + first_half[::-1]

s = 'abccbaabccbaabccbaab'
k = 4
print(kth_palindromic_permutation(s, k))