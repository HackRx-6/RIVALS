def kth_palindromic_permutation(s, k):
    from collections import Counter
    from math import factorial

    def unique_half_permutations(half_counter):
        # Count unique permutations of the half string
        total = sum(half_counter.values())
        res = factorial(total)
        for v in half_counter.values():
            res //= factorial(v)
        return res

    def next_half_perm(half_counter, k):
        # Generate the k-th lexicographical half permutation
        half_len = sum(half_counter.values())
        result = []
        chars = sorted(half_counter.keys())
        for _ in range(half_len):
            for c in chars:
                if half_counter[c] == 0:
                    continue
                half_counter[c] -= 1
                perms = unique_half_permutations(half_counter)
                if perms < k:
                    k -= perms
                    half_counter[c] += 1
                else:
                    result.append(c)
                    break
        return ''.join(result)

    freq = Counter(s)
    odd_chars = [c for c in freq if freq[c] % 2 == 1]
    if len(odd_chars) > 1:
        return ''
    half_counter = {}
    for c in freq:
        half_counter[c] = freq[c] // 2
    total_perms = unique_half_permutations(half_counter)
    if k > total_perms:
        return ''
    half_str = next_half_perm(half_counter.copy(), k)
    mid = odd_chars[0] if odd_chars else ''
    return half_str + mid + half_str[::-1]

# Example usage:
s = input()
k = int(input())
print(kth_palindromic_permutation(s, k))