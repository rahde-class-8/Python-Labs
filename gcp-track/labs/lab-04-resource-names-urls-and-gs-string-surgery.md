## Lab 4 — Resource names, URLs and gs:// string surgery

**Pairs with Python Lab 4 (§1.6) · 25 minutes**

Goal: Google Cloud identifies everything with structured strings — `gs://` URIs, resource names and full URLs — and splitting, slicing and f-strings are the whole toolkit.

**Steps**

1. Take a `gs://` URI apart. This is how every Google Cloud tool refers to an object:

   ```python
   uri = 'gs://pydistilled-labs/data/2026/portfolio.csv'

   uri.startswith('gs://')
   rest = uri.removeprefix('gs://')     # Python 3.9+
   rest
   bucket, _, name = rest.partition('/')
   bucket, name
   ```

   `partition('/')` splits at the *first* slash only and always returns three parts. That is exactly right here: the bucket name cannot contain `/`, but the object name can contain as many as it likes.
2. See why `split` alone is the wrong tool:

   ```python
   rest.split('/')            # Four pieces — the object name got chopped up
   rest.split('/', 1)         # Two pieces — correct
   'gs://bucket-only'.removeprefix('gs://').partition('/')
   ```

   `split('/', 1)` stops after one split. `partition` gives the same answer and returns an empty object name, rather than a shorter list, when there is no slash. Code that unpacks the result keeps working either way.
3. Take a Compute Engine URL apart. Load the fixture and look at one field:

   ```python
   import json

   with open('instances.json') as f:
       inst = json.load(f)[0]

   inst['machineType']
   inst['machineType'].rsplit('/', 1)[-1]       # 'e2-micro'
   inst['zone'].rsplit('/', 1)[-1]              # 'us-central1-a'
   ```

   The API returns full URLs where you might expect short names. `rsplit('/', 1)[-1]` — split once from the right and take the last piece — is the one-liner for "give me the short name".
4. Name the pieces of a resource path by slicing a split list:

   ```python
   url = inst['selfLink']
   path = url.split('/compute/v1/', 1)[1]
   path
   parts = path.split('/')
   parts
   dict(zip(parts[::2], parts[1::2]))
   ```

   The path is `projects/pydistilled/zones/us-central1-a/instances/web-1`: collection, id, collection, id. `parts[::2]` takes every other item starting at 0 and `parts[1::2]` every other item starting at 1, and `zip` pairs them into `{'projects': 'pydistilled', 'zones': 'us-central1-a', 'instances': 'web-1'}`. This alternating shape is how Google names almost every resource.
5. Derive a region from a zone, and check the result:

   ```python
   zone = 'us-central1-a'
   region = zone.rsplit('-', 1)[0]        # 'us-central1'
   zone[:-2]                              # Same answer, by slicing
   zone.rsplit('-', 1)[1]                 # 'a' — the zone letter
   ```

   A zone is a region plus a one-letter suffix. Slicing works because the suffix is always two characters; `rsplit` works because it says *why* you are cutting there.
6. Build names and URIs with f-strings instead of concatenation:

   ```python
   project = 'pydistilled'
   zone = 'us-central1-a'
   bucket = 'pydistilled-labs'

   object_uri   = f'gs://{bucket}/data/portfolio.csv'
   instance     = f'projects/{project}/zones/{zone}/instances/web-1'
   machine_type = f'zones/{zone}/machineTypes/e2-micro'
   sa_email     = f'lab-runner@{project}.iam.gserviceaccount.com'
   iam_member   = f'serviceAccount:{sa_email}'

   for s in [object_uri, instance, machine_type, sa_email, iam_member]:
       print(s)
   ```

   Note the last two. A service account is identified by an email address that has the project ID inside it, and IAM refers to it with a `type:` prefix. `user:`, `group:` and `serviceAccount:` are different kinds of member, and Lab 7 works with them.
7. Generate a dated object prefix, combining `datetime` formatting with f-strings:

   ```python
   from datetime import datetime, timezone

   now = datetime.now(timezone.utc)
   prefix = f'data/{now:%Y/%m/%d}'
   print(f'gs://{bucket}/{prefix}/portfolio.csv')
   ```

   The `{now:%Y/%m/%d}` format spec inside an f-string works on `datetime` objects — the same mechanism as `{price:0.2f}` on a float.
8. Write `gsinfo.py` that parses `gs://` URIs into a labelled report:

   ```python
   # gsinfo.py

   def parse_gs_uri(uri):
       bucket, _, name = uri.removeprefix('gs://').partition('/')
       folder, _, filename = name.rpartition('/')
       return {
           'bucket': bucket,
           'folder': folder or '(top level)',
           'file': filename or '(none)',
           'extension': filename.rpartition('.')[2] if '.' in filename else '(none)',
       }

   if __name__ == '__main__':
       for uri in ['gs://pydistilled-labs/data/2026/portfolio.csv',
                   'gs://pydistilled-labs/README',
                   'gs://pydistilled-labs']:
           print(uri)
           for field, value in parse_gs_uri(uri).items():
               print(f'  {field:<10} {value}')
   ```

   `folder or '(top level)'` uses the truthiness of the empty string from Lab 3 — an empty piece falls through to the default. `rpartition` is `partition` from the right, so it splits at the *last* slash.

**Checkpoint** — `gsinfo.py` reports `data/2026` and `csv` for the first URI, `(top level)` for the second, and `(none)` for both the file and the extension of the bare bucket.

**Stretch** — Make `parse_gs_uri` raise `ValueError('not a gs:// URI')` when the string does not start with `gs://`, then test it.

**Self-check**

- Why is `partition('/')` a better fit than `split('/')` for a `gs://` URI?
- What does `rsplit('/', 1)[-1]` do to a `machineType` URL, and why from the right?

---

[← Lab 3](lab-03-conditionals-over-cloud-state.md) · [GCP track index](../README.md) · [Paired Python track lab 4](../../python-track/labs/lab-04-text-strings-and-formatting.md) · [Paired AWS track lab 4](../../aws-track/labs/lab-04-arn-and-s3-key-string-surgery.md) · [Lab 5 →](lab-05-local-files-to-cloud-storage-and-back.md)
