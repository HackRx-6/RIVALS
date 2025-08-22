def kth_palindromic_permutation(s, k):
    from collections import Counter
    from math import factorial

    def count_perms(half_counter):
        total = sum(half_counter.values())
        res = factorial(total)
        for v in half_counter.values():
            res //= factorial(v)
        return res

    def next_perm(half_counter, k, half_len):
        res = []
        chars = sorted(half_counter)
        for _ in range(half_len):
            for c in chars:
                if half_counter[c] == 0:
                    continue
                half_counter[c] -= 1
                perms = count_perms(half_counter)
                if perms < k:
                    k -= perms
                    half_counter[c] += 1
                else:
                    res.append(c)
                    break
            else:
                return None
        return ''.join(res)

    n = len(s)
    counter = Counter(s)
    odd = [c for c in counter if counter[c] % 2 == 1]
    if len(odd) > 1:
        return ""
    half_counter = {c: counter[c] // 2 for c in counter}
    half_len = sum(half_counter.values())
    total_perms = count_perms(half_counter.copy())
    if k > total_perms:
        return ""
    half = next_perm(half_counter.copy(), k, half_len)
    if half is None:
        return ""
    mid = odd[0] if odd else ''
    return half + mid + half[::-1]

s = input()
k = int(input())
print(kth_palindromic_permutation(s, k))