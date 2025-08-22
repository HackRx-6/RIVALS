from collections import Counter
import math

def kth_palindromic_permutation(s, k):
    def can_form_palindrome(counter):
        odd = sum(v % 2 for v in counter.values())
        return odd <= 1

    def half_string_and_middle(counter):
        half = []
        middle = ''
        for ch, cnt in counter.items():
            if cnt % 2 == 1:
                middle = ch
            half.extend([ch] * (cnt // 2))
        return ''.join(half), middle

    def count_permutations(half_counter):
        total = sum(half_counter.values())
        res = math.factorial(total)
        for v in half_counter.values():
            res //= math.factorial(v)
        return res

    def next_perm(half):
        # Generate next lexicographical permutation in-place
        i = len(half) - 2
        while i >= 0 and half[i] >= half[i+1]:
            i -= 1
        if i == -1:
            return False
        j = len(half) - 1
        while half[j] <= half[i]:
            j -= 1
        half[i], half[j] = half[j], half[i]
        half[i+1:] = reversed(half[i+1:])
        return True

    counter = Counter(s)
    if not can_form_palindrome(counter):
        return ''

    half, middle = half_string_and_middle(counter)
    half = sorted(half)
    half_counter = Counter(half)
    total_perms = count_permutations(half_counter)
    if k > total_perms:
        return ''

    # Generate k-th unique permutation
    used = [False] * len(half)
    res = []
    def dfs(path, counter, k):
        if len(path) == len(half):
            return ''.join(path), k
        for ch in sorted(counter):
            if counter[ch] == 0:
                continue
            counter[ch] -= 1
            perms = count_permutations(counter)
            if k > perms:
                k -= perms
                counter[ch] += 1
                continue
            path.append(ch)
            result, k = dfs(path, counter, k)
            if result:
                return result, k
            path.pop()
            counter[ch] += 1
        return '', k

    half_perm, _ = dfs([], Counter(half), k)
    if not half_perm:
        return ''
    pal_perm = half_perm + middle + half_perm[::-1]
    return pal_perm

s = input().strip()
k = int(input())
print(kth_palindromic_permutation(s, k))