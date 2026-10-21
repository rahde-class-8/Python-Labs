## Lab 3 — Conditionals over cloud state

**Pairs with Python Lab 3 (§1.5) · 25 minutes**

Goal: branch on cloud responses, and learn where a missing key or an empty value is waiting for you.

**Steps**

1. Start with the client library, which protects you. Create `empty.py`:

   ```python
   # empty.py
   from google.cloud import storage
   from gcpmock import mock_gcs

   def main():
       with mock_gcs():
           client = storage.Client(project='pydistilled')
           bucket = client.create_bucket('pydistilled-labs')

           for blob in client.list_blobs(bucket):
               print(blob.name)
           print('done listing')

           print(repr(bucket.labels))
           print(bucket.get_blob('nope.csv'))
           print(client.lookup_bucket('no-such-bucket-xyz'))

   if __name__ == '__main__':
       main()
   ```

   Nothing crashes. An empty listing loops zero times, a bucket with no labels has `{}`, and the `get_blob` and `lookup_bucket` calls return `None` for something that does not exist. If you did the AWS track, this is the opposite of Lab 3 there: the client library absorbed the missing-key problem for you.
2. Use those values in conditions, relying on truthiness:

   ```python
   if not bucket.labels:
       print('bucket is unlabelled')

   blob = bucket.get_blob('nope.csv')
   if blob is None:
       print('not uploaded yet')

   found = client.lookup_bucket('no-such-bucket-xyz')
   print('exists' if found else 'missing')
   ```

   Note `blob is None` rather than `not blob`. Both work here, but `is None` says what you mean: you are asking "was anything returned", not "is it empty".
3. Now meet the raw JSON, which does *not* protect you. Load the saved Compute Engine listing:

   ```python
   import json

   with open('instances.json') as f:
       instances = json.load(f)

   for inst in instances:
       print(inst['name'], inst['labels'])      # KeyError on the fourth
   ```

   It raises `KeyError: 'labels'`. An instance with no labels does not have an empty `labels` dict in the JSON — the key is absent. The same is true of most optional fields in Google's REST responses. Whenever you work from `gcloud ... --format=json` output, a REST call, or a saved response, you are back to handling missing keys yourself.
4. Fix it, and confirm the truthiness rules on the values involved:

   ```python
   for inst in instances:
       print(inst['name'], inst.get('labels', {}))

   for value in [{}, [], '', None, inst.get('labels'), instances[0].get('labels')]:
       print(repr(value), '->', bool(value))
   ```

   `.get('labels', {})` is the form to internalize. An empty dict is falsy, so code that tests it simply skips the unlabelled case.
5. Branch on instance status with a full `if`/`elif`/`else` chain. Create `triage.py`:

   ```python
   # triage.py
   import json

   def main():
       with open('instances.json') as f:
           instances = json.load(f)

       for inst in instances:
           status = inst['status']
           if status == 'RUNNING':
               verdict = 'billing now — CPU, memory and disks'
           elif status == 'TERMINATED':
               verdict = 'stopped — disks still billed'
           elif status == 'SUSPENDED':
               verdict = 'suspended — disks and saved memory billed'
           else:
               verdict = f'in transition: {status!r}'
           print(f"{inst['name']:<10} {status:<11} {verdict}")

   if __name__ == '__main__':
       main()
   ```

   The trap here is vocabulary. In Compute Engine, `TERMINATED` means *stopped*, not deleted: the instance still exists, can be started again, and its disks still cost money. A deleted instance simply disappears from the listing.
6. Add a label-compliance scan, using `continue` to skip what you do not care about:

   ```python
   REQUIRED = 'env'

   for inst in instances:
       labels = inst.get('labels', {})
       if REQUIRED in labels:
           continue                       # Compliant — nothing to report
       print('MISSING LABEL:', inst['name'], inst['status'])
   ```

   Note that labels are already a dictionary. If you did the AWS track, compare this with converting AWS tags from a list of dicts first. Lab 7 comes back to it.
7. Use `break` to stop at the first problem, for a fail-fast check:

   ```python
   first_bad = None
   for inst in instances:
       if not inst.get('labels'):
           first_bad = inst['name']
           break

   if first_bad:
       raise SystemExit(f'Unlabelled instance found: {first_bad}')
   print('All labelled')
   ```

   One loop, one `break`. The listing from `gcloud compute instances list` is already flat; Lab 6 shows the nested form the API can also return, and what it does to code like this.

**Checkpoint** — `empty.py` prints `done listing`, `{}`, `None` and `None` without crashing; `triage.py` lists four instances with two `RUNNING`, one `TERMINATED` and one `SUSPENDED`; the label scan flags exactly one instance, `scratch`.

**Stretch** — Add a `STOPPING` instance to your copy of `instances.json` and rerun `triage.py` to exercise the `else` branch.

**Self-check**

- Why does `bucket.labels` give `{}` while `inst['labels']` raises `KeyError` for the same idea?
- What does `TERMINATED` mean in Compute Engine, and does it cost anything?

---

[← Lab 2](lab-02-cloud-types-and-cost-arithmetic.md) · [GCP track index](../README.md) · [Paired Python track lab 3](../../python-track/labs/lab-03-conditionals-and-control-flow.md) · [Paired AWS track lab 3](../../aws-track/labs/lab-03-conditionals-over-aws-state.md) · [Lab 4 →](lab-04-resource-names-urls-and-gs-string-surgery.md)
