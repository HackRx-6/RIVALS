def kth_palindromic_permutation(s, k):
    from math import factorial
    from collections import Counter

    def count_palindromic_permutations(half_counter):
        total = sum(half_counter.values())
        res = factorial(total)
        for v in half_counter.values():
            res //= factorial(v)
        return res

    def next_half(half_counter, k):
        half_len = sum(half_counter.values())
        half_chars = sorted(half_counter.keys())
        result = []
        for _ in range(half_len):
            for ch in half_chars:
                if half_counter[ch] == 0:
                    continue
                half_counter[ch] -= 1
                cnt = count_palindromic_permutations(half_counter)
                if k > cnt:
                    k -= cnt
                    half_counter[ch] += 1
                else:
                    result.append(ch)
                    break
        return ''.join(result)

    counter = Counter(s)
    odd_chars = [ch for ch, cnt in counter.items() if cnt % 2 == 1]
    if len(odd_chars) > 1:
        return ''
    half_counter = {ch: cnt // 2 for ch, cnt in counter.items()}
    total_perms = count_palindromic_permutations(half_counter)
    if k > total_perms:
        return ''
    half_str = next_half(Counter(half_counter), k)
    mid = odd_chars[0] if odd_chars else ''
    return half_str + mid + half_str[::-1]