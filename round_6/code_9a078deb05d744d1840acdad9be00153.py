s = "aabb"
k = 2
```

**Output:**
```
baab
```

**Explanation:**  
The palindromic permutations of "aabb" in lexicographical order are: "abba", "baab". The 2nd one is "baab".

---

**Input:**
```
s = "aaa"
k = 3
```

**Output:**
```
-1
```

**Explanation:**  
There is only one palindromic permutation of "aaa".

## How It Works

1. The script checks if the input string is a palindrome.
2. It generates all unique palindromic permutations of the string.
3. It sorts them lexicographically.
4. It returns the k-th permutation if it exists, otherwise returns `-1`.

## Sample Run

```
Enter string s: aabb
Enter integer k: 2
baab