from math import factorial
from collections import Counter

def kth_palindromic_permutation(s, k):
    def count_palindromes(half_count):
        total = sum(half_count.values())
        res = factorial(total)
        for v in half_count.values():
            res //= factorial(v)
        return res

    freq = Counter(s)
    odd = [c for c in freq if freq[c] % 2]
    if len(odd) > 1:
        return ''
    half = []
    half_count = {}
    for c in sorted(freq):
        half_count[c] = freq[c] // 2
        half.extend([c] * (freq[c] // 2))
    n = len(half)
    used = Counter()
    res = []
    k -= 1
    while len(res) < n:
        for c in sorted(half_count):
            if used[c] < half_count[c]:
                used[c] += 1
                cnt = count_palindromes(Counter({x: half_count[x] - used[x] for x in half_count}))
                if k < cnt:
                    res.append(c)
                    break
                else:
                    k -= cnt
                used[c] -= 1
    first_half = ''.join(res)
    mid = ''
    if odd:
        mid = odd[0]
    return first_half + mid + first_half[::-1]

s = input()
k = int(input())
print(kth_palindromic_permutation(s, k))