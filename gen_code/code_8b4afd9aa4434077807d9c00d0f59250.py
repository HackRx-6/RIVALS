from math import factorial
from collections import Counter

def kth_palindromic_permutation(s, k):
    def count_palindromes(half_counter):
        total = sum(half_counter.values())
        res = factorial(total)
        for v in half_counter.values():
            res //= factorial(v)
        return res

    counter = Counter(s)
    odd = [ch for ch, cnt in counter.items() if cnt % 2]
    if len(odd) > 1:
        return ""
    mid = odd[0] if odd else ""
    half_counter = {ch: cnt // 2 for ch, cnt in counter.items()}
    half_chars = []
    for ch in sorted(half_counter):
        half_chars.extend([ch] * half_counter[ch])
    n = len(half_chars)
    used = Counter()
    res = []
    def backtrack(path, k):
        if len(path) == n:
            return ''.join(path)
        for ch in sorted(half_counter):
            if used[ch] < half_counter[ch]:
                used[ch] += 1
                # Count how many palindromes if we pick ch next
                remain = Counter()
                for c in half_counter:
                    remain[c] = half_counter[c] - used[c]
                cnt = count_palindromes(remain)
                if k > cnt:
                    k -= cnt
                    used[ch] -= 1
                    continue
                else:
                    path.append(ch)
                    return backtrack(path, k)
        return None
    ans = backtrack([], k)
    if not ans:
        return ""
    half = ans
    return half + mid + half[::-1]

s = input().strip()
k = int(input())
print(kth_palindromic_permutation(s, k))