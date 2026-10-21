## Lab 5 — Local files to Cloud Storage and back

**Pairs with Python Lab 5 (§1.7) · 30 minutes**

Goal: the ways to move data in and out of Cloud Storage, the `bytes`-versus-`str` boundary, and the file-like interface that makes a blob behave almost like `open()`.

**Steps**

1. Create `gcsio.py` with a bucket and the portfolio file uploaded three ways:

   ```python
   # gcsio.py
   from google.cloud import storage
   from gcpmock import mock_gcs

   BUCKET = 'pydistilled-labs'

   def main():
       with mock_gcs():
           client = storage.Client(project='pydistilled')
           bucket = client.create_bucket(BUCKET)

           # Way 1: give it a path, it handles opening
           bucket.blob('uploaded/portfolio.csv').upload_from_filename('portfolio.csv')

           # Way 2: give it an open file — binary mode
           with open('portfolio.csv', 'rb') as f:
               bucket.blob('direct/portfolio.csv').upload_from_file(f)

           # Way 3: give it a string or bytes
           bucket.blob('inline/one-row.csv').upload_from_string('AA,100,32.20\n')

           for blob in client.list_blobs(bucket):
               print(blob.name, blob.size)

   if __name__ == '__main__':
       main()
   ```

   Note `'rb'` — binary mode. Cloud Storage stores bytes. `upload_from_string` accepts a `str` and encodes it as UTF-8 for you, which makes the next step's asymmetry easy to miss.
2. Read it back, as bytes and as text:

   ```python
   blob = bucket.blob('uploaded/portfolio.csv')

   raw = blob.download_as_bytes()
   type(raw)                  # bytes
   raw[:20]

   text = blob.download_as_text()
   type(text)                 # str
   print(text)
   ```

   Two methods, two types. `download_as_text` decodes for you; `download_as_bytes` does not. Every call downloads the whole object again — there is no stream to exhaust, so you can call either one as often as you like.
3. Open a blob like a file. This is the step with no equivalent in boto3:

   ```python
   with blob.open('r') as f:
       for line in f:
           print(line, end='')
   ```

   `blob.open('r')` returns a file-like object, and the loop is character-for-character the one from Python Lab 5 step 2, including `end=''` because each line keeps its `\n`. Under the hood it downloads in chunks as you read, so a 10 GB object does not need 10 GB of memory.
4. Parse as you iterate, so the rest of your code sees rows:

   ```python
   with blob.open('r') as f:
       for line in f:
           row = line.strip().split(',')
           print(row)
   ```

   That is `line.split(',')` from Python Lab 6 with nothing changed but the `open`.
5. Download to a local file and verify the round trip:

   ```python
   blob.download_to_filename('roundtrip.csv')

   original = open('portfolio.csv', 'rb').read()
   returned = open('roundtrip.csv', 'rb').read()
   print('identical:', original == returned)
   ```
6. Write *generated* content straight to Cloud Storage, the equivalent of Python Lab 5's `out.txt`:

   ```python
   principal = 1000
   rate = 0.05

   with bucket.blob('reports/interest.txt').open('w') as out:
       for year in range(1, 6):
           principal = principal * (1 + rate)
           print(f'{year:>3d} {principal:0.2f}', file=out)

   print(bucket.blob('reports/interest.txt').download_as_text())
   ```

   `print(..., file=out)` is exactly the `file=` argument from Python Lab 5, and `open('w')` is the `'wt'` mode. Only the destination changed. The object is created when the `with` block closes the file, not line by line.
7. Build content in memory first with `io.StringIO`, for when you need the whole text before deciding where it goes:

   ```python
   import io

   buffer = io.StringIO()
   for name in ['AA', 'IBM', 'CAT']:
       print(name, file=buffer)

   bucket.blob('reports/names.txt').upload_from_string(buffer.getvalue())
   ```

   A `StringIO` behaves like an open file but keeps everything in memory. `getvalue()` hands back the whole string.
8. Confirm Cloud Storage has no append. Write the same name twice:

   ```python
   target = bucket.blob('reports/interest.txt')
   target.upload_from_string('replaced\n')
   print(target.download_as_text())
   ```

   The old content is gone, and `blob.open('a')` raises `NotImplementedError` because there is no append mode. Every write replaces the whole object; Cloud Storage objects are immutable, and "changing" one means writing a new **generation** of it — the `generation` number from Lab 2.

**Checkpoint** — `gcsio.py` lists three objects, two of them 93 bytes; the round-trip comparison prints `identical: True`; and the report written through `open('w')` reads back as five formatted lines.

**Stretch** — Cloud Storage can *compose* up to 32 objects into one. Write `gcs_append(bucket, name, text)` that uploads `text` to a temporary object, then calls `bucket.blob(name).compose([bucket.blob(name), temp])` and deletes the temporary object. Then write down why this is still unsafe with two writers.

**Self-check**

- What is the difference between `download_as_bytes` and `download_as_text`?
- Why does `blob.open('a')` not exist?

---

[← Lab 4](lab-04-resource-names-urls-and-gs-string-surgery.md) · [GCP track index](../README.md) · [Paired Python track lab 5](../../python-track/labs/lab-05-file-input-and-output.md) · [Paired AWS track lab 5](../../aws-track/labs/lab-05-local-files-to-s3-and-back.md) · [Lab 6 →](lab-06-lists-and-tuples-from-cloud-listings.md)
