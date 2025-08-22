def kth_palindromic_permutation(s, k):
    from collections import Counter
    from math import factorial

    def count_palindromic_permutations(half_counter):
        total = sum(half_counter.values())
        res = factorial(total)
        for v in half_counter.values():
            res //= factorial(v)
        return res

    freq = Counter(s)
    odd_chars = [c for c, v in freq.items() if v % 2 == 1]
    if len(odd_chars) > 1:
        return ''
    half = []
    half_counter = {}
    for c in sorted(freq):
        half_counter[c] = freq[c] // 2
        half.extend([c] * (freq[c] // 2))
    half_len = len(half)
    used = Counter()
    result = []
    k -= 1  # 0-based index

    while len(result) < half_len:
        for c in sorted(half_counter):
            if used[c] < half_counter[c]:
                used[c] += 1
                perms = count_palindromic_permutations(Counter({ch: half_counter[ch] - used[ch] for ch in half_counter}))
                if k < perms:
                    result.append(c)
                    break
                else:
                    k -= perms
                    used[c] -= 1
        else:
            return ''
    mid = odd_chars[0] if odd_chars else ''
    return ''.join(result) + mid + ''.join(result[::-1])

# Example usage:
s = input()
k = int(input())
print(kth_palindromic_permutation(s, k))