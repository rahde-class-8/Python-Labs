## Lab 11 — Modules and script writing

**Sections §1.17–1.18 · 30 minutes**

Goal: split your code across files, then make a file work as both a library and a command-line script.

**Steps**

1. Reduce `readport.py` to a pure module — definitions only, no top-level `print`:

   ```python
   # readport.py
   #
   # Reads a file of 'NAME,SHARES,PRICE' data
   
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
2. Create a second file, `pcost.py`, that imports it:

   ```python
   # pcost.py
   
   import readport
   
   def portfolio_cost(filename):
       '''
       Compute the total shares*price of a portfolio
       '''
       port = readport.read_portfolio(filename)
       return sum(shares * price for _, shares, price in port)
   ```
3. Use them from the REPL and try all three import forms:

   ```python
   import pcost
   pcost.portfolio_cost('portfolio.csv')
   
   import readport as rp
   rp.read_portfolio('portfolio.csv')
   
   from readport import read_portfolio
   read_portfolio('portfolio.csv')
   
   import readport
   dir(readport)              # See the namespace the import created
   ```
4. Cause an `ImportError` on purpose, then diagnose it:

   ```python
   import sys
   sys.path              # The directories Python searches
   ```

   Change to a different directory, start `python3`, and run `import readport`. Read the `ModuleNotFoundError`, then confirm your old directory is absent from `sys.path`.
5. Replace the hand-rolled parsing with the `csv` standard library module:

   ```python
   # readport.py
   #
   # Reads a file of 'NAME,SHARES,PRICE' data
   
   import csv
   
   def read_portfolio(filename):
       portfolio = []
       with open(filename) as file:
           rows = csv.reader(file)
           for row in rows:
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

   Note that `csv.reader` returns already-split lists, so `line.split(',')` is gone.
6. Add a `main()` and the `__name__` guard:

   ```python
   def main():
       portfolio = read_portfolio('portfolio.csv')
       for name, shares, price in portfolio:
           print(f'{name:>10s} {shares:10d} {price:10.2f}')
   
   if __name__ == '__main__':
       main()
   ```

   Run `python3 readport.py` — the table prints. Then run `python3 -c "import readport"` — nothing prints. Confirm why:

   ```python
   import readport
   readport.__name__          # 'readport'
   ```
7. Accept the filename from the command line, falling back to a prompt:

   ```python
   def main(argv):
       if len(argv) == 1:
           filename = input('Enter filename: ')
       elif len(argv) == 2:
           filename = argv[1]
       else:
           raise SystemExit(f'Usage: {argv[0]} [ filename ]')
       portfolio = read_portfolio(filename)
       for name, shares, price in portfolio:
           print(f'{name:>10s} {shares:10d} {price:10.2f}')
   
   if __name__ == '__main__':
       import sys
       main(sys.argv)
   ```
8. Exercise all three invocation paths:

   ```
   python3 readport.py
   python3 readport.py portfolio.csv
   python3 readport.py a b c
   ```

**Checkpoint** — All three commands behave as the chapter describes, and importing `readport` prints nothing.

**Stretch** — Swap `sys.argv` for `argparse` and add a `--total` flag that prints the cost instead of the table.

**Self-check**

- What is `__name__` set to when the file is imported rather than run?
- Why should a module avoid doing work at the top level?

---

[← Lab 10](lab-10-objects-and-classes.md) · [Python track index](../README.md) · [Paired AWS track lab 11](../../aws-track/labs/lab-11-a-module-and-a-cli.md) · [Paired GCP track lab 11](../../gcp-track/labs/lab-11-a-module-and-a-cli.md) · [Lab 12 →](lab-12-packages-structure-and-third-party-code.md)
