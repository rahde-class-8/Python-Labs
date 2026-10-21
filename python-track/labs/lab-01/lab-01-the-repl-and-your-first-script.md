## Lab 1 — The REPL and your first script

**Sections §1.1–1.2 · 25 minutes**

Goal: get comfortable in the read-eval-print loop, then learn the difference between typing at the interpreter and running a saved program.

**Steps**

1. Start the interpreter and confirm the version banner says 3.8 or newer:

   ```
   python3
   ```
2. At the `>>>` prompt, run each of these and watch what comes back:

   ```
   print('Hello World')
   6000 + 6000
   _ * 2
   _ + 100
   ```

   The `_` variable holds the result of the last operation. It exists only when working interactively — never use it in a saved program.
3. Exit with `quit()` or Ctrl-D (Ctrl-Z then Enter on Windows). Restart and confirm `_` is undefined until you evaluate something.
4. Leave the REPL. Create `hello.py`:

   ```python
   print('Hello World')
   ```

   Run it with `python3 hello.py`. Note that nothing echoes the way it did at the prompt — a script prints only what you tell it to.
5. Create `interest.py`, the compound-interest program the chapter opens with:

   ```python
   # interest.py
   
   principal = 1000       # Initial amount
   rate = 0.05            # Interest rate
   numyears = 5           # Number of years
   year = 1
   
   while year <= numyears:
       principal = principal * (1 + rate)
       print(year, principal)
       year += 1
   ```

   **What is a `while` loop?** A `while` loop repeats a block of code for as long as a condition stays true. Python checks the condition, runs the block if it is true, then returns to check the condition again. When the condition is false, Python skips the block and continues with the first line after the loop.

   **Syntax:**

   ```python
   while condition:
       statement
       statement
   ```

   - `while` is the keyword that starts the loop.
   - `condition` is an expression that evaluates to true or false, such as `year <= numyears`.
   - The colon `:` ends the header line. Leaving it out causes a `SyntaxError`.
   - The indented lines below the header are the **body**, which runs on each pass. Indent every line by the same amount; four spaces is the convention. The first line that is not indented marks the end of the loop.

   **What this loop does:** `year` starts at 1, and `year <= numyears` asks "is `year` 5 or less?" Each pass adds a year of interest to `principal`, prints the year and the new balance, and then adds 1 to `year` with `year += 1` (short for `year = year + 1`):

   | Pass | `year` at check | `year <= 5`? | `principal` after the pass |
   | --- | --- | --- | --- |
   | 1 | 1 | True | 1050.0 |
   | 2 | 2 | True | 1102.5 |
   | 3 | 3 | True | 1157.625 |
   | 4 | 4 | True | 1215.50625… |
   | 5 | 5 | True | 1276.28156… |
   | — | 6 | False | the loop stops |

   **Watch out:** something in the body must eventually make the condition false. If you delete `year += 1`, `year` stays 1 forever and the loop never ends. Press Ctrl-C to stop a runaway loop.

   Run it. The output columns are ugly on purpose — Lab 4 fixes that with f-strings.
6. Add a shebang line as the very first line of `interest.py`, make it executable, and run it without naming the interpreter:

   ```
   #!/usr/bin/env python3
   ```

   ```
   chmod +x interest.py
   ./interest.py
   ```

**Checkpoint** — `./interest.py` prints five lines ending in `1276.2815625000003`, and `python3 interest.py` prints the same thing.

**Stretch** — Change `numyears` to 30 and run again. Keep the file; Lab 5 writes this output to disk.

**Self-check**

- Why does `6000 + 6000` display a result at the prompt but not in a script?
- What is the shebang line for, and which platform ignores it?

---

[Python track index](../README.md) · [Paired AWS track lab 1](../../aws-track/labs/lab-01-boto3-in-the-repl-and-your-first-mocked-script.md) · [Lab 2 →](lab-02-primitives-variables-and-arithmetic.md)
