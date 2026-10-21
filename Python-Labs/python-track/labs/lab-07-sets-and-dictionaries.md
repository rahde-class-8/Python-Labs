## Lab 7 — Sets and dictionaries

**Sections §1.10–1.11 · 30 minutes**

Goal: use sets for membership and uniqueness, and dictionaries for lookup and tabulation. This is the densest lab in the chapter.

**Steps**

1. Create sets both ways and watch the duplicates vanish:

   ```python
   names1 = {'IBM', 'MSFT', 'AA'}
   names2 = set(['IBM', 'MSFT', 'HPE', 'IBM', 'CAT'])
   names2                    # 'IBM' appears once; order unpredictable
   len(names2)
   empty = set()             # {} would be an empty dict, not a set
   {['a']}                   # TypeError — lists are unhashable
   ```

   Run the script twice. The display order may differ between runs; sets are unordered.
2. Work the four set algebra operations:

   ```python
   t = {'IBM', 'MSFT', 'HPE', 'CAT'}
   s = {'IBM', 'MSFT', 'AA'}
   t | s      # Union
   t & s      # Intersection
   t - s      # In t but not s
   s - t      # In s but not t
   t ^ s      # In one or the other, not both
   ```
3. Mutate sets, and learn the one difference that matters:

   ```python
   t.add('DIS')
   s.update({'JJ', 'GE', 'ACME'})
   t.remove('IBM')
   t.remove('NOPE')      # KeyError
   t.discard('NOPE')     # Silent. This is the difference.
   ```
4. Build a set comprehension from your Lab 6 portfolio:

   ```python
   names = {s[0] for s in portfolio}
   ```
5. Build and use a dictionary:

   ```python
   s = {'name': 'GOOG', 'shares': 100, 'price': 490.10}
   s['name']
   s['shares'] * s['price']
   s['shares'] = 75
   s['date'] = '2007-06-07'      # New key, added on assignment
   ```
6. Handle missing keys three ways, from worst to best:

   ```python
   prices = {'GOOG': 490.1, 'AAPL': 123.5, 'IBM': 91.5, 'MSFT': 52.13}
   
   prices['NOPE']                 # KeyError
   
   if 'IBM' in prices:            # Works, but verbose
       p = prices['IBM']
   else:
       p = 0.0
   
   p = prices.get('IBM', 0.0)     # The idiomatic form
   p = prices.get('NOPE', 0.0)
   
   del prices['GOOG']
   ```
7. Use a tuple as a composite key — the reason tuples are immutable:

   ```python
   quotes = {}
   quotes[('IBM', '2015-02-03')] = 91.23
   quotes['IBM', '2015-02-04'] = 91.42     # Parens optional
   quotes
   quotes[['IBM', '2015-02-05']] = 91.0    # TypeError — list is unhashable
   ```
8. Tabulate total shares per symbol, first by hand with a dict comprehension, then with the standard library:

   ```python
   total_shares = {s[0]: 0 for s in portfolio}
   for name, shares, _ in portfolio:
       total_shares[name] += shares
   print(total_shares)
   
   from collections import Counter
   total_shares = Counter()
   for name, shares, _ in portfolio:
       total_shares[name] += shares
   print(total_shares)
   ```

   `Counter` needs no initialization pass — a missing key starts at zero.
9. Inspect the three views and confirm that a view is live:

   ```python
   d = {'x': 2, 'y': 3}
   k = d.keys()
   k
   d['z'] = 4
   k              # 'z' is already there — the view tracks the dict
   list(d)        # A snapshot instead
   d.values()
   for sym, price in prices.items():
       print(f'{sym} = {price}')
   ```

**Checkpoint** — `total_shares` is `{'AA': 100, 'IBM': 150, 'CAT': 150, 'MSFT': 250}` and the symbol set has four members.

**Stretch** — Find the symbols held in `portfolio` but absent from `prices`, using one set operation.

**Self-check**

- Why can a tuple be a dict key but a list cannot?
- What does `{}` create, and how do you create the other one?

---

[← Lab 6](lab-06-lists-and-tuples.md) · [Python track index](../README.md) · [Paired AWS track lab 7](../../aws-track/labs/lab-07-sets-for-iam-policy-diffing-dicts-for-tags.md) · [Lab 8 →](lab-08-iteration-and-functions.md)
