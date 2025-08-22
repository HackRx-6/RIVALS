import math
from collections import Counter

def kth_palindromic_permutation(s, k):
    def count_perms(half_counts):
        total = sum(half_counts.values())
        denom = 1
        for v in half_counts.values():
            denom *= math.factorial(v)
        return math.factorial(total) // denom

    freq = Counter(s)
    odd = [c for c in freq if freq[c] % 2]
    if len(odd) > 1:
        return ''
    half = {}
    for c in freq:
        half[c] = freq[c] // 2
    half_chars = []
    for c in sorted(half):
        half_chars += [c] * half[c]
    n = len(half_chars)
    used = Counter()
    res = []
    def dfs(pos, k, used, path):
        if pos == n:
            return path
        for c in sorted(half):
            if used[c] < half[c]:
                used[c] += 1
                perms = count_perms(Counter({x: half[x] - used[x] for x in half}))
                if k > perms:
                    k -= perms
                    used[c] -= 1
                    continue
                return dfs(pos+1, k, used, path + [c])
        return None
    ans = dfs(0, k, Counter(), [])
    if not ans:
        return ''
    half_str = ''.join(ans)
    mid = odd[0] if odd else ''
    return half_str + mid + half_str[::-1]

print(kth_palindromic_permutation('abccbaabccbaabccbaab', 4))