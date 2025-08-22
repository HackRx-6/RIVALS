def kth_palindromic_permutation(s, k):
    from collections import Counter
    import math

    def can_form_palindrome(counter):
        odd = sum(v % 2 for v in counter.values())
        return odd <= 1

    def unique_permutations(seq):
        # Generates unique permutations of seq (which may have duplicates)
        def backtrack(path, counter, length):
            if len(path) == length:
                yield tuple(path)
                return
            for ch in sorted(counter):
                if counter[ch] > 0:
                    counter[ch] -= 1
                    path.append(ch)
                    yield from backtrack(path, counter, length)
                    path.pop()
                    counter[ch] += 1
        return backtrack([], Counter(seq), len(seq))

    counter = Counter(s)
    if not can_form_palindrome(counter):
        return ""

    half = []
    mid = ""
    for ch, cnt in counter.items():
        if cnt % 2 == 1:
            mid = ch
        half.extend([ch] * (cnt // 2))
    seen = set()
    perms = []
    for p in unique_permutations(half):
        if p not in seen:
            seen.add(p)
            perms.append(p)
    perms.sort()
    if k > len(perms):
        return ""
    half_str = ''.join(perms[k-1])
    return half_str + mid + half_str[::-1]

# Example usage:
# s = input()
# k = int(input())
# print(kth_palindromic_permutation(s, k))