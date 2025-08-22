from math import factorial
from collections import Counter

def next_perm(seq):
    # Find the rightmost character which is smaller than its next character
    i = len(seq) - 2
    while i >= 0 and seq[i] >= seq[i+1]:
        i -= 1
    if i == -1:
        return False
    # Find the rightmost character which is greater than seq[i]
    j = len(seq) - 1
    while seq[j] <= seq[i]:
        j -= 1
    # Swap
    seq[i], seq[j] = seq[j], seq[i]
    # Reverse the suffix
    seq[i+1:] = reversed(seq[i+1:])
    return True

def unique_palindromic_permutations(s):
    count = Counter(s)
    odd = [c for c in count if count[c] % 2 == 1]
    if len(odd) > 1:
        return []
    half = []
    for c in sorted(count):
        half.extend([c] * (count[c] // 2))
    # Generate unique permutations of half
    perms = []
    used = [False] * len(half)
    def backtrack(path):
        if len(path) == len(half):
            perms.append(''.join(path))
            return
        prev = None
        for i in range(len(half)):
            if used[i]:
                continue
            if prev == half[i]:
                continue
            used[i] = True
            path.append(half[i])
            backtrack(path)
            path.pop()
            used[i] = False
            prev = half[i]
    backtrack([])
    palins = []
    mid = odd[0] if odd else ''
    for p in perms:
        palins.append(p + mid + p[::-1])
    return palins

s = input().strip()
k = int(input())
palins = unique_palindromic_permutations(s)
palins = sorted(set(palins))
if k <= len(palins):
    print(palins[k-1])
else:
    print("")