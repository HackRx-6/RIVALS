from collections import Counter
import math

def next_palindromic_permutation(s, k):
    n = len(s)
    count = Counter(s)
    odd = [ch for ch in count if count[ch] % 2 == 1]
    if len(odd) > 1:
        return ""
    half = []
    for ch in sorted(count):
        half.extend([ch] * (count[ch] // 2))
    half = ''.join(half)
    def unique_perms(s):
        c = Counter(s)
        res = math.factorial(len(s))
        for v in c.values():
            res //= math.factorial(v)
        return res
    def kth_perm(s, k):
        c = Counter(s)
        res = []
        chars = sorted(c)
        while len(res) < len(s):
            for ch in chars:
                if c[ch] == 0:
                    continue
                c[ch] -= 1
                perms = unique_perms(''.join([ch2 * c[ch2] for ch2 in chars]))
                if k > perms:
                    k -= perms
                    c[ch] += 1
                else:
                    res.append(ch)
                    break
        return ''.join(res)
    total = unique_perms(half)
    if k > total:
        return ""
    first_half = kth_perm(half, k)
    mid = odd[0] if odd else ''
    return first_half + mid + first_half[::-1]

s = input().strip()
k = int(input())
print(next_palindromic_permutation(s, k))