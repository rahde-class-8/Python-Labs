## Lab 9 — Exceptions and program termination

**Sections §1.14–1.15 · 25 minutes**

Goal: read a traceback fluently, handle the bad row in your data file, and learn the three ways a program can end.

**Steps**

1. Put the bad row back into `portfolio.csv`, as the fifth line:

   ```
   GE,95,N/A
   ```
2. Run `readport.py` from Lab 8 and read the traceback from the bottom up:

   ```
   Traceback (most recent call last):
     File "readport.py", line 9, in <module>
       shares = int(row[1])
   ValueError: invalid literal for int() with base 10: 'N/A'
   ```

   The last line gives the exception type and the reason; the lines above give the location. Always read the last line first.
3. Handle it. Wrap the per-row parsing in `try`/`except` and keep going:

   ```python
   # readport.py
   
   def read_portfolio(filename):
       portfolio = []
       with open(filename) as file:
           for line in file:
               row = line.split(',')
               try:
                   name = row[0]
                   shares = int(row[1])
                   price = float(row[2])
                   portfolio.append((name, shares, price))
               except ValueError as err:
                   print('Bad row:', row)
                   print('Reason:', err)
       return portfolio
   ```

   Note where the `try` sits: inside the loop, so one bad row skips one row rather than aborting the file.
4. Confirm that execution does *not* resume where the error occurred. Add `print('after except')` as the first line after the `except` block and trace the order of output.
5. Raise an exception yourself:

   ```python
   raise RuntimeError('Computer says no')
   ```
6. Use `try`/`finally` for cleanup that must happen either way:

   ```python
   import threading
   lock = threading.Lock()
   
   lock.acquire()
   try:
       print('working')
       raise RuntimeError('boom')
   finally:
       lock.release()          # Always runs
       print('lock released')
   ```

   Then rewrite it with `with lock:` and confirm the behaviour is identical with less code.
7. Terminate deliberately. Create `bail.py`:

   ```python
   import sys
   
   if len(sys.argv) != 2:
       raise SystemExit(f'Usage: {sys.argv[0]} filename')
   
   print('Got', sys.argv[1])
   ```

   Run it with no arguments, then with one. Check the shell exit status after each run with `echo $?`.
8. Register a cleanup handler:

   ```python
   import atexit
   
   def cleanup():
       print('Going away...')
   
   atexit.register(cleanup)
   print('main body done')
   ```

   Note the output order — the handler runs last, after the interpreter finishes.

**Checkpoint** — `readport.py` now reports one bad row, returns six holdings, and totals `40836.0` without crashing.

**Stretch** — Add a second `except IndexError` clause and test it by adding a line containing only `XYZ` to the data file.

**Self-check**

- After an exception is handled, where does execution resume?
- When would you prefer `try`/`finally` over `with`?

---

[← Lab 8](lab-08-iteration-and-functions.md) · [Python track index](../README.md) · [Paired AWS track lab 9](../../aws-track/labs/lab-09-clienterror-and-error-codes.md) · [Lab 10 →](lab-10-objects-and-classes.md)
