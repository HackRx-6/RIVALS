def kth_palindromic_permutation(s, k):
    from collections import Counter
    import math

    def can_form_palindrome(counter):
        odd = sum(v % 2 for v in counter.values())
        return odd <= 1

    def half_permutations(counter):
        half = []
        for c, v in counter.items():
            half.extend([c] * (v // 2))
        return half

    def count_perms(half_counter):
        total = sum(half_counter.values())
        res = math.factorial(total)
        for v in half_counter.values():
            res //= math.factorial(v)
        return res

    def kth_perm(half_counter, k, chars):
        if not chars:
            return ''
        for c in sorted(chars):
            if half_counter[c] == 0:
                continue
            half_counter[c] -= 1
            perms = count_perms(half_counter)
            if k <= perms:
                return c + kth_perm(half_counter, k, chars)
            k -= perms
            half_counter[c] += 1
        return None

    counter = Counter(s)
    if not can_form_palindrome(counter):
        return ''
    mid = ''
    for c, v in counter.items():
        if v % 2 == 1:
            mid = c
            break
    half = half_permutations(counter)
    half_counter = Counter(half)
    total_perms = count_perms(half_counter)
    if k > total_perms:
        return ''
    half_str = kth_perm(half_counter, k, list(set(half)))
    if half_str is None:
        return ''
    return half_str + mid + half_str[::-1]

# Example usage:
s = input()
k = int(input())
print(kth_palindromic_permutation(s, k))