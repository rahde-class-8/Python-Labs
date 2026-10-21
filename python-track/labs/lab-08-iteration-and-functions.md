## Lab 8 — Iteration and functions

**Sections §1.12–1.13 · 30 minutes**

Goal: iterate over every kind of object the chapter mentions, then package your portfolio code into real functions.

**Steps**

1. Loop over a list, then replace it with `range()`:

   ```python
   for n in [1, 2, 3, 4, 5, 6, 7, 8, 9]:
       print(f'2 to the {n} power is {2**n}')
   
   for n in range(1, 10):
       print(f'2 to the {n} power is {2**n}')
   ```
2. Try every `range()` form and convert each to a list to see it:

   ```python
   list(range(5))            # 0 1 2 3 4
   list(range(1, 8))         # 1 through 7
   list(range(0, 14, 3))     # 0 3 6 9 12
   list(range(8, 1, -1))     # 8 down to 2
   range(1000000)            # Cheap — values computed on demand
   ```
3. Iterate over the four other kinds of object:

   ```python
   for c in 'Hello World':
       print(c)
   
   for name in ['Dave', 'Mark', 'Ann', 'Phil']:
       print(name)
   
   prices = {'GOOG': 490.10, 'IBM': 91.50, 'AAPL': 123.15}
   for key in prices:                 # Iterates keys
       print(key, '=', prices[key])
   
   with open('portfolio.csv') as file:
       for line in file:
           print(line, end='')
   ```
4. Write a function with a docstring, then read it back with `help()`:

   ```python
   def remainder(a, b):
       '''
       Computes the remainder of dividing a by b
       '''
       q = a // b
       r = a - q * b
       return r
   
   remainder(37, 15)
   help(remainder)
   ```
5. Add annotations, then call it with floats to confirm nothing is enforced:

   ```python
   def remainder(a: int, b: int) -> int:
       '''
       Computes the remainder of dividing a by b
       '''
       q = a // b
       r = a - q * b
       return r
   
   remainder(37.5, 3.2)      # Works. Annotations are informational.
   ```
6. Return multiple values as a tuple and unpack them:

   ```python
   def divide(a, b):
       q = a // b
       r = a - q * b
       return (q, r)
   
   quotient, remainder_val = divide(1456, 33)
   ```
7. Use default and keyword arguments:

   ```python
   def connect(hostname, port, timeout=300):
       print(f'{hostname}:{port} timeout={timeout}')
   
   connect('www.python.org', 80)
   connect('www.python.org', 80, 500)
   connect('www.python.org', 80, timeout=500)      # Clearer
   connect(port=80, hostname='www.python.org')     # Order stops mattering
   ```
8. Prove the scoping rule, which has one surprise:

   ```python
   debug = True            # Global
   
   def read_data(filename):
       local_var = 'invisible outside'
       if debug:           # Globals are readable
           print('Reading', filename)
   
   read_data('portfolio.csv')
   print(local_var)        # NameError — destroyed when the function returned
   ```
9. Refactor `readport.py` into a function that takes the filename as a parameter and returns the portfolio:

   ```python
   # readport.py
   
   def read_portfolio(filename):
       portfolio = []
       with open(filename) as file:
           for line in file:
               row = line.split(',')
               name = row[0]
               shares = int(row[1])
               price = float(row[2])
               portfolio.append((name, shares, price))
       return portfolio
   
   def portfolio_cost(filename):
       '''
       Compute the total shares*price of a portfolio
       '''
       port = read_portfolio(filename)
       return sum(shares * price for _, shares, price in port)
   
   print(portfolio_cost('portfolio.csv'))
   ```

**Checkpoint** — `readport.py` prints `40836.0`, and `help(read_portfolio)` shows your docstring.

**Stretch** — Give `read_portfolio` a `separator=','` default argument and read a tab-separated copy of the file with it.

**Self-check**

- Why is `range(1000000)` cheap to create?
- What happens to a variable assigned inside a function when it returns?

---

[← Lab 7](lab-07-sets-and-dictionaries.md) · [Python track index](../README.md) · [Paired AWS track lab 8](../../aws-track/labs/lab-08-paginators-as-iteration-functions-as-the-fix.md) · [Paired GCP track lab 8](../../gcp-track/labs/lab-08-iterators-as-iteration-functions-as-the-fix.md) · [Lab 9 →](lab-09-exceptions-and-program-termination.md)
