## Lab 6 — Lists and tuples from cloud listings

**Pairs with Python Lab 6 (§1.8–1.9) · 30 minutes**

Goal: reshape listings into the list-of-tuples form from the Python track, and flatten the nested ones.

**Steps**

1. Create `inventory.py`, populate a bucket, and look at the shape you get back:

   ```python
   # inventory.py
   from google.cloud import storage
   from gcpmock import mock_gcs

   BUCKET = 'pydistilled-labs'

   def main():
       with mock_gcs():
           client = storage.Client(project='pydistilled')
           bucket = client.create_bucket(BUCKET)

           for name, body in [('data/portfolio.csv', b'AA,100,32.20\nIBM,50,91.10\n'),
                              ('data/notes.txt', b'short'),
                              ('logs/app.log', b'x' * 4096),
                              ('logs/old.log', b'y' * 512)]:
               bucket.blob(name).upload_from_string(body)

           blobs = list(client.list_blobs(bucket))
           print(type(blobs), len(blobs))
           print(type(blobs[0]))
           print(blobs[0].name, blobs[0].size)

   if __name__ == '__main__':
       main()
   ```

   `list_blobs` returns an iterator (Lab 8 is about that), and `list(...)` turns it into an ordinary `list`. Each element is a `Blob` object with attributes, not a dict with keys: `blob.size`, not `blob['Size']`. All the list operations from §1.8 apply to the result directly.
2. Index and slice it as a list:

   ```python
   blobs[0].name
   blobs[-1].name
   [b.name for b in blobs[:2]]
   len(blobs)
   ```
3. Reshape into a list of tuples — the same structure Python Lab 6 built from a CSV:

   ```python
   inventory = [(b.name, b.size) for b in blobs]
   inventory

   for name, size in inventory:          # Tuple unpacking in the loop
       print(f'{name:<24} {size:>8}')

   total = sum(size for _, size in inventory)
   print('total bytes:', total)
   ```

   The `_` throwaway variable does the same job it did on the Python track.
4. Sort by size, descending, and find the biggest object:

   ```python
   inventory.sort(key=lambda pair: pair[1], reverse=True)
   inventory[0]

   largest = max(blobs, key=lambda b: b.size)
   print(largest.name, largest.size)
   ```

   `sort()` mutates and returns `None`; `sorted()` returns a new list. Same rule as §1.8.
5. Filter with a comprehension, then do it server-side instead:

   ```python
   logs = [b.name for b in blobs if b.name.startswith('logs/')]
   big  = [b.name for b in blobs if b.size > 1000]

   logs = [b.name for b in client.list_blobs(bucket, prefix='logs/')]
   ```

   The `prefix` argument filters before the data crosses the network. A comprehension filters after. On a bucket with a million objects, the difference is the whole ballgame.
6. Ask for "folders" with a delimiter, and meet an attribute that fills in late:

   ```python
   listing = client.list_blobs(bucket, delimiter='/')
   print(listing.prefixes)              # set() — nothing fetched yet
   top_level = [b.name for b in listing]
   print(top_level)                     # [] — every object is inside a "folder"
   print(sorted(listing.prefixes))      # ['data/', 'logs/']
   ```

   Cloud Storage has no real directories; `/` is part of the object name. A delimiter asks the server to group names by their first `/`, and the groups arrive as `prefixes`. That set is only filled in while you iterate, so reading it before the loop gives an empty set.
7. Now meet a genuinely nested response. The Compute Engine API's *aggregated* listing groups instances by zone:

   ```python
   import json

   with open('aggregated.json') as f:
       response = json.load(f)

   list(response['items'])                                  # One key per zone
   response['items']['zones/us-central1-a'].keys()          # dict_keys(['instances'])
   response['items']['zones/europe-west1-b'].keys()         # dict_keys(['warning'])
   ```

   A zone with instances has an `instances` list. A zone with none has no `instances` key at all, only a `warning`. Lab 3's missing-key problem, one level down.
8. Flatten it. The nested loop first, then the comprehension that replaces it:

   ```python
   instances = []
   for scope, data in response['items'].items():
       for inst in data.get('instances', []):
           instances.append(inst)

   instances = [inst
                for data in response['items'].values()
                for inst in data.get('instances', [])]

   len(instances)
   ```

   The two `for` clauses read in the same order as the nested loop: outer first, inner second. `.get('instances', [])` is what lets the empty zone through without a `KeyError`.
9. Build the tuple list from the flattened instances:

   ```python
   fleet = [(i['name'], i['machineType'].rsplit('/', 1)[-1], i['status'])
            for data in response['items'].values()
            for i in data.get('instances', [])]

   for name, mtype, status in sorted(fleet, key=lambda t: t[1]):
       print(f'{name:<10} {mtype:<15} {status}')
   ```

   The `rsplit('/', 1)[-1]` is Lab 4, inside a comprehension.

**Checkpoint** — `inventory.py` shows four objects totalling `4639` bytes, the `logs/` prefix returns two, the delimiter listing gives `['data/', 'logs/']`, and the flattened `instances` list has four entries from the two zones that have instances.

**Stretch** — Write the flattening comprehension so it also keeps the zone, producing `(zone, name)` pairs. The zone is in the dict key (`'zones/us-east1-b'`), so you will need `.items()` and some Lab 4 string work.

**Self-check**

- Why does `listing.prefixes` come back empty if you read it before iterating?
- When should you filter with `prefix=` instead of a list comprehension?

---

[← Lab 5](lab-05-local-files-to-cloud-storage-and-back.md) · [GCP track index](../README.md) · [Paired Python track lab 6](../../python-track/labs/lab-06-lists-and-tuples.md) · [Paired AWS track lab 6](../../aws-track/labs/lab-06-lists-and-tuples-from-aws-responses.md) · [Lab 7 →](lab-07-sets-for-iam-bindings-dicts-for-labels.md)
