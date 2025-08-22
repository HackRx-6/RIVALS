from collections import Counter
import math

def kth_palindromic_permutation(s, k):
    count = Counter(s)
    odd = [ch for ch in count if count[ch] % 2 == 1]
    if len(odd) > 1:
        return ""
    half = []
    mid = ""
    for ch in sorted(count):
        if count[ch] % 2 == 1:
            mid = ch
        half.extend([ch] * (count[ch] // 2))
    def count_perms(half_count):
        total = sum(half_count.values())
        res = math.factorial(total)
        for v in half_count.values():
            res //= math.factorial(v)
        return res
    def next_perm(half_count, k, path):
        if sum(half_count.values()) == 0:
            return ''.join(path)
        for ch in sorted(half_count):
            if half_count[ch] == 0:
                continue
            half_count[ch] -= 1
            perms = count_perms(half_count)
            if k > perms:
                k -= perms
                half_count[ch] += 1
                continue
            path.append(ch)
            return next_perm(half_count, k, path)
        return None
    half_count = Counter(half)
    total_perms = count_perms(half_count)
    if k > total_perms:
        return ""
    half_str = next_perm(half_count, k, [])
    if half_str is None:
        return ""
    return half_str + mid + half_str[::-1]

s = 'malayalam'
k = 2
print(kth_palindromic_permutation(s, k))