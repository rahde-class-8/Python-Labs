## Lab 4 — ARN and S3 key string surgery

**Pairs with Python Lab 4 (§1.6) · 25 minutes**

Goal: ARNs and S3 keys are structured strings, and splitting, slicing and f-strings are the whole toolkit. This is the lab where §1.6 pays off immediately.

**Steps**

1. Take an ARN apart. An ARN has six colon-separated fields, and some are deliberately empty:

   ```python
   arn = 'arn:aws:s3:::pydistilled-labs/data/portfolio.csv'
   parts = arn.split(':')
   parts
   len(parts)
   ```

   You get `['arn', 'aws', 's3', '', '', 'pydistilled-labs/data/portfolio.csv']` — six fields. S3 is global, so the region and account fields are empty strings, not missing. That is why `arn:aws:s3:::` has three colons in a row.
2. Name the fields by unpacking, which you know from Python Lab 6:

   ```python
   prefix, partition, service, region, account, resource = arn.split(':')
   print(f'{service=} {region=!r} {account=!r} {resource=}')
   ```

   The `!r` shows the empty strings as `''` rather than as nothing at all.
3. Compare with an IAM ARN, where those fields are populated differently:

   ```python
   user_arn = 'arn:aws:iam::123456789012:user/rahde-lab'
   parts = user_arn.split(':')
   parts
   parts[4]                      # '123456789012' — account present
   parts[5].split('/')           # ['user', 'rahde-lab'] — type and name
   ```

   IAM is also global, so region is empty — but the account is not. Each service decides which fields it uses.
4. Hit the trap. Why you must bound the split:

   ```python
   weird = 'arn:aws:s3:::my-bucket/logs/2026:10:20/app.log'
   weird.split(':')              # Eight items — the key contained colons!
   weird.split(':', 5)           # Six items — correct
   ```

   `split(':', 5)` stops after five splits and leaves the rest intact. Always bound the split when parsing ARNs; S3 keys may legally contain colons.
5. Work S3 keys as paths, using slicing and `rsplit`:

   ```python
   key = 'data/2026/10/portfolio.csv'
   
   key.split('/')                # All the segments
   key.rsplit('/', 1)            # ['data/2026/10', 'portfolio.csv'] — dir and file
   key.rsplit('/', 1)[-1]        # 'portfolio.csv'
   key.rsplit('.', 1)[-1]        # 'csv' — the extension
   key.startswith('data/')       # True — this is what a prefix filter does
   key[:key.rindex('/')]         # 'data/2026/10'
   ```

   S3 has no real directories. A key is one flat string, and `/` is a convention that the console renders as folders.
6. Build ARNs and keys with f-strings instead of concatenation:

   ```python
   account = '123456789012'
   region = 'us-east-1'
   bucket = 'pydistilled-labs'
   
   bucket_arn = f'arn:aws:s3:::{bucket}'
   object_arn = f'arn:aws:s3:::{bucket}/*'
   table_arn  = f'arn:aws:dynamodb:{region}:{account}:table/Holdings'
   role_arn   = f'arn:aws:iam::{account}:role/LabRole'
   
   for a in [bucket_arn, object_arn, table_arn, role_arn]:
       print(a)
   ```

   Note that `object_arn` ends in `/*`, while `bucket_arn` does not. Confusing the two is the most common IAM policy mistake there is — Lab 7 comes back to it.
7. Generate a dated key prefix, combining `datetime` formatting with f-strings:

   ```python
   from datetime import datetime, timezone
   
   now = datetime.now(timezone.utc)
   prefix = f'data/{now:%Y/%m/%d}'
   print(f'{prefix}/portfolio.csv')
   ```

   The `{now:%Y/%m/%d}` format spec inside an f-string works on `datetime` objects — the same mechanism as `{price:0.2f}` on a float.
8. Write `arninfo.py` that parses any ARN into a labelled report:

   ```python
   # arninfo.py
   
   def parse_arn(arn):
       prefix, partition, service, region, account, resource = arn.split(':', 5)
       return {
           'service': service,
           'region': region or '(global)',
           'account': account or '(none)',
           'resource': resource,
       }
   
   if __name__ == '__main__':
       for arn in ['arn:aws:s3:::pydistilled-labs/data/portfolio.csv',
                   'arn:aws:iam::123456789012:user/rahde-lab',
                   'arn:aws:dynamodb:us-east-1:123456789012:table/Holdings']:
           print(arn)
           for field, value in parse_arn(arn).items():
               print(f'  {field:<10} {value}')
   ```

   `region or '(global)'` uses the truthiness of the empty string from Lab 3 — an empty field falls through to the default.

**Checkpoint** — `arninfo.py` reports S3 as `(global)` with no account, and DynamoDB as `us-east-1` with account `123456789012`.

**Stretch** — Make `parse_arn` raise `ValueError('not an ARN')` when the string does not start with `arn:`, then test it.

**Self-check**

- Why does `arn:aws:s3:::bucket` have three consecutive colons?
- Why must you use `split(':', 5)` rather than `split(':')`?

---

[← Lab 3](lab-03-conditionals-over-aws-state.md) · [AWS track index](../README.md) · [Paired Python track lab 4](../../python-track/labs/lab-04-text-strings-and-formatting.md) · [Lab 5 →](lab-05-local-files-to-s3-and-back.md)
