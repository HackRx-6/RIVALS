def kth_palindromic_permutation(s, k):
    from collections import Counter
    import math

    def factorial(n):
        return math.factorial(n)

    def count_palindromic_permutations(half_counter):
        total = sum(half_counter.values())
        res = factorial(total)
        for v in half_counter.values():
            res //= factorial(v)
        return res

    def next_palindrome(half_counter, mid_char, k):
        half_len = sum(half_counter.values())
        half_chars = sorted(half_counter.keys())
        result = []
        for _ in range(half_len):
            for ch in half_chars:
                if half_counter[ch] == 0:
                    continue
                half_counter[ch] -= 1
                cnt = count_palindromic_permutations(half_counter)
                if cnt < k:
                    k -= cnt
                    half_counter[ch] += 1
                else:
                    result.append(ch)
                    break
        return ''.join(result) + mid_char + ''.join(result[::-1])

    counter = Counter(s)
    odd_chars = [ch for ch, cnt in counter.items() if cnt % 2 == 1]
    if len(odd_chars) > 1:
        return ''
    mid_char = odd_chars[0] if odd_chars else ''
    half_counter = {ch: cnt // 2 for ch, cnt in counter.items()}
    total_perms = count_palindromic_permutations(Counter(half_counter))
    if k > total_perms:
        return ''
    return next_palindrome(Counter(half_counter), mid_char, k)

# Test
s = input("Enter palindromic string: ")
k = int(input("Enter k: "))
print(kth_palindromic_permutation(s, k))