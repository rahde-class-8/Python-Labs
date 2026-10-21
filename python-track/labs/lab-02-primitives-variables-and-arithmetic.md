## Lab 2 — Primitives, variables, and arithmetic

**Sections §1.3–1.4 · 25 minutes**

Goal: know the four primitive types, understand that variables are names rather than typed boxes, and get the division operators right.

**Steps**

1. In the REPL, bind a name to values of different types in turn and check each with `type()`:

   ```python
   x = 42
   type(x)
   x = 42.0
   type(x)
   x = True
   type(x)
   x = 'forty-two'
   type(x)
   ```

   One name, four types. Python checks types at runtime, not at assignment.
2. Add an annotation and then violate it, to prove annotations are not enforced:

   ```python
   x: int = 42
   x = 'not an int'      # No error. The hint is informational only.
   ```
3. Work through the division operators and predict each answer *before* pressing Enter:

   ```python
   7 / 4
   7 // 4
   -7 // 4
   7 % 4
   -7 % 4
   7 ** 2
   2 ** 0.5
   divmod(7, 4)
   ```

   `/` always produces a float, even on two integers. `//` truncates toward negative infinity, which is why `-7 // 4` is `-2`, not `-1`.
4. Observe banker's rounding, which surprises nearly everyone:

   ```python
   round(0.5)
   round(1.5)
   round(2.5)
   round(1.23456, 2)
   ```

   Halfway values round to the nearest *even* multiple.
5. Try the integer bit operators:

   ```python
   x = 0b1010
   x << 1
   x >> 1
   x & 0b0110
   x | 0b0110
   x ^ 0b0110
   ~x
   bin(x << 1)
   ```
6. Create `augment.py` and confirm Python has no `++`:

   ```python
   x = 10
   x += 1
   x *= 3
   x //= 2
   x **= 2
   print(x)
   ```

   Then add the line `x++` and run it. Read the `SyntaxError` carefully — Python has no increment or decrement operator.

**Checkpoint** — `augment.py` prints `256` once you remove the `x++` line.

**Stretch** — Evaluate `0.1 + 0.2 == 0.3`. Explain the answer to yourself, then try `round(0.1 + 0.2, 10) == 0.3`.

**Self-check**

- Which operators produce a float even when both operands are integers?
- What does an annotation such as `x: int` actually do at runtime?

---

[← Lab 1](lab-01-the-repl-and-your-first-script.md) · [Python track index](../README.md) · [Paired AWS track lab 2](../../aws-track/labs/lab-02-aws-types-and-cost-arithmetic.md) · [Paired GCP track lab 2](../../gcp-track/labs/lab-02-cloud-types-and-cost-arithmetic.md) · [Lab 3 →](lab-03-conditionals-and-control-flow.md)
