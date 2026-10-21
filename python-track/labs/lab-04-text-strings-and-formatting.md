## Lab 4 — Text strings and formatting

**Section §1.6 · 30 minutes**

Goal: fix the ugly output from Lab 1, and learn slicing and the string methods you will use every day.

**Steps**

1. Try all the quoting forms. They are interchangeable except for what they let you embed:

   ```python
   a = 'single'
   b = "double"
   c = '''triple
   spans lines'''
   d = "it's easier in double quotes"
   print(c)
   ```
2. Confirm that adjacent string literals concatenate with no operator at all:

   ```python
   s = ('Content-type: text/html\n'
        '\n'
        '<h1>Hello World</h1>\n')
   print(s)
   ```
3. Now rewrite `interest.py` from Lab 1 to format its columns. Replace the `print(year, principal)` line with each of these in turn, running the script after each change:

   ```python
   print(f'{year:>3d} {principal:0.2f}')
   print('{0:>3d} {1:0.2f}'.format(year, principal))
   print('%3d %0.2f' % (year, principal))
   ```

   All three produce the same output. The f-string is the one to use; the other two are what you will meet in older code.
4. Practice indexing and slicing. Negative indices count from the end:

   ```python
   s = 'Hello World'
   s[0]
   s[-1]
   s[:5]
   s[6:]
   s[6:11]
   s[::-1]
   s[0] = 'J'        # TypeError. Strings are immutable.
   ```
5. Work the common methods from Table 1.6:

   ```python
   s = '  GOOG,100,490.10  \n'
   s.strip()
   s.strip().split(',')
   s.lower()
   s.replace('GOOG', 'IBM')
   s.strip().startswith('GOOG')
   s.find('100')
   ','.join(['a', 'b', 'c'])
   ```

   `strip()` then `split(',')` is the two-step move Lab 6 uses to parse data files.
6. Convert between strings and numbers in both directions:

   ```python
   x = '37'
   y = '42'
   x + y                 # '3742' — concatenation, not addition
   int(x) + int(y)       # 79
   float('490.10')
   str(79)
   repr(79)
   format(12.34567, '0.2f')
   f'{12.34567:0.2f}'
   int('N/A')            # ValueError. Lab 9 handles this.
   ```

**Checkpoint** — `interest.py` now prints a right-aligned year column and two-decimal amounts, the last line reading `   5 1276.28 `.

**Stretch** — Add a header row and a thousands separator: `f'{principal:>12,.2f}'`.

**Self-check**

- What is the difference between `str(x)` and `repr(x)`?
- Why does `s[0] = 'J'` fail when `names[0] = 'J'` works on a list?

---

[← Lab 3](lab-03-conditionals-and-control-flow.md) · [Python track index](../README.md) · [Paired AWS track lab 4](../../aws-track/labs/lab-04-arn-and-s3-key-string-surgery.md) · [Paired GCP track lab 4](../../gcp-track/labs/lab-04-resource-names-urls-and-gs-string-surgery.md) · [Lab 5 →](lab-05-file-input-and-output.md)
