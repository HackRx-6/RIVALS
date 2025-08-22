import os
import math
from collections import Counter

def kth_palindromic_permutation(s, k):
    n = len(s)
    count = Counter(s)
    odd = [ch for ch in count if count[ch] % 2 == 1]
    if len(odd) > 1:
        return ""
    half = []
    mid = ''
    for ch in sorted(count):
        if count[ch] % 2 == 1:
            mid = ch
        half.extend([ch] * (count[ch] // 2))
    def fact(n):
        return math.factorial(n)
    def count_perm(half_count):
        total = sum(half_count.values())
        res = fact(total)
        for v in half_count.values():
            res //= fact(v)
        return res
    half_count = Counter(half)
    res = []
    k -= 1
    for i in range(len(half)):
        for ch in sorted(half_count):
            if half_count[ch] == 0:
                continue
            half_count[ch] -= 1
            cnt = count_perm(half_count)
            if k < cnt:
                res.append(ch)
                break
            else:
                k -= cnt
                half_count[ch] += 1
    first_half = ''.join(res)
    second_half = first_half[::-1]
    return first_half + mid + second_half

def main():
    s = input("Enter the palindromic string: ")
    k = int(input("Enter k: "))
    result = kth_palindromic_permutation(s, k)
    print(result)

os.makedirs('round_6', exist_ok=True)
with open('round_6/palindromic_permutation.py', 'w') as f:
    f.write('import math\n')
    f.write('from collections import Counter\n\n')
    f.write('def kth_palindromic_permutation(s, k):\n')
    f.write('    n = len(s)\n')
    f.write('    count = Counter(s)\n')
    f.write('    odd = [ch for ch in count if count[ch] % 2 == 1]\n')
    f.write('    if len(odd) > 1:\n')
    f.write('        return ""\n')
    f.write('    half = []\n')
    f.write('    mid = \'\'\n')
    f.write('    for ch in sorted(count):\n')
    f.write('        if count[ch] % 2 == 1:\n')
    f.write('            mid = ch\n')
    f.write('        half.extend([ch] * (count[ch] // 2))\n')
    f.write('    def fact(n):\n')
    f.write('        return math.factorial(n)\n')
    f.write('    def count_perm(half_count):\n')
    f.write('        total = sum(half_count.values())\n')
    f.write('        res = fact(total)\n')
    f.write('        for v in half_count.values():\n')
    f.write('            res //= fact(v)\n')
    f.write('        return res\n')
    f.write('    half_count = Counter(half)\n')
    f.write('    res = []\n')
    f.write('    k -= 1\n')
    f.write('    for i in range(len(half)):\n')
    f.write('        for ch in sorted(half_count):\n')
    f.write('            if half_count[ch] == 0:\n')
    f.write('                continue\n')
    f.write('            half_count[ch] -= 1\n')
    f.write('            cnt = count_perm(half_count)\n')
    f.write('            if k < cnt:\n')
    f.write('                res.append(ch)\n')
    f.write('                break\n')
    f.write('            else:\n')
    f.write('                k -= cnt\n')
    f.write('                half_count[ch] += 1\n')
    f.write('    first_half = \'\'.join(res)\n')
    f.write('    second_half = first_half[::-1]\n')
    f.write('    return first_half + mid + second_half\n\n')
    f.write('def main():\n')
    f.write('    s = input("Enter the palindromic string: ")\n')
    f.write('    k = int(input("Enter k: "))\n')
    f.write('    result = kth_palindromic_permutation(s, k)\n')
    f.write('    print(result)\n\n')
    f.write('if __name__ == "__main__":\n')
    f.write('    main()\n')