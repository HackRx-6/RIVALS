import sys
import math
from collections import Counter

def kth_palindromic_permutation(s, k):
    count = Counter(s)
    odd = [ch for ch in count if count[ch] % 2 == 1]
    if len(odd) > 1:
        return ""
    half = []
    mid = ''
    for ch in sorted(count):
        if count[ch] % 2 == 1:
            mid = ch
        half.extend([ch] * (count[ch] // 2))
    n = len(half)
    def count_perms(half_count):
        total = sum(half_count.values())
        res = math.factorial(total)
        for v in half_count.values():
            res //= math.factorial(v)
        return res
    half_count = Counter(half)
    res = []
    used = set()
    def backtrack(path, half_count, k):
        if len(path) == n:
            return ''.join(path)
        for ch in sorted(half_count):
            if half_count[ch] > 0:
                half_count[ch] -= 1
                perms = count_perms(half_count)
                if perms < k:
                    k -= perms
                    half_count[ch] += 1
                    continue
                path.append(ch)
                return backtrack(path, half_count, k)
        return None
    left = backtrack([], half_count, k)
    if not left:
        return ""
    right = left[::-1]
    return left + mid + right

if __name__ == "__main__":
    s = input().strip()
    k = int(input())
    print(kth_palindromic_permutation(s, k))