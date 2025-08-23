from math import factorial
from collections import Counter

def kth_palindromic_permutation(s, k):
    count = Counter(s)
    odd = [ch for ch in count if count[ch] % 2 == 1]
    if len(odd) > 1:
        return ''
    half = []
    for ch in sorted(count):
        half.extend([ch] * (count[ch] // 2))
    half_len = len(half)
    def count_perms(half_count):
        total = sum(half_count.values())
        res = factorial(total)
        for v in half_count.values():
            res //= factorial(v)
        return res
    used = Counter()
    res = []
    half_count = Counter(half)
    for i in range(half_len):
        for ch in sorted(half_count):
            if half_count[ch] == 0:
                continue
            half_count[ch] -= 1
            perms = count_perms(half_count)
            if perms < k:
                k -= perms
                half_count[ch] += 1
            else:
                res.append(ch)
                break
    first_half = ''.join(res)
    mid = odd[0] if odd else ''
    second_half = first_half[::-1]
    return first_half + mid + second_half

s = 'abccbaabccbaabccbaab'
k = 4
print(kth_palindromic_permutation(s, k))