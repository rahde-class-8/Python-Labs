## Lab 11 — A module and a CLI

**Pairs with Python Lab 11 (§1.17–1.18) · 30 minutes**

Goal: split the Google Cloud code into an importable module and a command-line tool, and solve the problem emulation creates for a real CLI.

**Steps**

1. Rewrite `gcpport.py` as a pure module — definitions only, and note that it takes a client as an argument rather than creating one:

   ```python
   # gcpport.py
   #
   # Reads 'NAME,SHARES,PRICE' portfolio data out of Cloud Storage

   import csv
   from google.api_core.exceptions import NotFound

   def read_portfolio(client, bucket, name):
       '''
       Read a portfolio CSV from Cloud Storage and return a list of (name, shares, price).
       '''
       blob = client.bucket(bucket).blob(name)
       portfolio = []
       try:
           with blob.open('r') as f:
               for row in csv.reader(f):
                   if not row:
                       continue
                   try:
                       portfolio.append((row[0], int(row[1]), float(row[2])))
                   except (ValueError, IndexError) as err:
                       print('Bad row:', row)
                       print('Reason:', err)
       except NotFound:
           raise SystemExit(f'No such object: gs://{bucket}/{name}')
       return portfolio

   def portfolio_cost(client, bucket, name):
       '''
       Compute the total shares*price of a portfolio stored in Cloud Storage.
       '''
       return sum(shares * price
                  for _, shares, price in read_portfolio(client, bucket, name))
   ```

   Three things worth noticing. `csv.reader` takes the file object from `blob.open('r')` directly, exactly as it took `open(filename)` on the Python track — no `io.StringIO` step. The `except (ValueError, IndexError)` tuple catches either. And passing `client` in rather than building it inside is what makes this module testable at all.
2. Create `pcost_gcp.py` that imports it, and try the import forms:

   ```python
   # pcost_gcp.py
   import gcpport

   def report(client, bucket, name):
       port = gcpport.read_portfolio(client, bucket, name)
       for sym, shares, price in port:
           print(f'{sym:>10s} {shares:10d} {price:10.2f}')
       print(f'{"TOTAL":>10s} {"":10s} {sum(s * p for _, s, p in port):10.2f}')
   ```

   ```python
   import gcpport as gp
   from gcpport import read_portfolio
   import gcpport
   dir(gcpport)
   ```
3. Add a `main()` and the `__name__` guard to `gcpport.py`. This is where emulation gets interesting:

   ```python
   # Append to gcpport.py

   def main(argv):
       from google.cloud import storage
       if len(argv) == 2 and argv[1].startswith('gs://'):
           bucket, _, name = argv[1].removeprefix('gs://').partition('/')
       elif len(argv) == 1:
           bucket = input('Bucket: ')
           name = input('Object: ')
       else:
           raise SystemExit(f'Usage: {argv[0]} [ gs://bucket/object ]')

       client = storage.Client()
       for sym, shares, price in read_portfolio(client, bucket, name):
           print(f'{sym:>10s} {shares:10d} {price:10.2f}')

   if __name__ == '__main__':
       import sys
       main(sys.argv)
   ```

   The argument parsing is Lab 4's `gs://` surgery.
4. Run it and watch it fail:

   ```
   python3 gcpport.py gs://pydistilled-labs/data/portfolio.csv
   ```

   It cannot work. There is no emulator running and no real bucket, so you get `DefaultCredentialsError` (or, if you are logged in to Google Cloud, a `NotFound` from your real project). The module is correct; the problem is that the data does not exist anywhere.
5. Solve it with a seeding script, which is the realistic pattern. Create `demo.py`:

   ```python
   # demo.py
   from google.cloud import storage
   from gcpmock import mock_gcs
   import gcpport

   BUCKET = 'pydistilled-labs'
   NAME = 'data/portfolio.csv'

   def main():
       with mock_gcs():
           client = storage.Client(project='pydistilled')
           bucket = client.create_bucket(BUCKET)
           bucket.blob(NAME).upload_from_filename('portfolio.csv')

           port = gcpport.read_portfolio(client, BUCKET, NAME)
           for sym, shares, price in port:
               print(f'{sym:>10s} {shares:10d} {price:10.2f}')
           print('total:', gcpport.portfolio_cost(client, BUCKET, NAME))

   if __name__ == '__main__':
       main()
   ```

   Run `python3 demo.py`. The bad `GE,95,N/A` row is reported and skipped, exactly as on the Python track, and the total comes out. `gcpport.py` itself knows nothing about the emulator — that is the point of taking `client` as an argument.
6. Confirm the import guard works:

   ```
   python3 -c "import gcpport; print(gcpport.__name__)"
   ```

   Prints `gcpport` and makes no Google Cloud calls. Importing the module is now completely inert — which is what makes it safe to import from a test, a Cloud Function, or another script.
7. Check the standard-library namespace you have been leaning on:

   ```python
   import csv, io, json
   dir(csv)
   dir(json)
   ```

**Checkpoint** — `python3 demo.py` prints six holdings, reports `Bad row: ['GE', '95', 'N/A']`, and totals `40836.0`; importing `gcpport` prints nothing and makes no Google Cloud calls.

**Stretch** — Swap `sys.argv` for `argparse` and add an `--emulator` flag that wraps the work in `mock_gcs()` and seeds the bucket, so the single script runs either way.

**Self-check**

- Why does `read_portfolio` take `client` as an argument instead of creating it?
- Why does `csv.reader` need no `io.StringIO` here, when the AWS track needed one?

---

[← Lab 10](lab-10-wrapping-the-client-in-a-class.md) · [GCP track index](../README.md) · [Paired Python track lab 11](../../python-track/labs/lab-11-modules-and-script-writing.md) · [Paired AWS track lab 11](../../aws-track/labs/lab-11-a-module-and-a-cli.md) · [Lab 12 →](lab-12-package-it-test-it-and-point-it-at-real-google-cloud.md)
