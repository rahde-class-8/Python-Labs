## Lab 3 — Conditionals and control flow

**Section §1.5 · 25 minutes**

Goal: write every branching and looping form the chapter introduces, and learn what Python treats as false.

**Steps**

1. Write `classify.py` using the full `if`/`elif`/`else` chain:

   ```python
   # classify.py
   
   for suffix in ['.htm', '.txt', '.csv', '.pdf']:
       if suffix == '.htm':
           content = 'text/html'
       elif suffix == '.jpg':
           content = 'image/jpeg'
       elif suffix == '.txt':
           content = 'text/plain'
       else:
           raise RuntimeError(f'Unknown content type {suffix!r}')
       print(suffix, content)
   ```

   Run it. It prints two lines and then crashes on `.csv`. Read the traceback — note that `!r` in the f-string printed the quotes around the suffix.
2. Add `.csv` as a fourth branch mapping to `'text/csv'`, then rerun. It should now crash only on `.pdf`.
3. Replace a four-line `if`/`else` with a conditional expression:

   ```python
   a, b = 17, 42
   maxval = a if a > b else b
   print(maxval)
   ```
4. Write `loops.py` exercising `break` and `continue` in the same file:

   ```python
   # loops.py
   
   x = 0
   while x < 10:
       x += 1
       if x == 5:
           continue      # Skips the print. Back to the top.
       if x == 8:
           break         # Leaves the loop entirely.
       print(x)
   print('Done, x =', x)
   ```

   Predict the output before running it.
5. Test truthiness directly — this is the single most useful thing in §1.5:

   ```python
   for value in [0, 1, -1, 0.0, '', 'a', [], [0], {}, None, False]:
       print(repr(value), '->', bool(value))
   ```

   Note that `[0]` is true while `0` is false, and that `-1` is true.
6. Break the indentation on purpose. In `loops.py`, indent the final `print` line by two extra spaces and run it. Read the `IndentationError`. Python does not mandate a particular width, but it must be consistent within a block; four spaces is the convention.

**Checkpoint** — `loops.py` prints `1 2 3 4 6 7` on separate lines, then `Done, x = 8`.

**Stretch** — Add an `else` clause to the `while` loop and work out when it runs. (It runs when the loop ends without `break`.)

**Self-check**

- Which values are false without being `False`?
- When does `continue` differ from simply ending the loop body?

---

[← Lab 2](lab-02-primitives-variables-and-arithmetic.md) · [Python track index](../README.md) · [Paired AWS track lab 3](../../aws-track/labs/lab-03-conditionals-over-aws-state.md) · [Lab 4 →](lab-04-text-strings-and-formatting.md)
