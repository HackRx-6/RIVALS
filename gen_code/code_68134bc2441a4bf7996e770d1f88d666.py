from collections import Counter
import math

def input_data():
    s = input().strip()
    k = int(input())
    return s, k

def factorial(n):
    return math.factorial(n)

def count_palindromic_permutations(char_counts):
    half_counts = [v // 2 for v in char_counts.values()]
    total = sum(half_counts)
    denom = 1
    for c in half_counts:
        denom *= factorial(c)
    return factorial(total) // denom

def kth_palindromic_permutation(s, k):
    count = Counter(s)
    odd_chars = [c for c in count if count[c] % 2 == 1]
    if len(odd_chars) > 1:
        return ""
    half = []
    for c in sorted(count):
        half.extend([c] * (count[c] // 2))
    used = Counter()
    n = len(half)
    result = []
    chars = sorted(set(half))
    while len(result) < n:
        for c in chars:
            if used[c] < half.count(c):
                used[c] += 1
                temp_counts = Counter()
                for ch in chars:
                    temp_counts[ch] = half.count(ch) - used[ch]
                perms = count_palindromic_permutations(temp_counts)
                if k > perms:
                    k -= perms
                    used[c] -= 1
                else:
                    result.append(c)
                    break
    first_half = ''.join(result)
    second_half = first_half[::-1]
    mid = odd_chars[0] if odd_chars else ''
    return first_half + mid + second_half

s, k = input_data()
print(kth_palindromic_permutation(s, k))