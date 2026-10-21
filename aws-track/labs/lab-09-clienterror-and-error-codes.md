## Lab 9 — ClientError and error codes

**Pairs with Python Lab 9 (§1.14–1.15) · 30 minutes**

Goal: boto3 funnels almost every AWS failure through one exception class, so the useful information is inside the object, not in its type. Learn to read it.

**Steps**

1. Create `errors.py` and trigger a failure:

   ```python
   # errors.py
   import boto3
   from moto import mock_aws
   from botocore.exceptions import ClientError
   
   BUCKET = 'pydistilled-labs'
   
   @mock_aws
   def main():
       s3 = boto3.client('s3', region_name='us-east-1')
       s3.create_bucket(Bucket=BUCKET)
   
       s3.get_object(Bucket=BUCKET, Key='nope.csv')
   
   if __name__ == '__main__':
       main()
   ```

   Read the traceback bottom-up, as on the Python track. The last line is `botocore.exceptions.ClientError: An error occurred (NoSuchKey) ...`. The code you need is in the parentheses.
2. Catch it and take the exception apart:

   ```python
   try:
       s3.get_object(Bucket=BUCKET, Key='nope.csv')
   except ClientError as err:
       print('code:   ', err.response['Error']['Code'])
       print('message:', err.response['Error']['Message'])
       print('status: ', err.response['ResponseMetadata']['HTTPStatusCode'])
   ```

   You get `NoSuchKey`, a message, and `404`. The whole response dict is hanging off the exception — this is the thing to know about boto3 error handling.
3. See why the *type* alone is not enough. Both of these raise the same class:

   ```python
   for bucket, key in [(BUCKET, 'nope.csv'), ('no-such-bucket-xyz', 'any.csv')]:
       try:
           s3.get_object(Bucket=bucket, Key=key)
       except ClientError as err:
           print(bucket, '->', err.response['Error']['Code'])
   ```

   `NoSuchKey` and `NoSuchBucket` are the same Python type. `except ClientError` cannot tell them apart; only the code can. This is the opposite of the Python track, where `ValueError` and `IndexError` were different classes.
4. Branch on the code — the boto3 equivalent of multiple `except` clauses:

   ```python
   def fetch(s3, bucket, key):
       try:
           return s3.get_object(Bucket=bucket, Key=key)['Body'].read()
       except ClientError as err:
           code = err.response['Error']['Code']
           if code == 'NoSuchKey':
               print(f'{key} not there yet — treating as empty')
               return b''
           elif code == 'NoSuchBucket':
               raise SystemExit(f'Bucket {bucket} does not exist. Check the name.')
           elif code in ('AccessDenied', 'InvalidAccessKeyId'):
               raise SystemExit('Credentials or policy problem. Not retrying.')
           else:
               raise            # Unknown — let it propagate
   
   print(fetch(s3, BUCKET, 'nope.csv'))
   ```

   The bare `raise` at the end re-raises the current exception unchanged. Swallowing errors you did not plan for is how outages get hidden.
5. Note which errors are worth retrying and which are not:
   - `NoSuchKey`, `NoSuchBucket`, `AccessDenied`, `ValidationException` — never retry. The answer will not change.
   - `Throttling`, `ThrottlingException`, `RequestLimitExceeded`, `ServiceUnavailable`, `InternalError` — retry with backoff. boto3 already retries some of these for you.

   Retrying a permission error in a loop is how you turn one failure into a rate-limit incident.
6. Trigger a validation error from a different service, to see the pattern holds:

   ```python
   ddb = boto3.client('dynamodb', region_name='us-east-1')
   ddb.create_table(
       TableName='Holdings',
       KeySchema=[{'AttributeName': 'Symbol', 'KeyType': 'HASH'}],
       AttributeDefinitions=[{'AttributeName': 'Symbol', 'AttributeType': 'S'}],
       BillingMode='PAY_PER_REQUEST')
   
   table = boto3.resource('dynamodb', region_name='us-east-1').Table('Holdings')
   try:
       table.put_item(Item={'Shares': 1})        # No Symbol — missing the key
   except ClientError as err:
       print(err.response['Error']['Code'])      # ValidationException
   ```

   Same exception class, different service, different code. One `except ClientError` plus a code lookup covers all of AWS.
7. Use `try`/`finally` for teardown that must happen regardless. This is the habit that keeps a real account clean:

   ```python
   s3.create_bucket(Bucket='temp-scratch-bucket')
   try:
       s3.put_object(Bucket='temp-scratch-bucket', Key='x', Body=b'x')
       raise RuntimeError('something went wrong mid-job')
   finally:
       for obj in s3.list_objects_v2(
               Bucket='temp-scratch-bucket').get('Contents', []):
           s3.delete_object(Bucket='temp-scratch-bucket', Key=obj['Key'])
       s3.delete_bucket(Bucket='temp-scratch-bucket')
       print('cleaned up')
   ```

   `cleaned up` prints even though the job failed. Note that you must empty a bucket before deleting it — and that `.get('Contents', [])` is doing its Lab 3 job again.
8. Make the script exit properly. Add to `errors.py`:

   ```python
   if __name__ == '__main__':
       import sys
       if len(sys.argv) != 3:
           raise SystemExit(f'Usage: {sys.argv[0]} bucket key')
       main()
   ```

   Run it with no arguments and check `echo $?` — a non-zero exit status is what makes a script usable in a pipeline.

**Checkpoint** — you can print `NoSuchKey` and `404` from a caught `ClientError`, `fetch` returns `b''` for a missing key, and `cleaned up` prints despite the `RuntimeError`.

**Stretch** — Write `head_exists(s3, bucket, key)` returning `True`/`False` using `head_object` and catching only `404`. Compare it with calling `list_objects_v2` and checking the result.

**Self-check**

- Why is `except ClientError` usually not specific enough?
- Which error codes should never be retried, and why?

---

[← Lab 8](lab-08-paginators-as-iteration-functions-as-the-fix.md) · [AWS track index](../README.md) · [Paired Python track lab 9](../../python-track/labs/lab-09-exceptions-and-program-termination.md) · [Paired GCP track lab 9](../../gcp-track/labs/lab-09-api-exceptions-and-status-codes.md) · [Lab 10 →](lab-10-wrapping-boto3-in-a-class.md)
