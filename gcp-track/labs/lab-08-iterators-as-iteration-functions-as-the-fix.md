## Lab 8 — Iterators as iteration, functions as the fix

**Pairs with Python Lab 8 (§1.12–1.13) · 30 minutes**

Goal: Google Cloud listings come back as lazy, single-use iterators that page through results for you. Learn how they behave, then wrap them in functions with sensible defaults.

**Steps**

1. Create `paginate.py` and fill a bucket. Writing 2,500 objects takes about twenty seconds against the emulator:

   ```python
   # paginate.py
   from google.cloud import storage
   from gcpmock import mock_gcs

   BUCKET = 'pydistilled-labs'

   def main():
       with mock_gcs():
           client = storage.Client(project='pydistilled')
           bucket = client.create_bucket(BUCKET)
           for i in range(2500):
               bucket.blob(f'logs/{i:05d}.log').upload_from_string('x')

           listing = client.list_blobs(bucket)
           print(type(listing).__name__)
           print('pages fetched so far:', listing.page_number)

           count = 0
           for blob in listing:
               count += 1
           print('objects:', count)
           print('pages fetched:', listing.page_number)

   if __name__ == '__main__':
       main()
   ```

   `list_blobs` returns an `HTTPIterator` and, before the loop, has fetched nothing: `page_number` is `0`. The `for` loop pulls results as it goes. The count is 2500 — all of them, not a first page. If you did the AWS track, this is the opposite design: boto3 hands you one truncated page and makes you ask for a paginator; Google's iterator follows the page tokens for you.
2. Know what the emulator is hiding. Against real Cloud Storage, one request returns at most 1,000 objects, so the loop above makes three requests and `pages fetched` is `3`. The emulator returns everything in one page, so you see `1`. Your code is the same either way — that is the point of the iterator — but remember the requests are there when you estimate cost or latency.
3. Hit the single-use rule:

   ```python
   listing = client.list_blobs(bucket, prefix='logs/')
   first = [b.name for b in listing]
   again = [b.name for b in listing]      # ValueError: Iterator has already started
   ```

   An `HTTPIterator` can be looped over once. A `list` can be looped over any number of times. When you need the results twice, keep `list(client.list_blobs(...))`, or call `list_blobs` again. This is the same difference as between a file you have read to the end and a list of its lines.
4. Walk the pages yourself, to see the structure underneath:

   ```python
   listing = client.list_blobs(bucket, page_size=500)
   for n, page in enumerate(listing.pages, start=1):
       print(f'page {n}: {page.num_items} objects, more to come: {bool(listing.next_page_token)}')
   ```

   `listing.pages` is itself something you iterate, one page per request, and `page_size` asks the server for smaller pages. Real Cloud Storage would print five pages of 500. The emulator ignores `page_size` and prints one page of 2500; the loop is still the right one to know. `enumerate(..., start=1)` numbers the pages as they arrive — a `for` loop over something that is not a list at all.
5. Now write the functions. Create `gcpport.py` with defaults that make the common call short:

   ```python
   # gcpport.py
   from google.cloud import storage

   def list_names(bucket, prefix='', client=None):
       '''
       Return the name of every object in bucket that starts with prefix.
       '''
       if client is None:
           client = storage.Client()
       return [b.name for b in client.list_blobs(bucket, prefix=prefix)]
   ```

   `prefix=''` is the useful default because an empty prefix matches everything. `client=None` with an `if` inside is the standard way to give an argument a default you cannot write in the signature — you do not want a client created once at import time, which is Lab 1's boundary bug.
6. Call it every way §1.13 allows, inside an emulator block:

   ```python
   from gcpmock import mock_gcs

   with mock_gcs():
       client = storage.Client(project='pydistilled')
       bucket = client.create_bucket('pydistilled-labs')
       for name in ['logs/a.log', 'logs/b.log', 'data/portfolio.csv']:
           bucket.blob(name).upload_from_string('x')

       list_names('pydistilled-labs', client=client)
       list_names('pydistilled-labs', 'logs/', client)
       list_names('pydistilled-labs', prefix='logs/', client=client)
       list_names(prefix='logs/', bucket='pydistilled-labs', client=client)   # Order stops mattering
   ```

   Inside the block, `list_names('pydistilled-labs')` with no client would also work, because the client it creates sees the emulator. Passing `client` in is still the better habit — Lab 11 shows why.
7. Return a tuple of several values, and unpack it:

   ```python
   def bucket_stats(bucket, prefix='', client=None):
       '''
       Return (object_count, total_bytes, largest_name) for a prefix.
       '''
       if client is None:
           client = storage.Client()

       count = 0
       total = 0
       largest = (None, -1)
       for blob in client.list_blobs(bucket, prefix=prefix):
           count += 1
           total += blob.size
           if blob.size > largest[1]:
               largest = (blob.name, blob.size)

       return count, total, largest[0]

   count, total, biggest = bucket_stats('pydistilled-labs', 'logs/', client)
   print(f'{count} objects, {total} bytes, biggest is {biggest}')
   ```

   Returning a tuple and unpacking at the call site — §1.13 applied to something you would actually ship. The function only loops over the iterator once, so the single-use rule never bites.
8. Add a type-annotated signature, remembering it changes nothing at runtime:

   ```python
   def list_names(bucket: str, prefix: str = '', client: storage.Client | None = None) -> list[str]:
       ...
   ```

   `storage.Client | None` reads "a client or `None`". The `|` form in an annotation needs Python 3.10 or newer.

**Checkpoint** — `paginate.py` counts 2500 objects; looping over the same iterator a second time raises `ValueError`; and `bucket_stats` on `paginate.py`'s bucket reports 2500 objects and 2500 bytes.

**Stretch** — Add `max_names=None` to `list_names` and stop the loop with `break` once that many names are collected. Against the real service, think about which page requests the `break` saves.

**Self-check**

- Why does a second loop over the same `list_blobs` result raise an error?
- Why is `client=None` with an `if` inside better than `client=storage.Client()` in the signature?

---

[← Lab 7](lab-07-sets-for-iam-bindings-dicts-for-labels.md) · [GCP track index](../README.md) · [Paired Python track lab 8](../../python-track/labs/lab-08-iteration-and-functions.md) · [Paired AWS track lab 8](../../aws-track/labs/lab-08-paginators-as-iteration-functions-as-the-fix.md) · [Lab 9 →](lab-09-api-exceptions-and-status-codes.md)
