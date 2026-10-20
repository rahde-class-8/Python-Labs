## Lab 5 — File input and output

**Section §1.7 · 25 minutes**

Goal: read and write files using the `with` statement, and create the data file that the next seven labs depend on.

**Steps**

1. Create `portfolio.csv` in your editor. Keep it exactly as written — the bad row in the middle is deliberate, and Lab 9 handles it:

   ```
   AA,100,32.20
   IBM,50,91.10
   CAT,150,83.44
   MSFT,200,51.23
   GE,95,N/A
   MSFT,50,65.10
   IBM,100,70.44
   ```
2. Read it line by line. This is the idiomatic form — the file closes itself when the block ends:

   ```python
   with open('portfolio.csv') as file:
       for line in file:
           print(line, end='')
   ```

   `end=''` suppresses the extra newline, because each line already carries one.
3. Compare the three ways of pulling content in:

   ```python
   with open('portfolio.csv') as file:
       data = file.read()          # Entire file as one string
   len(data)
   
   with open('portfolio.csv') as file:
       lines = file.readlines()    # List of strings, newlines kept
   len(lines)
   ```
4. See why `with` is worth the habit. Do it the manual way and then forget the `close()`:

   ```python
   file = open('portfolio.csv')
   data = file.read()
   file.close()                    # Easy to forget. with does it for you.
   ```
5. Redirect `interest.py` output to a file. Copy it to `interest_out.py` and wrap the loop:

   ```python
   # interest_out.py
   
   principal = 1000
   rate = 0.05
   numyears = 5
   year = 1
   
   with open('out.txt', 'wt') as out:
       while year <= numyears:
           principal = principal * (1 + rate)
           print(f'{year:>3d} {principal:0.2f}', file=out)
           year += 1
   ```

   Run it, then `cat out.txt`. The `file=` argument to `print()` is the easiest way to write formatted text.
6. Write with the `write()` method instead, and note that it adds no newline for you:

   ```python
   with open('note.txt', 'wt') as out:
       out.write('first line\n')
       out.write('second line')
       out.write(' — still the second line\n')
   ```
7. Open `out.txt` in append mode and confirm the difference from `'wt'`:

   ```python
   with open('out.txt', 'at') as out:
       print('appended', file=out)
   ```

   Then rerun `interest_out.py` and check that `'wt'` truncated the file.

**Checkpoint** — `portfolio.csv` has seven rows, `out.txt` has five formatted lines, and `note.txt` has two lines.

**Stretch** — Write a three-line script that counts the lines in `portfolio.csv` without loading the whole file into memory.

**Self-check**

- What does `with` do that a bare `open()` does not?
- Why does `print(line)` inside a file loop produce blank lines between rows?

---

[← Lab 4](lab-04-text-strings-and-formatting.md) · [Python track index](../README.md) · [Paired AWS track lab 5](../../aws-track/labs/lab-05-local-files-to-s3-and-back.md) · [Lab 6 →](lab-06-lists-and-tuples.md)
