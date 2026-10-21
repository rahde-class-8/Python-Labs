## Lab 6 — Lists and tuples

**Sections §1.8–1.9 · 30 minutes**

Goal: build the list-of-tuples structure the chapter uses for tabular data, and learn when mutability matters.

**Steps**

1. Exercise the list operations:

   ```python
   names = ['Dave', 'Paula', 'Thomas', 'Lewis']
   names[2]
   names[2] = 'Tom'
   names.append('Alex')
   names.insert(2, 'Aya')
   names.remove('Paula')
   len(names)
   names + ['Mark']
   'Dave' in names
   ```
2. Slice, and then assign *to* a slice — something strings cannot do:

   ```python
   a = [1, 2, 3, 4, 5, 6, 7, 8]
   a[2:5]
   a[:3]
   a[::2]
   a[2:5] = ['x', 'y']       # Replaces three items with two
   a
   del a[0]
   a
   ```
3. Sort in place and note that `sort()` returns `None`:

   ```python
   nums = [10, 2, 33, 4]
   nums.sort()
   nums
   result = nums.sort()      # result is None — a common bug
   print(result)
   sorted([10, 2, 33, 4])    # Returns a new list instead
   ```
4. Write a list comprehension, the form that replaces most short loops:

   ```python
   nums = [1, 2, 3, 4, 5]
   squares = [n * n for n in nums]
   evens = [n for n in nums if n % 2 == 0]
   ```
5. Build tuples and learn the one-element trap:

   ```python
   holding = ('GOOG', 100, 490.10)
   address = ('www.python.org', 80)
   empty = ()
   one = ('GOOG',)          # Trailing comma required
   not_a_tuple = ('GOOG')   # This is just a string
   type(one), type(not_a_tuple)
   name, shares, price = holding    # Unpacking
   holding[1] = 50          # TypeError. Tuples are immutable.
   ```
6. Now parse `portfolio.csv` into a list of tuples. Create `readport.py` — you will keep extending this file through Lab 12:

   ```python
   # readport.py
   
   filename = 'portfolio.csv'
   
   portfolio = []
   with open(filename) as file:
       for line in file:
           row = line.split(',')
           name = row[0]
           shares = int(row[1])
           price = float(row[2])
           holding = (name, shares, price)
           portfolio.append(holding)
   
   print(portfolio[0])
   print(portfolio[1][1])
   ```

   Run it. It crashes on the `GE,95,N/A` row with a `ValueError`. That is expected — for now, delete the GE line from `portfolio.csv` and rerun. Lab 9 puts it back and handles it properly.
7. Total the portfolio two ways, and meet the throwaway `_` variable:

   ```python
   total = 0.0
   for name, shares, price in portfolio:
       total += shares * price
   
   total = sum([shares * price for _, shares, price in portfolio])
   ```

**Checkpoint** — `readport.py` prints `('AA', 100, 32.2)` and `50`, and with the GE row removed the portfolio total is `40836.0`.

**Stretch** — Sort the portfolio by price, descending: `portfolio.sort(key=lambda h: h[2], reverse=True)`.

**Self-check**

- When would you choose a tuple over a list for the same three values?
- Why does `('GOOG')` not produce a tuple?

---

[← Lab 5](lab-05-file-input-and-output.md) · [Python track index](../README.md) · [Paired AWS track lab 6](../../aws-track/labs/lab-06-lists-and-tuples-from-aws-responses.md) · [Paired GCP track lab 6](../../gcp-track/labs/lab-06-lists-and-tuples-from-cloud-listings.md) · [Lab 7 →](lab-07-sets-and-dictionaries.md)
