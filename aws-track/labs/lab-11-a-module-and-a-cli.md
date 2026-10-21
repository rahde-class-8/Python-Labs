## Lab 11 — A module and a CLI

**Pairs with Python Lab 11 (§1.17–1.18) · 30 minutes**

Goal: split the AWS code into an importable module and a command-line tool, and solve the problem that mocking creates for a real CLI.

**Steps**

1. Build `awsport.py` as a pure module — definitions only, and note that it takes a client as an argument rather than creating one:

   ```python
   # awsport.py
   #
   # Reads 'NAME,SHARES,PRICE' portfolio data out of S3
   
   import csv
   import io
   from botocore.exceptions import ClientError
   
   def read_portfolio(s3, bucket, key):
       '''
       Read a portfolio CSV from S3 and return a list of (name, shares, price).
       '''
       try:
           body = s3.get_object(Bucket=bucket, Key=key)['Body']
       except ClientError as err:
           code = err.response['Error']['Code']
           if code == 'NoSuchKey':
               raise SystemExit(f'No such object: s3://{bucket}/{key}')
           elif code == 'NoSuchBucket':
               raise SystemExit(f'No such bucket: {bucket}')
           raise
   
       text = body.read().decode('utf-8')
       portfolio = []
       for row in csv.reader(io.StringIO(text)):
           if not row:
               continue
           try:
               portfolio.append((row[0], int(row[1]), float(row[2])))
           except (ValueError, IndexError) as err:
               print('Bad row:', row)
               print('Reason:', err)
       return portfolio
   
   def portfolio_cost(s3, bucket, key):
       '''
       Compute the total shares*price of a portfolio stored in S3.
       '''
       return sum(shares * price
                  for _, shares, price in read_portfolio(s3, bucket, key))
   ```

   Three things worth noticing. `csv.reader` needs something that yields lines, so the S3 text goes through `io.StringIO` — the standard library module from §1.17, fed from S3 instead of a file. The `except (ValueError, IndexError)` tuple catches either. And passing `s3` in rather than building it inside is what makes this module testable at all.
2. Create `pcost_aws.py` that imports it, and try the import forms:

   ```python
   # pcost_aws.py
   import awsport
   
   def report(s3, bucket, key):
       port = awsport.read_portfolio(s3, bucket, key)
       for name, shares, price in port:
           print(f'{name:>10s} {shares:10d} {price:10.2f}')
       print(f'{"TOTAL":>10s} {"":10s} {sum(s * p for _, s, p in port):10.2f}')
   ```

   ```python
   import awsport as ap
   from awsport import read_portfolio
   import awsport
   dir(awsport)
   ```
3. Add a `main()` and the `__name__` guard. This is where mocking gets interesting:

   ```python
   # Append to awsport.py
   
   def main(argv):
       import boto3
       if len(argv) == 3:
           bucket, key = argv[1], argv[2]
       elif len(argv) == 1:
           bucket = input('Bucket: ')
           key = input('Key: ')
       else:
           raise SystemExit(f'Usage: {argv[0]} [ bucket key ]')
   
       s3 = boto3.client('s3')
       for name, shares, price in read_portfolio(s3, bucket, key):
           print(f'{name:>10s} {shares:10d} {price:10.2f}')
   
   if __name__ == '__main__':
       import sys
       main(sys.argv)
   ```
4. Run it and watch it fail:

   ```
   python3 awsport.py pydistilled-labs data/portfolio.csv
   ```

   It cannot work. There is no mock, and no real bucket — so you get a credentials or `NoSuchBucket` error. The module is correct; the problem is that the data does not exist anywhere.
5. Solve it with a seeding script, which is the realistic pattern. Create `demo.py`:

   ```python
   # demo.py
   import boto3
   import sys
   from moto import mock_aws
   import awsport
   
   BUCKET = 'pydistilled-labs'
   KEY = 'data/portfolio.csv'
   
   @mock_aws
   def main():
       s3 = boto3.client('s3', region_name='us-east-1')
       s3.create_bucket(Bucket=BUCKET)
       s3.upload_file('portfolio.csv', BUCKET, KEY)
   
       port = awsport.read_portfolio(s3, BUCKET, KEY)
       for name, shares, price in port:
           print(f'{name:>10s} {shares:10d} {price:10.2f}')
       print('total:', awsport.portfolio_cost(s3, BUCKET, KEY))
   
   if __name__ == '__main__':
       main()
   ```

   Run `python3 demo.py`. The bad `GE,95,N/A` row is reported and skipped, exactly as on the Python track, and the total comes out. `awsport.py` itself knows nothing about moto — that is the point of taking `s3` as an argument.
6. Confirm the import guard works:

   ```
   python3 -c "import awsport; print(awsport.__name__)"
   ```

   Prints `awsport` and runs no AWS calls. Importing the module is now completely inert — which is what makes it safe to import from a test, a Lambda handler, or another script.
7. Check the standard-library namespace you have been leaning on:

   ```python
   import csv, io, json
   dir(csv)
   dir(io)
   ```

**Checkpoint** — `python3 demo.py` prints six holdings, reports `Bad row: ['GE', '95', 'N/A']`, and totals `40836.0`; importing `awsport` prints nothing and makes no AWS calls.

**Stretch** — Add a `--mock` flag to `main()` that wraps the work in `mock_aws()` and seeds the bucket, so the single script runs either way.

**Self-check**

- Why does `read_portfolio` take `s3` as an argument instead of creating the client itself?
- Why does `csv.reader` need `io.StringIO` here, when it took an open file on the Python track?

---

[← Lab 10](lab-10-wrapping-boto3-in-a-class.md) · [AWS track index](../README.md) · [Paired Python track lab 11](../../python-track/labs/lab-11-modules-and-script-writing.md) · [Lab 12 →](lab-12-package-it-test-it-and-point-it-at-real-aws.md)
