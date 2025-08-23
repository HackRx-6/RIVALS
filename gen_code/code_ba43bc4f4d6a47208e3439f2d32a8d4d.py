from itertools import permutations

def kth_palindromic_permutation(s, k):
    from collections import Counter

    count = Counter(s)
    mid = ''
    half = []
    for ch, cnt in count.items():
        if cnt % 2 == 1:
            if mid:
                return ''
            mid = ch
        half.extend([ch] * (cnt // 2))
    half = ''.join(half)
    perms = sorted(set(permutations(half)))
    if len(perms) < k:
        return ''
    half_perm = ''.join(perms[k-1])
    return half_perm + mid + half_perm[::-1]

s = input()
k = int(input())
print(kth_palindromic_permutation(s, k))