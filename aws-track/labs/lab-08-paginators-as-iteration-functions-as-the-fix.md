## Lab 8 — Paginators as iteration, functions as the fix

**Pairs with Python Lab 8 (§1.12–1.13) · 30 minutes**

Goal: AWS truncates every list response. Learn the iteration pattern that hides that, then wrap it in functions with sensible defaults.

**Steps**

1. Create `paginate.py` and manufacture a truncated response:

   ```python
   # paginate.py
   import boto3
   from moto import mock_aws
   
   BUCKET = 'pydistilled-labs'
   
   @mock_aws
   def main():
       s3 = boto3.client('s3', region_name='us-east-1')
       s3.create_bucket(Bucket=BUCKET)
       for i in range(2500):
           s3.put_object(Bucket=BUCKET, Key=f'logs/{i:05d}.log', Body=b'x')
   
       response = s3.list_objects_v2(Bucket=BUCKET)
       print('returned:', len(response['Contents']))
       print('truncated:', response['IsTruncated'])
   
   if __name__ == '__main__':
       main()
   ```

   You get 1000 objects, not 2500, and `IsTruncated` is `True`. S3 caps a single response at 1000 keys. Code that ignores this silently processes 40% of your data and reports success — the worst kind of bug.
2. Page through it by hand, to see what is actually happening:

   ```python
   keys = []
   token = None
   while True:
       kwargs = {'Bucket': BUCKET}
       if token:
           kwargs['ContinuationToken'] = token
       response = s3.list_objects_v2(**kwargs)
       keys.extend(o['Key'] for o in response.get('Contents', []))
       if not response['IsTruncated']:
           break
       token = response['NextContinuationToken']
   
   print(len(keys))
   ```

   Note the `while True` with `break`, and the truthiness test `if token`. All of this is §1.5 and §1.12 material. Now never write it again.
3. Use a paginator, which is the same loop done for you:

   ```python
   paginator = s3.get_paginator('list_objects_v2')
   
   keys = []
   for page in paginator.paginate(Bucket=BUCKET):
       keys.extend(o['Key'] for o in page.get('Contents', []))
   
   print(len(keys))
   ```

   `paginator.paginate(...)` returns an iterable you can use in a `for` loop, exactly like a list or a file. It fetches each page only as the loop asks for it — the same lazy behaviour as `range()` in §1.12.
4. Prove it is lazy, and control the page size:

   ```python
   pages = paginator.paginate(Bucket=BUCKET, PaginationConfig={'PageSize': 500})
   type(pages)
   
   for n, page in enumerate(pages, start=1):
       print(f'page {n}: {len(page["Contents"])} keys')
   ```

   `enumerate(pages, start=1)` numbers the pages as they arrive — a `for` loop over something that is not a list at all.
5. Now write the functions. Create `awsport.py` with a default argument for region:

   ```python
   # awsport.py
   import boto3
   
   def list_keys(bucket, prefix='', region='us-east-1'):
       '''
       Return every key in bucket, following pagination.
       '''
       s3 = boto3.client('s3', region_name=region)
       paginator = s3.get_paginator('list_objects_v2')
       keys = []
       for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
           keys.extend(o['Key'] for o in page.get('Contents', []))
       return keys
   ```

   `prefix=''` is the useful default because an empty prefix matches everything — the parameter is optional without needing a separate code path.
6. Call it every way §1.13 allows:

   ```python
   list_keys(BUCKET)
   list_keys(BUCKET, 'logs/')
   list_keys(BUCKET, prefix='logs/')
   list_keys(bucket=BUCKET, prefix='logs/', region='us-east-1')
   list_keys(prefix='logs/', bucket=BUCKET)        # Order stops mattering
   ```
7. Return a tuple of several values, and unpack it:

   ```python
   def bucket_stats(bucket, prefix='', region='us-east-1'):
       '''
       Return (object_count, total_bytes, largest_key) for a prefix.
       '''
       s3 = boto3.client('s3', region_name=region)
       paginator = s3.get_paginator('list_objects_v2')
   
       count = 0
       total = 0
       largest = (None, -1)
       for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
           for obj in page.get('Contents', []):
               count += 1
               total += obj['Size']
               if obj['Size'] > largest[1]:
                   largest = (obj['Key'], obj['Size'])
   
       return count, total, largest[0]
   
   count, total, biggest = bucket_stats(BUCKET, 'logs/')
   print(f'{count} objects, {total} bytes, biggest is {biggest}')
   ```

   Returning a tuple and unpacking at the call site — §1.13 applied to something you would actually ship.
8. Add a type-annotated signature, remembering it changes nothing at runtime:

   ```python
   def list_keys(bucket: str, prefix: str = '', region: str = 'us-east-1') -> list:
       ...
   ```

**Checkpoint** — the unpaginated call returns 1000 with `IsTruncated: True`; both the manual loop and the paginator return 2500; `bucket_stats` reports 2500 objects.

**Stretch** — Add `max_keys=None` to `list_keys` and stop early once that many keys are collected. Think about which pages you avoided fetching.

**Self-check**

- What does `IsTruncated: True` mean, and what goes wrong if you ignore it?
- Why is `prefix=''` a better default than `prefix=None`?

---

[← Lab 7](lab-07-sets-for-iam-policy-diffing-dicts-for-tags.md) · [AWS track index](../README.md) · [Paired Python track lab 8](../../python-track/labs/lab-08-iteration-and-functions.md) · [Paired GCP track lab 8](../../gcp-track/labs/lab-08-iterators-as-iteration-functions-as-the-fix.md) · [Lab 9 →](lab-09-clienterror-and-error-codes.md)
