def kth_palindromic_permutation(s, k):
    from collections import Counter
    from math import factorial

    def unique_perms(chars):
        # Generate unique permutations using backtracking
        def backtrack(path, counter, length):
            if len(path) == length:
                yield ''.join(path)
                return
            for ch in sorted(counter):
                if counter[ch] > 0:
                    counter[ch] -= 1
                    path.append(ch)
                    yield from backtrack(path, counter, length)
                    path.pop()
                    counter[ch] += 1
        return backtrack([], Counter(chars), len(chars))

    count = Counter(s)
    odd = [ch for ch in count if count[ch] % 2 == 1]
    if len(odd) > 1:
        return ''
    half = []
    for ch in sorted(count):
        half.extend([ch] * (count[ch] // 2))
    mid = odd[0] if odd else ''
    seen = set()
    idx = 0
    for perm in unique_perms(half):
        if perm in seen:
            continue
        seen.add(perm)
        pal = perm + mid + perm[::-1]
        idx += 1
        if idx == k:
            return pal
    return ''

# Example usage:
s = input()
k = int(input())
print(kth_palindromic_permutation(s, k))