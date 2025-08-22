from math import factorial
from collections import Counter

def kth_palindromic_permutation(s, k):
    def count_palindromic_permutations(half_counter):
        total = sum(half_counter.values())
        denom = 1
        for v in half_counter.values():
            denom *= factorial(v)
        return factorial(total) // denom

    counter = Counter(s)
    odd_chars = [ch for ch, cnt in counter.items() if cnt % 2 == 1]
    if len(odd_chars) > 1:
        return ''
    half_counter = {ch: cnt // 2 for ch, cnt in counter.items()}
    half_chars = []
    for ch in sorted(half_counter):
        half_chars.extend([ch] * half_counter[ch])
    n = len(half_chars)
    used = Counter()
    result = []
    k -= 1
    while len(result) < n:
        for ch in sorted(half_counter):
            if used[ch] < half_counter[ch]:
                used[ch] += 1
                perms = count_palindromic_permutations(Counter({c: half_counter[c] - used[c] for c in half_counter}))
                if k < perms:
                    result.append(ch)
                    break
                else:
                    k -= perms
                    used[ch] -= 1
    half = ''.join(result)
    mid = odd_chars[0] if odd_chars else ''
    return half + mid + half[::-1]

s = input()
k = int(input())
print(kth_palindromic_permutation(s, k))