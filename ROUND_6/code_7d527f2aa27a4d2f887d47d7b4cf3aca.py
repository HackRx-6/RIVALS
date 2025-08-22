from math import factorial
from collections import Counter

def kth_palindromic_permutation(s, k):
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
        total = sum(cnt.values())
        res = factorial(total)
        for v in cnt.values():
            res //= factorial(v)
        return res
    used = Counter()
    ans = []
    chars = sorted(set(half))
    for i in range(n):
        for ch in chars:
            if used[ch] < half.count(ch):
                used[ch] += 1
                left = Counter()
                for c in chars:
                    left[c] = half.count(c) - used[c]
                perms = count_perm(left)
                if perms < k:
                    k -= perms
                    used[ch] -= 1
                else:
                    ans.append(ch)
                    break
    first_half = ''.join(ans)
    second_half = first_half[::-1]
    return first_half + mid + second_half

s = input().strip()
k = int(input())
print(kth_palindromic_permutation(s, k))