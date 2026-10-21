## Lab 10 — Wrapping boto3 in a class

**Pairs with Python Lab 10 (§1.16) · 30 minutes**

Goal: build the AWS version of the `Stack`/`Calculator` lesson. A class that *holds* a boto3 client, not one that *is* one — and this time the composition argument is not academic.

**Steps**

1. Explore a client with `dir()`, as you did with a list:

   ```python
   import boto3
   s3 = boto3.client('s3', region_name='us-east-1')
   [name for name in dir(s3) if not name.startswith('_')][:20]
   len([n for n in dir(s3) if not n.startswith('_')])
   ```

   Roughly a hundred methods, generated at runtime. There is no class here you could sensibly inherit from — which settles the inheritance question before you ask it.
2. Create `portfolio_bucket.py` with a class that holds a client:

   ```python
   # portfolio_bucket.py
   import boto3
   from botocore.exceptions import ClientError
   
   class PortfolioBucket:
       '''
       A single S3 bucket holding portfolio CSV files.
       '''
   
       def __init__(self, bucket, region='us-east-1'):
           self._bucket = bucket
           self._s3 = boto3.client('s3', region_name=region)
   
       def create(self):
           self._s3.create_bucket(Bucket=self._bucket)
   
       def put(self, key, text):
           self._s3.put_object(Bucket=self._bucket, Key=key, Body=text)
   
       def get(self, key):
           try:
               body = self._s3.get_object(Bucket=self._bucket, Key=key)['Body']
               return body.read().decode('utf-8')
           except ClientError as err:
               if err.response['Error']['Code'] == 'NoSuchKey':
                   return None
               raise
   
       def keys(self):
           paginator = self._s3.get_paginator('list_objects_v2')
           return [o['Key']
                   for page in paginator.paginate(Bucket=self._bucket)
                   for o in page.get('Contents', [])]
   
       def __len__(self):
           return len(self.keys())
   
       def __contains__(self, key):
           return key in self.keys()
   
       def __repr__(self):
           return f'<{type(self).__name__} {self._bucket!r}, {len(self)} objects>'
   ```

   `_bucket` and `_s3` use the single-underscore convention from §1.16 — internal by agreement, not enforcement.
3. Use it inside a mock:

   ```python
   from moto import mock_aws
   
   @mock_aws
   def main():
       b = PortfolioBucket('pydistilled-labs')
       b.create()
       b.put('data/portfolio.csv', 'AA,100,32.20\nIBM,50,91.10\n')
       b.put('data/notes.txt', 'hello')
   
       print(len(b))                         # __len__
       print('data/notes.txt' in b)           # __contains__
       print('missing.csv' in b)
       print(b)                               # __repr__
       print(b.get('data/portfolio.csv'))
       print(b.get('missing.csv'))            # None, not an exception
   
   main()
   ```

   `len()`, `in` and a readable `repr` all work on your own object, through exactly the three special methods from §1.16. Note that `get()` returning `None` for a missing key is a design decision you made — the Lab 9 error handling is now hidden inside the class, where callers do not have to repeat it.
4. Now try the inheritance version and watch it fall apart:

   ```python
   s3 = boto3.client('s3', region_name='us-east-1')
   type(s3).__name__           # 'S3'
   type(s3).__mro__            # Where would you even hook in?
   
   class BadBucket(type(s3)):  # Technically possible
       pass
   ```

   The class does not exist until a client is built, so you cannot write `class BadBucket(S3)` in a source file at all. Inheriting from a boto3 client is not a judgement call — the library's design forecloses it. Composition is the only option, which is why every AWS wrapper you will ever read looks like step 2.
5. Subclass *your own* class instead, adding behaviour — the `MyStack` move:

   ```python
   class DryRunBucket(PortfolioBucket):
       def put(self, key, text):
           print(f'DRY RUN: would write {len(text)} bytes to {key}')
   
   @mock_aws
   def main():
       b = DryRunBucket('pydistilled-labs')
       b.create()
       b.put('data/portfolio.csv', 'AA,100,32.20\n')
       print(len(b))            # 0 — nothing was actually written
   
   main()
   ```

   Overriding `put()` to do nothing is the cheapest dry-run flag there is, and `create()`, `get()`, `keys()` and `__repr__` are inherited untouched.
6. Override while still calling the original, with `super()` — the `NumericStack` move:

   ```python
   class AuditedBucket(PortfolioBucket):
       def __init__(self, bucket, region='us-east-1'):
           super().__init__(bucket, region)
           self._writes = []
   
       def put(self, key, text):
           super().put(key, text)
           self._writes.append(key)
   
       def audit(self):
           return list(self._writes)
   
   @mock_aws
   def main():
       b = AuditedBucket('pydistilled-labs')
       b.create()
       b.put('a.csv', 'x')
       b.put('b.csv', 'y')
       print(b.audit())         # ['a.csv', 'b.csv']
       print(len(b))            # 2 — the writes really happened
   
   main()
   ```

   Note that `__init__` also calls `super().__init__(...)` before adding its own state. Forget that and `self._s3` never gets created.
7. Add a `Portfolio` class that *uses* a `PortfolioBucket` — composition one level up, mirroring `Calculator`:

   ```python
   class Portfolio:
       def __init__(self, bucket, key):
           self._store = bucket
           self._key = key
   
       def holdings(self):
           text = self._store.get(self._key)
           if text is None:
               return []
           rows = []
           for line in text.strip().split('\n'):
               name, shares, price = line.split(',')
               rows.append((name, int(shares), float(price)))
           return rows
   
       def total(self):
           return sum(s * p for _, s, p in self.holdings())
   
       def __repr__(self):
           return f'<Portfolio {self._key!r}, {len(self.holdings())} holdings>'
   ```

   A `Portfolio` is not a bucket, so it does not inherit from one — it holds one. Storage could become DynamoDB or a local file by swapping what you pass in, and `Portfolio` would not change.

**Checkpoint** — `len(b)` is 2, `'missing.csv' in b` is `False`, `b.get('missing.csv')` is `None`, and `Portfolio(...).total()` on the two-line CSV gives `7775.0`.

**Stretch** — Give `PortfolioBucket` a `__iter__` that yields keys, so `for key in b:` works. Compare it with `b.keys()` for a bucket with 10,000 objects.

**Self-check**

- Why can you not write `class MyBucket(S3Client)` in a source file?
- What does `Portfolio` gain by holding a bucket instead of inheriting one?

---

[← Lab 9](lab-09-clienterror-and-error-codes.md) · [AWS track index](../README.md) · [Paired Python track lab 10](../../python-track/labs/lab-10-objects-and-classes.md) · [Lab 11 →](lab-11-a-module-and-a-cli.md)
