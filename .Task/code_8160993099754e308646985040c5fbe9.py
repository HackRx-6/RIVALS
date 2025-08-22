from math import factorial

def kth_palindromic_permutation(s, k):
    from collections import Counter

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
        res = factorial(total)
        for v in half_count.values():
            res //= factorial(v)
        return res
    res = []
    used = Counter()
    def dfs(path, half_count, k):
        if len(path) == n:
            return path
        for ch in sorted(half_count):
            if half_count[ch] > 0:
                half_count[ch] -= 1
                perms = count_perms(half_count)
                if k > perms:
                    k -= perms
                    half_count[ch] += 1
                    continue
                return dfs(path + [ch], half_count, k)
        return None
    half_count = Counter(half)
    perm = dfs([], half_count, k)
    if not perm:
        return ""
    first_half = ''.join(perm)
    second_half = first_half[::-1]
    return first_half + mid + second_half

s = input()
k = int(input())
print(kth_palindromic_permutation(s, k))