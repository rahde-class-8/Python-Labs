## Lab 9 — API exceptions and status codes

**Pairs with Python Lab 9 (§1.14–1.15) · 30 minutes**

Goal: Google's libraries raise a different exception class for each kind of failure, so `except` clauses do the sorting for you. Learn the hierarchy and how to read an exception.

**Steps**

1. Create `errors.py` and trigger a failure:

   ```python
   # errors.py
   from google.cloud import storage
   from gcpmock import mock_gcs

   BUCKET = 'pydistilled-labs'

   def main():
       with mock_gcs():
           client = storage.Client(project='pydistilled')
           bucket = client.create_bucket(BUCKET)

           bucket.blob('nope.csv').download_as_bytes()

   if __name__ == '__main__':
       main()
   ```

   Read the traceback bottom-up, as on the Python track. The last line starts with `google.api_core.exceptions.NotFound: 404`. The class name and the HTTP status code tell you what happened before you read anything else.
2. Catch it and take the exception apart:

   ```python
   from google.api_core.exceptions import NotFound

   try:
       bucket.blob('nope.csv').download_as_bytes()
   except NotFound as err:
       print('type:   ', type(err).__name__)
       print('code:   ', err.code)
       print('message:', err.message)
   ```

   You get `NotFound`, `404`, and a message naming the request. `err.code` is the HTTP status as an `int`.
3. See the class hierarchy that makes `except` useful:

   ```python
   from google.api_core import exceptions

   exceptions.NotFound.__mro__
   ```

   `NotFound` is a `ClientError`, which is a `GoogleAPICallError`, which is an `Exception`. Every 4xx status has its own class under `ClientError` (`Forbidden` is 403, `Conflict` is 409, `TooManyRequests` is 429), and every 5xx under `ServerError` (`ServiceUnavailable` is 503). If you did the AWS track, this is the opposite design: boto3 raises one `ClientError` for everything and makes you read a code out of a dict. Here, Python Lab 9's multiple `except` clauses work exactly as written.
4. Trigger two other classes:

   ```python
   from google.api_core.exceptions import Conflict

   for action in [lambda: client.create_bucket(BUCKET),     # Already exists
                  lambda: bucket.delete()]:                 # Not empty yet
       try:
           bucket.blob('keep.txt').upload_from_string('x')
           action()
       except Conflict as err:
           print(type(err).__name__, err.code)
   ```

   Both are `Conflict`, 409. A bucket that still holds objects cannot be deleted, and a name that is taken cannot be created. A `lambda` here is a small unnamed function, so the loop can hold two different actions and call each one.
5. Notice what the class does *not* tell you:

   ```python
   for b, name in [(BUCKET, 'nope.csv'), ('no-such-bucket-xyz', 'any.csv')]:
       try:
           client.bucket(b).blob(name).download_as_bytes()
       except NotFound as err:
           print(b, '->', type(err).__name__)
   ```

   A missing object and a missing bucket are both `NotFound`. The class tells you the status, not which resource was missing. When the difference matters, check the bucket with `client.lookup_bucket(b)`.
6. Branch with multiple `except` clauses — the most specific first:

   ```python
   from google.api_core.exceptions import Forbidden, GoogleAPICallError

   def fetch(client, bucket, name):
       try:
           return client.bucket(bucket).blob(name).download_as_bytes()
       except NotFound:
           if client.lookup_bucket(bucket) is None:
               raise SystemExit(f'Bucket {bucket} does not exist. Check the name.')
           print(f'{name} not there yet — treating as empty')
           return b''
       except Forbidden:
           raise SystemExit('Credentials or IAM problem. Not retrying.')
       except GoogleAPICallError:
           raise            # Anything else — let it propagate

   print(fetch(client, BUCKET, 'nope.csv'))
   ```

   The bare `raise` at the end re-raises the current exception unchanged. Swallowing errors you did not plan for is how outages get hidden. Order matters: the first `except` that matches wins, so `GoogleAPICallError` must come after the specific classes it contains.
7. Note which errors are worth retrying and which are not:
   - `NotFound`, `Forbidden`, `Conflict`, `BadRequest` — never retry. The answer will not change.
   - `TooManyRequests`, `InternalServerError`, `ServiceUnavailable`, `GatewayTimeout` — retry with backoff.

   The storage library already retries the second group for you on safe operations, using `google.cloud.storage.retry.DEFAULT_RETRY`. It also retries network failures, for up to two minutes, which is why a script pointed at an emulator that is not running seems to hang instead of failing. Retrying a permission error in a loop is how you turn one failure into a rate-limit incident.
8. Use `try`/`finally` for teardown that must happen regardless:

   ```python
   temp = client.create_bucket('temp-scratch-bucket')
   try:
       temp.blob('x').upload_from_string('x')
       raise RuntimeError('something went wrong mid-job')
   finally:
       temp.delete(force=True)
       print('cleaned up')
   ```

   `cleaned up` prints even though the job failed. `delete(force=True)` deletes the objects first and then the bucket, which avoids the `Conflict` from step 4. It refuses buckets with more than 256 objects, so large buckets need a loop over `list_blobs` instead. Then look back at `gcpmock.py`: its `try`/`finally` is this same pattern, and it is why the emulator always shuts down even when a lab script crashes.
9. Make the script exit properly. Replace the guard at the bottom of `errors.py`:

   ```python
   if __name__ == '__main__':
       import sys
       if len(sys.argv) != 3:
           raise SystemExit(f'Usage: {sys.argv[0]} bucket name')
       main()
   ```

   Run it with no arguments and check `echo $?` — a non-zero exit status is what makes a script usable in a pipeline.

**Checkpoint** — you can print `NotFound` and `404` from a caught exception, step 4 prints `Conflict 409` twice, `fetch` returns `b''` for a missing object, and `cleaned up` prints despite the `RuntimeError`.

**Stretch** — Write `fetch_or_none(bucket, name)` using `bucket.get_blob(name)` instead of catching `NotFound`, and decide which version you would rather read.

**Self-check**

- Why does `except NotFound` work here when `except ClientError` was the only option in boto3?
- Why must `except GoogleAPICallError` come after `except NotFound`?

---

[← Lab 8](lab-08-iterators-as-iteration-functions-as-the-fix.md) · [GCP track index](../README.md) · [Paired Python track lab 9](../../python-track/labs/lab-09-exceptions-and-program-termination.md) · [Paired AWS track lab 9](../../aws-track/labs/lab-09-clienterror-and-error-codes.md) · [Lab 10 →](lab-10-wrapping-the-client-in-a-class.md)
