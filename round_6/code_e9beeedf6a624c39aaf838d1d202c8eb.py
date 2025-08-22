import sys
import math
from collections import Counter

def input():
    return sys.stdin.readline().strip()

def palindromic_permutations_count(half_counter):
    total = sum(half_counter.values())
    denom = 1
    for v in half_counter.values():
        denom *= math.factorial(v)
    return math.factorial(total) // denom

def kth_palindromic_permutation(s, k):
    count = Counter(s)
    odd = [c for c in count if count[c] % 2 == 1]
    if len(odd) > 1:
        return ""
    half = []
    for c in sorted(count):
        half.extend([c] * (count[c] // 2))
    half_counter = Counter(half)
    n = len(half)
    res = []
    used = Counter()
    def build(half_counter, k, path):
        if len(path) == n:
            return path
        for c in sorted(half_counter):
            if half_counter[c] > 0:
                half_counter[c] -= 1
                cnt = palindromic_permutations_count(half_counter)
                if k <= cnt:
                    path.append(c)
                    return build(half_counter, k, path)
                else:
                    k -= cnt
                half_counter[c] += 1
        return None
    path = build(half_counter, k, [])
    if not path:
        return ""
    first_half = ''.join(path)
    second_half = first_half[::-1]
    mid = odd[0] if odd else ''
    return first_half + mid + second_half

s = input()
k = int(input())
print(kth_palindromic_permutation(s, k))