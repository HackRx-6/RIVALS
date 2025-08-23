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
    odd = [c for c in counter if counter[c] % 2]
    if len(odd) > 1:
        return ""
    half = []
    mid = ""
    for c in sorted(counter):
        if counter[c] % 2:
            mid = c
        half.extend([c] * (counter[c] // 2))
    half_counter = Counter(half)
    n = len(half)
    used = Counter()
    res = []
    def dfs(path, half_counter, k):
        if len(path) == n:
            return path, k
        for c in sorted(half_counter):
            if half_counter[c] > 0:
                half_counter[c] -= 1
                cnt = count_palindromes(half_counter)
                if k > cnt:
                    k -= cnt
                    half_counter[c] += 1
                    continue
                path.append(c)
                return dfs(path, half_counter, k)
        return None, k
    path, left = dfs([], half_counter.copy(), k)
    if path is None or left > 1:
        return ""
    first_half = ''.join(path)
    second_half = first_half[::-1]
    return first_half + mid + second_half

s = input()
k = int(input())
print(kth_palindromic_permutation(s, k))