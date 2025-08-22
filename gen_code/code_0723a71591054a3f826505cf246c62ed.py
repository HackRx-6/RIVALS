from collections import Counter
import math

def input_data():
    s = input().strip()
    k = int(input())
    return s, k

def factorial(n):
    return math.factorial(n)

def count_palindromic_permutations(half_counter):
    total = sum(half_counter.values())
    denom = 1
    for v in half_counter.values():
        denom *= factorial(v)
    return factorial(total) // denom

def kth_palindromic_permutation(s, k):
    counter = Counter(s)
    odd_chars = [ch for ch, cnt in counter.items() if cnt % 2 == 1]
    if len(odd_chars) > 1:
        return ""
    half_counter = {ch: cnt // 2 for ch, cnt in counter.items()}
    half_chars = []
    for ch in sorted(half_counter):
        half_chars.extend([ch] * half_counter[ch])
    n = len(half_chars)
    used = Counter()
    res = []
    def helper(half, k, used):
        if len(half) == n:
            return ''.join(half)
        for ch in sorted(half_counter):
            if used[ch] < half_counter[ch]:
                used[ch] += 1
                perms = count_palindromic_permutations(Counter({c: half_counter[c] - used[c] for c in half_counter}))
                if k > perms:
                    k -= perms
                    used[ch] -= 1
                    continue
                half.append(ch)
                return helper(half, k, used)
        return None
    half = []
    ans = helper(half, k, used)
    if not ans:
        return ""
    mid = odd_chars[0] if odd_chars else ""
    return ans + mid + ans[::-1]

s, k = input_data()
print(kth_palindromic_permutation(s, k))