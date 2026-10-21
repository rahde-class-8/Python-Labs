## Lab 6 — Lists and tuples from AWS responses

**Pairs with Python Lab 6 (§1.8–1.9) · 30 minutes**

Goal: every AWS list call returns a list of dicts. Learn to reshape those into the list-of-tuples form from the Python track, and to flatten the nested ones.

**Steps**

1. Create `inventory.py`, populate a bucket, and look at the shape you get back:

   ```python
   # inventory.py
   import boto3
   from moto import mock_aws
   
   BUCKET = 'pydistilled-labs'
   
   @mock_aws
   def main():
       s3 = boto3.client('s3', region_name='us-east-1')
       s3.create_bucket(Bucket=BUCKET)
   
       for key, body in [('data/portfolio.csv', b'AA,100,32.20\nIBM,50,91.10\n'),
                         ('data/notes.txt', b'short'),
                         ('logs/app.log', b'x' * 4096),
                         ('logs/old.log', b'y' * 512)]:
           s3.put_object(Bucket=BUCKET, Key=key, Body=body)
   
       contents = s3.list_objects_v2(Bucket=BUCKET)['Contents']
       print(type(contents), len(contents))
       print(type(contents[0]))
       print(contents[0])
   
   if __name__ == '__main__':
       main()
   ```

   `Contents` is a plain Python `list`, and each element is a plain `dict`. All the list operations from §1.8 apply directly.
2. Index and slice it as a list:

   ```python
   contents[0]['Key']
   contents[-1]['Key']
   contents[:2]
   len(contents)
   ```
3. Reshape into a list of tuples — the same structure Python Lab 6 built from a CSV:

   ```python
   inventory = [(o['Key'], o['Size']) for o in contents]
   inventory
   
   for key, size in inventory:        # Tuple unpacking in the loop
       print(f'{key:<24} {size:>8}')
   
   total = sum(size for _, size in inventory)
   print('total bytes:', total)
   ```

   The `_` throwaway variable does the same job it did on the Python track.
4. Sort by size, descending, and find the biggest object:

   ```python
   inventory.sort(key=lambda pair: pair[1], reverse=True)
   inventory[0]
   
   largest = max(contents, key=lambda o: o['Size'])
   print(largest['Key'], largest['Size'])
   ```

   `sort()` mutates and returns `None`; `sorted()` returns a new list. Same rule as §1.8.
5. Filter with a comprehension, two ways:

   ```python
   logs = [o['Key'] for o in contents if o['Key'].startswith('logs/')]
   big  = [o['Key'] for o in contents if o['Size'] > 1000]
   ```

   Then do it server-side instead, which is what you would actually do:

   ```python
   logs = s3.list_objects_v2(Bucket=BUCKET, Prefix='logs/')['Contents']
   [o['Key'] for o in logs]
   ```

   The `Prefix` argument filters before the data crosses the network. A comprehension filters after. On a bucket with a million objects, the difference is the whole ballgame.
6. Now meet a genuinely nested response. EC2 wraps instances in reservations:

   ```python
   ec2 = boto3.client('ec2', region_name='us-east-1')
   ami = ec2.describe_images()['Images'][0]['ImageId']
   
   for itype in ['t3.micro', 't3.small', 'm5.large']:
       ec2.run_instances(ImageId=ami, MinCount=1, MaxCount=1, InstanceType=itype)
   
   response = ec2.describe_instances()
   len(response['Reservations'])                      # 3 reservations
   len(response['Reservations'][0]['Instances'])      # 1 instance in the first
   ```

   A reservation is one `run_instances` call, so three separate calls give three reservations. Launching three instances in *one* call would give one reservation with three instances. Your code must handle both.
7. Flatten it. The nested loop first, then the comprehension that replaces it:

   ```python
   instances = []
   for res in response['Reservations']:
       for inst in res['Instances']:
           instances.append(inst)
   
   instances = [inst
                for res in response['Reservations']
                for inst in res['Instances']]
   
   len(instances)
   ```

   The two `for` clauses read in the same order as the nested loop: outer first, inner second. This is the single most useful comprehension in all of boto3.
8. Build the tuple list from the flattened instances:

   ```python
   fleet = [(i['InstanceId'], i['InstanceType'], i['State']['Name'])
            for res in response['Reservations']
            for i in res['Instances']]
   
   for iid, itype, state in sorted(fleet, key=lambda t: t[1]):
       print(f'{iid:<21} {itype:<10} {state}')
   ```

**Checkpoint** — `inventory.py` shows four objects totalling `4639` bytes, the `logs/` prefix returns two, and the flattened `instances` list has three entries from three reservations.

**Stretch** — Launch three instances in a single `run_instances(MinCount=3, MaxCount=3)` call and confirm the flattening comprehension still gives three.

**Self-check**

- Why does EC2 nest instances inside reservations at all?
- When should you filter with `Prefix` instead of a list comprehension?

---

[← Lab 5](lab-05-local-files-to-s3-and-back.md) · [AWS track index](../README.md) · [Paired Python track lab 6](../../python-track/labs/lab-06-lists-and-tuples.md) · [Paired GCP track lab 6](../../gcp-track/labs/lab-06-lists-and-tuples-from-cloud-listings.md) · [Lab 7 →](lab-07-sets-for-iam-policy-diffing-dicts-for-tags.md)
