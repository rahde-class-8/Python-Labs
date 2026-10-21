## Lab 1 — boto3 in the REPL and your first mocked script

**Pairs with Python Lab 1 (§1.1–1.2) · 25 minutes**

Goal: get the same REPL-then-script rhythm, but with boto3, and understand the one rule about where mocking applies.

**Steps**

1. In the REPL, confirm boto3 is installed and see what a client is:

   ```python
   import boto3
   boto3.__version__
   s3 = boto3.client('s3', region_name='us-east-1')
   type(s3)
   ```

   The class name is generated at runtime from AWS's own service definitions. There is no hand-written `S3Client` class in boto3.
2. Try a call *without* mocking, to see what you are avoiding:

   ```python
   s3.list_buckets()
   ```

   With fake credentials this fails — an `InvalidAccessKeyId` or a connection error. This is the correct outcome. Now do it properly.
3. Create `whoami.py`:

   ```python
   # whoami.py
   import boto3
   from moto import mock_aws
   
   @mock_aws
   def main():
       sts = boto3.client('sts', region_name='us-east-1')
       print(sts.get_caller_identity())
   
   if __name__ == '__main__':
       main()
   ```

   Run it. You get moto's fixed fake identity:

   ```
   {'UserId': 'AKIAIOSFODNN7EXAMPLE',
    'Account': '123456789012',
    'Arn': 'arn:aws:sts::123456789012:user/moto', ...}
   ```

   Account `123456789012` is moto's stand-in account number. You will see it in every ARN this track produces — Lab 4 takes it apart.
4. Note the `ResponseMetadata` key in that output. Every boto3 response carries it. Real response data and transport metadata arrive in the same dictionary, which is a thing to get used to.
5. Learn the mocking boundary the hard way. Make this mistake deliberately:

   ```python
   # broken.py
   import boto3
   from moto import mock_aws
   
   s3 = boto3.client('s3', region_name='us-east-1')   # Outside the mock!
   
   @mock_aws
   def main():
       s3.create_bucket(Bucket='too-late')
   
   main()
   ```

   It fails or tries to reach real AWS. Move the client creation inside `main()` and it works. **The client must be created inside the mock.**
6. Use the context-manager form instead of the decorator, which is handier in the REPL:

   ```python
   from moto import mock_aws
   import boto3
   
   with mock_aws():
       s3 = boto3.client('s3', region_name='us-east-1')
       s3.create_bucket(Bucket='scratch')
       print(s3.list_buckets()['Buckets'])
   ```

   You already know `with` from Python Lab 5 — this is the same statement doing setup and teardown.
7. See that `client` and `resource` are two interfaces to the same service:

   ```python
   with mock_aws():
       s3c = boto3.client('s3', region_name='us-east-1')
       s3c.create_bucket(Bucket='scratch')
   
       s3r = boto3.resource('s3', region_name='us-east-1')
       for b in s3r.buckets.all():
           print(b.name)
   ```

   `client` mirrors the API one call at a time; `resource` wraps it in objects. This track uses `client` almost everywhere, because that is what the docs and the exams describe.

**Checkpoint** — `whoami.py` prints account `123456789012`, and you can state why the client must be created inside the mock.

**Stretch** — Run two separate `with mock_aws():` blocks, creating a bucket in the first and listing buckets in the second. Explain the result.

**Self-check**

- What does `ResponseMetadata` tell you, and why is it in the same dict as your data?
- Why does a client created at module level not get mocked?

---

[AWS track index](../README.md) · [Paired Python track lab 1](../../python-track/labs/lab-01-the-repl-and-your-first-script.md) · [Paired GCP track lab 1](../../gcp-track/labs/lab-01-the-client-library-and-your-first-emulated-script.md) · [Lab 2 →](lab-02-aws-types-and-cost-arithmetic.md)
