import sys
import math
from collections import Counter

def next_perm(arr):
    i = len(arr) - 2
    while i >= 0 and arr[i] >= arr[i+1]:
        i -= 1
    if i == -1:
        return False
    j = len(arr) - 1
    while arr[j] <= arr[i]:
        j -= 1
    arr[i], arr[j] = arr[j], arr[i]
    arr[i+1:] = reversed(arr[i+1:])
    return True

def count_half_perms(half_counter):
    total = sum(half_counter.values())
    res = math.factorial(total)
    for v in half_counter.values():
        res //= math.factorial(v)
    return res

def kth_palindromic_permutation(s, k):
    counter = Counter(s)
    odd_chars = [c for c in counter if counter[c] % 2 == 1]
    if len(odd_chars) > 1:
        return ""
    half = []
    for c in sorted(counter):
        half.extend([c] * (counter[c] // 2))
    half_counter = Counter(half)
    total_perms = count_half_perms(half_counter)
    if k > total_perms:
        return ""
    n = len(half)
    used = Counter()
    res = []
    chars = sorted(half_counter)
    for i in range(n):
        for c in chars:
            if used[c] < half_counter[c]:
                used[c] += 1
                temp_counter = Counter()
                for cc in chars:
                    temp_counter[cc] = half_counter[cc] - used[cc]
                perms = count_half_perms(temp_counter)
                if perms < k:
                    k -= perms
                    used[c] -= 1
                else:
                    res.append(c)
                    break
    mid = odd_chars[0] if odd_chars else ""
    return "".join(res) + mid + "".join(reversed(res))

s = sys.stdin.readline().strip()
k = int(sys.stdin.readline().strip())
print(kth_palindromic_permutation(s, k))