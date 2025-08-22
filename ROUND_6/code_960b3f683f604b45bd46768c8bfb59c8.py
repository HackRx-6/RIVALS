from math import factorial
from collections import Counter

def palindromic_permutation_kth(s, k):
    count = Counter(s)
    odd = [ch for ch in count if count[ch] % 2]
    if len(odd) > 1:
        return ""
    half = []
    mid = ''
    for ch in sorted(count):
        if count[ch] % 2:
            mid = ch
        half.extend([ch] * (count[ch] // 2))
    n = len(half)
    def count_perm(cnt):
        res = factorial(sum(cnt.values()))
        for v in cnt.values():
            res //= factorial(v)
        return res
    used = Counter()
    ans = []
    for i in range(n):
        for ch in sorted(set(half)):
            if used[ch] < half.count(ch):
                used[ch] += 1
                left = Counter()
                for c in half:
                    left[c] = half.count(c) - used[c]
                perms = count_perm(left)
                if k > perms:
                    k -= perms
                    used[ch] -= 1
                else:
                    ans.append(ch)
                    break
    if len(ans) < n:
        return ""
    res = ''.join(ans)
    res_full = res + mid + res[::-1]
    return res_full

s = input().strip()
k = int(input())
print(palindromic_permutation_kth(s, k))