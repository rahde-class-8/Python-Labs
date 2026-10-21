## Lab 5 — Local files to S3 and back

**Pairs with Python Lab 5 (§1.7) · 30 minutes**

Goal: the four ways to move bytes in and out of S3, and the `bytes`-versus-`str` boundary that catches everyone.

**Steps**

1. Create `s3io.py` with a bucket and the portfolio file uploaded two ways:

   ```python
   # s3io.py
   import boto3
   from moto import mock_aws
   
   BUCKET = 'pydistilled-labs'
   
   @mock_aws
   def main():
       s3 = boto3.client('s3', region_name='us-east-1')
       s3.create_bucket(Bucket=BUCKET)
   
       # Way 1: upload_file — give it a path, it handles opening
       s3.upload_file('portfolio.csv', BUCKET, 'uploaded/portfolio.csv')
   
       # Way 2: put_object — give it bytes or a file object
       with open('portfolio.csv', 'rb') as f:
           s3.put_object(Bucket=BUCKET, Key='direct/portfolio.csv', Body=f)
   
       for obj in s3.list_objects_v2(Bucket=BUCKET).get('Contents', []):
           print(obj['Key'], obj['Size'])
   
   if __name__ == '__main__':
       main()
   ```

   Note `'rb'` — binary mode. S3 stores bytes, and `put_object` wants bytes, not text.
2. Prove the bytes boundary. Add this and watch it fail:

   ```python
   s3.put_object(Bucket=BUCKET, Key='bad.csv', Body='AA,100,32.20')     # str
   ```

   This one actually works — boto3 encodes a `str` for you as UTF-8. But reading does *not* decode for you, which is the asymmetry to remember.
3. Read it back and meet the `StreamingBody`:

   ```python
   response = s3.get_object(Bucket=BUCKET, Key='uploaded/portfolio.csv')
   body = response['Body']
   type(body)                 # StreamingBody, or StreamingChecksumBody on newer boto3
   
   raw = body.read()
   type(raw)                  # bytes — not str
   raw[:20]
   text = raw.decode('utf-8')
   print(text)
   
   body.read()                # b'' — the stream is exhausted
   ```

   Either way it is a stream, and it can only be read once. Read it twice and the second call returns nothing — a genuinely confusing bug if you do not know it.
4. Iterate line by line, which is the S3 equivalent of looping over an open file:

   ```python
   body = s3.get_object(Bucket=BUCKET, Key='uploaded/portfolio.csv')['Body']
   for line in body.iter_lines():
       print(line)
   ```

   Each line is `bytes` and the newline is already stripped. Compare with the Python track, where lines were `str` and kept their `\n`.
5. Decode as you iterate, so the rest of your code sees text:

   ```python
   body = s3.get_object(Bucket=BUCKET, Key='uploaded/portfolio.csv')['Body']
   for line in body.iter_lines():
       row = line.decode('utf-8').split(',')
       print(row)
   ```

   That `.decode('utf-8').split(',')` is the S3 version of `line.split(',')` from Python Lab 6.
6. Download to a local file and verify the round trip:

   ```python
   s3.download_file(BUCKET, 'uploaded/portfolio.csv', 'roundtrip.csv')
   
   original = open('portfolio.csv', 'rb').read()
   returned = open('roundtrip.csv', 'rb').read()
   print('identical:', original == returned)
   ```
7. Write *generated* content straight to S3, the equivalent of Python Lab 5's `out.txt`. Use `io.StringIO` to build it in memory:

   ```python
   import io
   
   buffer = io.StringIO()
   principal = 1000
   rate = 0.05
   for year in range(1, 6):
       principal = principal * (1 + rate)
       print(f'{year:>3d} {principal:0.2f}', file=buffer)
   
   s3.put_object(Bucket=BUCKET, Key='reports/interest.txt',
                 Body=buffer.getvalue())
   
   back = s3.get_object(Bucket=BUCKET, Key='reports/interest.txt')['Body']
   print(back.read().decode('utf-8'))
   ```

   `print(..., file=buffer)` is exactly the `file=` argument from Python Lab 5 — only the destination changed. A `StringIO` behaves like an open file but keeps everything in memory, which matters because S3 has no append.
8. Confirm S3 has no append. Put a second object at the same key:

   ```python
   s3.put_object(Bucket=BUCKET, Key='reports/interest.txt', Body='replaced\n')
   print(s3.get_object(Bucket=BUCKET, Key='reports/interest.txt')['Body'].read())
   ```

   The old content is gone. There is no `'at'` mode for S3 — every write is a whole-object replacement. To append, you read, concatenate and put the whole thing back.

**Checkpoint** — `s3io.py` lists four or more objects, the round-trip comparison prints `identical: True`, and reading an exhausted `StreamingBody` returns `b''`.

**Stretch** — Write `s3_append(s3, bucket, key, text)` that reads the current object, appends, and puts it back. Then write down why this is unsafe with two writers.

**Self-check**

- Why does `get_object` return `bytes` when `put_object` accepted a `str`?
- What happens on the second `body.read()`, and why?

---

[← Lab 4](lab-04-arn-and-s3-key-string-surgery.md) · [AWS track index](../README.md) · [Paired Python track lab 5](../../python-track/labs/lab-05-file-input-and-output.md) · [Paired GCP track lab 5](../../gcp-track/labs/lab-05-local-files-to-cloud-storage-and-back.md) · [Lab 6 →](lab-06-lists-and-tuples-from-aws-responses.md)
