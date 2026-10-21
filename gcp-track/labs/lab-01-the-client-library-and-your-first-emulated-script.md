## Lab 1 — The client library and your first emulated script

**Pairs with Python Lab 1 (§1.1–1.2) · 25 minutes**

Goal: get the same REPL-then-script rhythm with `google-cloud-storage`, and understand the one rule about where emulation applies.

**Steps**

1. In the REPL, confirm the library is installed and see what you are importing:

   ```python
   from google.cloud import storage
   storage.__version__
   storage.Client
   ```

   `google.cloud` is a shared namespace. Every Google Cloud library (`storage`, `bigquery`, `pubsub` and the rest) installs into it separately, which is why you import `storage` *from* it rather than importing one big SDK.
2. Try creating a client *without* the emulator, to see what you are avoiding:

   ```python
   client = storage.Client()
   ```

   On a machine with no Google Cloud login this fails immediately with `DefaultCredentialsError`. Google's libraries look for **Application Default Credentials** the moment you create a client, not when you first make a call. That is earlier than boto3, which waits until the first request. The failure is the correct outcome here. If it succeeds, you have run `gcloud auth application-default login` at some point, and this client is talking to your real account. Do not make calls with it.
3. Create `whoami.py`:

   ```python
   # whoami.py
   from google.cloud import storage
   from gcpmock import mock_gcs

   def main():
       with mock_gcs():
           client = storage.Client(project='pydistilled')
           print('project:    ', client.project)
           print('credentials:', type(client._credentials).__name__)
           bucket = client.create_bucket('pydistilled-labs')
           print('bucket:     ', bucket.name, bucket.location, bucket.storage_class)

   if __name__ == '__main__':
       main()
   ```

   Run it. You get:

   ```
   project:     pydistilled
   credentials: AnonymousCredentials
   bucket:      pydistilled-labs US STANDARD
   ```

   When `STORAGE_EMULATOR_HOST` is set, the library switches to anonymous credentials by itself. `pydistilled` is a project ID you made up. In Google Cloud, almost everything lives inside a **project**, and the project ID turns up in every resource name this track produces. Lab 4 takes those names apart.
4. Note `client._credentials`. The leading underscore marks it as internal (§1.16 comes back to this in Lab 10). You are reading it only to see which credentials were picked. Real code never touches it.
5. Learn the emulation boundary the hard way. Make this mistake deliberately:

   ```python
   # broken.py
   from google.cloud import storage
   from gcpmock import mock_gcs

   client = storage.Client(project='pydistilled')   # Outside the emulator!

   def main():
       with mock_gcs():
           client.create_bucket('too-late')

   main()
   ```

   It fails on the `storage.Client(...)` line with `DefaultCredentialsError`, before `main()` is ever called. Move the client creation inside the `with` block and it works. **The client must be created inside the emulator block**, because the client reads `STORAGE_EMULATOR_HOST` once, when it is created.
6. Use the emulator interactively. The `with` form works the same at the `>>>` prompt:

   ```python
   from google.cloud import storage
   from gcpmock import mock_gcs

   with mock_gcs():
       client = storage.Client(project='pydistilled')
       client.create_bucket('scratch')
       print([b.name for b in client.list_buckets()])
   ```

   You already know `with` from Python Lab 5. This is the same statement doing setup and teardown, and `gcpmock.py` is what decides what setup and teardown mean.
7. See that a `Bucket` object and a bucket are not the same thing:

   ```python
   with mock_gcs():
       client = storage.Client(project='pydistilled')
       local = client.bucket('never-created')     # No API call at all
       print(local, local.exists())               # <Bucket: never-created> False
       client.get_bucket('never-created')         # NotFound — this one asks the server
   ```

   `client.bucket(name)` only builds a Python object with a name in it. `client.get_bucket(name)` makes a request and fails if the bucket is not there. The client library is full of these lazy handles; knowing which calls touch the network is most of reading it well.

**Checkpoint** — `whoami.py` prints project `pydistilled` with `AnonymousCredentials`, and you can state why the client must be created inside the emulator block.

**Stretch** — Run two separate `with mock_gcs():` blocks, creating a bucket in the first and listing buckets in the second. Explain the result.

**Self-check**

- When does a Google Cloud client look for credentials, and how is that different from boto3?
- What is the difference between `client.bucket(name)` and `client.get_bucket(name)`?

---

[GCP track index](../README.md) · [Paired Python track lab 1](../../python-track/labs/lab-01-the-repl-and-your-first-script.md) · [Paired AWS track lab 1](../../aws-track/labs/lab-01-boto3-in-the-repl-and-your-first-mocked-script.md) · [Lab 2 →](lab-02-cloud-types-and-cost-arithmetic.md)
