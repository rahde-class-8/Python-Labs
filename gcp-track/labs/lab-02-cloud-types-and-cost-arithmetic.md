## Lab 2 — Cloud types and cost arithmetic

**Pairs with Python Lab 2 (§1.3–1.4) · 30 minutes**

Goal: find out what types Google Cloud actually hands you, which is not always what you sent, and do the division-operator work on billing math.

**Steps**

1. Create `types_tour.py` and look at the types on a stored object:

   ```python
   # types_tour.py
   from google.cloud import storage
   from gcpmock import mock_gcs

   def main():
       with mock_gcs():
           client = storage.Client(project='pydistilled')
           bucket = client.create_bucket('pydistilled-labs')
           bucket.blob('portfolio.csv').upload_from_filename('portfolio.csv')

           blob = bucket.get_blob('portfolio.csv')
           for attr in ['name', 'size', 'updated', 'md5_hash', 'generation', 'content_type']:
               value = getattr(blob, attr)
               print(f'{attr:<14} {type(value).__name__:<10} {value}')

   if __name__ == '__main__':
       main()
   ```

   An object in Cloud Storage is a **blob** in this library. `size` is an `int`, `updated` is a `datetime`, and `generation` is a large `int` that changes every time the object is overwritten. `md5_hash` is a `str` holding a base64-encoded hash, not the hex digest you might expect. `getattr(blob, attr)` fetches an attribute by name, which is how one loop prints six of them.
2. Now meet custom metadata, which does something different. Add to the same block:

   ```python
   blob = bucket.blob('holdings/AA')
   blob.metadata = {'shares': 100, 'price': 32.20}
   blob.upload_from_string('')

   meta = bucket.get_blob('holdings/AA').metadata
   print(meta)
   print(type(meta['shares']), type(meta['price']))
   ```

   You stored an `int` and a `float`. Both come back as `str`: `{'shares': '100', 'price': '32.2'}`. Custom metadata is a dictionary of strings, always, and the library converts your numbers on the way in without a word.
3. Hit the trap this creates:

   ```python
   shares = meta['shares']
   shares * 2              # '100100' — string repetition, not arithmetic
   shares + 1              # TypeError: can only concatenate str (not "int") to str
   int(shares) * 2         # 200 — convert first
   ```

   The first line is the dangerous one. It does not crash; it gives a wrong answer that looks plausible. This is Python Lab 4's `'37' + '42'` lesson, arriving from a cloud API.
4. Compute a portfolio value from metadata, converting explicitly and keeping money in `Decimal`:

   ```python
   from decimal import Decimal

   for sym, shares, price in [('AA', '100', '32.20'), ('IBM', '50', '91.10')]:
       blob = bucket.blob(f'holdings/{sym}')
       blob.metadata = {'shares': shares, 'price': price}
       blob.upload_from_string('')          # Replaces holdings/AA from step 2

   total = Decimal('0')
   for b in client.list_blobs(bucket, prefix='holdings/'):
       total += int(b.metadata['shares']) * Decimal(b.metadata['price'])
   print(total, type(total).__name__)
   ```

   You get `7775.00` as a `Decimal`: exact, with trailing zeros preserved. This time you stored the numbers as strings yourself (`'32.20'`, not `32.20`), because a `float` would have arrived as `'32.2'` and lost the trailing zero before `Decimal` ever saw it.
5. Meet a second string-for-number surprise, this time in Compute Engine data:

   ```python
   import json

   with open('instances.json') as f:
       instances = json.load(f)

   first = instances[0]
   first['id'], type(first['id'])
   ```

   The instance ID is a string of digits. The underlying value is a 64-bit unsigned integer, and JSON numbers are not safe above 2⁵³ in many languages, so Google's APIs send 64-bit integers as strings. Compare it with an ID as a number only after `int(first['id'])`.
6. Do storage cost arithmetic, exercising the operators from §1.4. Assume a rate of `0.020` per GB-month (substitute the real current rate if you want — the arithmetic is the lesson):

   ```python
   size_bytes = 1536 * 1024 * 1024

   gib = size_bytes / (1024 ** 3)      # 1.5         — binary gigabytes
   gb  = size_bytes / (1000 ** 3)      # 1.610612736 — decimal gigabytes
   print(gib, gb)

   rate = 0.020
   print(round(gib * rate, 4))         # 0.03
   ```

   The two answers differ by about 7%. Google Cloud's pricing pages define a GB as 2³⁰ bytes, which is a GiB, so for Google the first number is the one that gets billed. Check the definition on the pricing page of whatever service you are estimating; it is the kind of detail that differs between providers.
7. Use truncating division and modulo on per-second billing. Compute Engine bills by the second, with a one-minute minimum:

   ```python
   seconds = 5000
   hours, rest = divmod(seconds, 3600)
   minutes, secs = divmod(rest, 60)
   print(f'{hours}h {minutes}m {secs}s')    # 1h 23m 20s

   billed = max(seconds, 60)                 # The one-minute minimum
   billed = max(45, 60)                      # 60 — a 45-second VM costs a minute
   -5000 // 3600                             # -2, not -1 — truncates toward negative infinity
   ```
8. Watch float money go wrong, and fix it:

   ```python
   0.1 + 0.2 == 0.3                                    # False
   Decimal('0.1') + Decimal('0.2') == Decimal('0.3')   # True
   Decimal(0.1)                                        # The float's real value — look at it
   ```

   `Decimal(0.1)` from a float keeps the float's error; `Decimal('0.1')` from a string does not. Always build `Decimal` from strings, which step 4 did.

**Checkpoint** — `types_tour.py` prints `size` as `int` and `updated` as `datetime`, both metadata values come back as `str`, and the portfolio total is `7775.00`.

**Stretch** — Write `estimate_cost(size_bytes, rate=0.020, use_gib=True)` and show the two answers side by side for a 500 GB bucket.

**Self-check**

- Why does `meta['shares'] * 2` give a wrong answer instead of an error?
- Why do Google's APIs send 64-bit IDs as strings?

---

[← Lab 1](lab-01-the-client-library-and-your-first-emulated-script.md) · [GCP track index](../README.md) · [Paired Python track lab 2](../../python-track/labs/lab-02-primitives-variables-and-arithmetic.md) · [Paired AWS track lab 2](../../aws-track/labs/lab-02-aws-types-and-cost-arithmetic.md) · [Lab 3 →](lab-03-conditionals-over-cloud-state.md)
