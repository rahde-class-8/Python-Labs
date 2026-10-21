## Lab 10 — Wrapping the client in a class

**Pairs with Python Lab 10 (§1.16) · 30 minutes**

Goal: build the Google Cloud version of the `Stack`/`Calculator` lesson — a class that *holds* a bucket, not one that *is* one.

**Steps**

1. Explore a `Bucket` with `dir()`, as you did with a list:

   ```python
   from google.cloud import storage
   [name for name in dir(storage.Bucket) if not name.startswith('_')][:20]
   len([n for n in dir(storage.Bucket) if not n.startswith('_')])
   storage.Bucket.__mro__
   ```

   About eighty public names, and `Bucket` is an ordinary class you could subclass. If you did the AWS track, that is a difference: a boto3 client class does not exist until runtime. Here inheritance is possible, which makes the question in step 4 a real design decision.
2. Create `portfolio_bucket.py` with a class that holds a client and a bucket:

   ```python
   # portfolio_bucket.py
   from google.cloud import storage

   class PortfolioBucket:
       '''
       A single Cloud Storage bucket holding portfolio CSV files.
       '''

       def __init__(self, name, client=None):
           self._client = client or storage.Client()
           self._bucket = self._client.bucket(name)

       def create(self):
           self._bucket = self._client.create_bucket(self._bucket.name)

       def put(self, name, text):
           self._bucket.blob(name).upload_from_string(text)

       def get(self, name):
           blob = self._bucket.get_blob(name)
           if blob is None:
               return None
           return blob.download_as_text()

       def names(self):
           return [b.name for b in self._client.list_blobs(self._bucket)]

       def __len__(self):
           return len(self.names())

       def __contains__(self, name):
           return self._bucket.blob(name).exists()

       def __repr__(self):
           return f'<{type(self).__name__} {self._bucket.name!r}, {len(self)} objects>'
   ```

   `_client` and `_bucket` use the single-underscore convention from §1.16 — internal by agreement, not enforcement. `__contains__` asks the server about one object instead of listing them all, which stays fast on a bucket with a million objects.
3. Use it inside the emulator:

   ```python
   from gcpmock import mock_gcs

   def main():
       with mock_gcs():
           b = PortfolioBucket('pydistilled-labs', storage.Client(project='pydistilled'))
           b.create()
           b.put('data/portfolio.csv', 'AA,100,32.20\nIBM,50,91.10\n')
           b.put('data/notes.txt', 'hello')

           print(len(b))                          # __len__
           print('data/notes.txt' in b)           # __contains__
           print('missing.csv' in b)
           print(b)                               # __repr__
           print(b.get('data/portfolio.csv'))
           print(b.get('missing.csv'))            # None, not an exception

   main()
   ```

   `len()`, `in` and a readable `repr` all work on your own object through exactly the three special methods from §1.16. `get()` returning `None` for a missing object is a design decision you made, and it means callers never see a `NotFound`.
4. Now try the inheritance version and see what it costs:

   ```python
   class BadBucket(storage.Bucket):
       def holdings(self):
           ...

   with mock_gcs():
       client = storage.Client(project='pydistilled')
       b = BadBucket(client, 'pydistilled-labs')
       [n for n in dir(b) if n.startswith('delete')]
   ```

   It works, and that is the problem. `BadBucket` *is* a bucket, so every caller who gets one also gets `delete`, `delete_blobs`, `make_public`, `set_iam_policy` and dozens of other methods you never meant to offer. `PortfolioBucket` exposes four methods and three special methods. Composition decides what the public surface is; inheritance hands over all of someone else's.
5. Subclass *your own* class instead, adding behaviour — the `MyStack` move:

   ```python
   class DryRunBucket(PortfolioBucket):
       def put(self, name, text):
           print(f'DRY RUN: would write {len(text)} bytes to {name}')

   with mock_gcs():
       b = DryRunBucket('pydistilled-labs', storage.Client(project='pydistilled'))
       b.create()
       b.put('data/portfolio.csv', 'AA,100,32.20\n')
       print(len(b))            # 0 — nothing was actually written
   ```

   Overriding `put()` to do nothing is the cheapest dry-run flag there is, and `create()`, `get()`, `names()` and `__repr__` are inherited untouched.
6. Override while still calling the original, with `super()` — the `NumericStack` move:

   ```python
   class AuditedBucket(PortfolioBucket):
       def __init__(self, name, client=None):
           super().__init__(name, client)
           self._writes = []

       def put(self, name, text):
           super().put(name, text)
           self._writes.append(name)

       def audit(self):
           return list(self._writes)

   with mock_gcs():
       b = AuditedBucket('pydistilled-labs', storage.Client(project='pydistilled'))
       b.create()
       b.put('a.csv', 'x')
       b.put('b.csv', 'y')
       print(b.audit())         # ['a.csv', 'b.csv']
       print(len(b))            # 2 — the writes really happened
   ```

   Note that `__init__` also calls `super().__init__(...)` before adding its own state. Forget that and `self._client` never gets created.
7. Add a `Portfolio` class that *uses* a `PortfolioBucket` — composition one level up, mirroring `Calculator`:

   ```python
   class Portfolio:
       def __init__(self, store, name):
           self._store = store
           self._name = name

       def holdings(self):
           text = self._store.get(self._name)
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
           return f'<Portfolio {self._name!r}, {len(self.holdings())} holdings>'
   ```

   A `Portfolio` is not a bucket, so it does not inherit from one — it holds one. Storage could become Firestore or a local file by swapping what you pass in, and `Portfolio` would not change.

**Checkpoint** — `len(b)` is 2, `'missing.csv' in b` is `False`, `b.get('missing.csv')` is `None`, and `Portfolio(b, 'data/portfolio.csv').total()` gives `7775.0`.

**Stretch** — Give `PortfolioBucket` a `__iter__` that yields names straight from `list_blobs`, so `for name in b:` works without building a list. Then work out what happens if a caller loops over `b` twice.

**Self-check**

- `storage.Bucket` can be subclassed. Why not do it anyway?
- What does `Portfolio` gain by holding a bucket instead of inheriting one?

---

[← Lab 9](lab-09-api-exceptions-and-status-codes.md) · [GCP track index](../README.md) · [Paired Python track lab 10](../../python-track/labs/lab-10-objects-and-classes.md) · [Paired AWS track lab 10](../../aws-track/labs/lab-10-wrapping-boto3-in-a-class.md) · [Lab 11 →](lab-11-a-module-and-a-cli.md)
