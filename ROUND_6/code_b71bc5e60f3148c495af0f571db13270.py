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
    half_counter = {c: v // 2 for c, v in freq.items()}
    half_chars = sorted(half_counter.keys())
    half_len = sum(half_counter.values())
    mid = odd_chars[0] if odd_chars else ''
    result = []
    k -= 1  # 0-based index

    for _ in range(half_len):
        for c in half_chars:
            if half_counter[c] == 0:
                continue
            half_counter[c] -= 1
            cnt = count_palindromic_permutations(half_counter)
            if k < cnt:
                result.append(c)
                break
            else:
                k -= cnt
                half_counter[c] += 1
        else:
            return ''
    first_half = ''.join(result)
    second_half = first_half[::-1]
    return first_half + mid + second_half

# Example usage:
s = input()
k = int(input())
print(kth_palindromic_permutation(s, k))