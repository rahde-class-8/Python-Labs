## Lab 3 — Conditionals over AWS state

**Pairs with Python Lab 3 (§1.5) · 25 minutes**

Goal: branch on AWS responses, and learn the single most common boto3 bug — which is a truthiness bug.

**Steps**

1. Meet the bug first. Create `empty.py`:

   ```python
   # empty.py
   import boto3
   from moto import mock_aws
   
   @mock_aws
   def main():
       s3 = boto3.client('s3', region_name='us-east-1')
       s3.create_bucket(Bucket='pydistilled-labs')
   
       response = s3.list_objects_v2(Bucket='pydistilled-labs')
       print(response.keys())
       for obj in response['Contents']:        # KeyError
           print(obj['Key'])
   
   if __name__ == '__main__':
       main()
   ```

   It raises `KeyError: 'Contents'`. An empty bucket does not return an empty list — it omits the key entirely. Code that works in testing breaks the first time a bucket is empty.
2. Fix it three ways and compare:

   ```python
   if 'Contents' in response:               # Explicit membership test
       for obj in response['Contents']:
           print(obj['Key'])
   
   for obj in response.get('Contents', []):  # Idiomatic — use this
       print(obj['Key'])
   
   if response.get('KeyCount'):              # Truthiness on the count
       ...
   ```

   `.get('Contents', [])` is the form to internalize. An empty list is falsy, so the loop simply does not run.
3. Confirm the truthiness rules on real AWS shapes:

   ```python
   for value in [[], {}, '', 0, response.get('Contents'), response.get('KeyCount')]:
       print(repr(value), '->', bool(value))
   ```

   Note that `response.get('Contents')` returns `None` when absent, and `None` is falsy — which is why the `.get()` form is safe even without the default.
4. Branch on EC2 instance state with a full `if`/`elif`/`else` chain. Create `triage.py`:

   ```python
   # triage.py
   import boto3
   from moto import mock_aws
   
   @mock_aws
   def main():
       ec2 = boto3.client('ec2', region_name='us-east-1')
       ami = ec2.describe_images()['Images'][0]['ImageId']
   
       for itype, env in [('t3.micro', 'prod'), ('t3.small', 'dev'),
                          ('m5.large', 'prod'), ('t3.nano', None)]:
           tags = [{'Key': 'Env', 'Value': env}] if env else []
           ec2.run_instances(
               ImageId=ami, MinCount=1, MaxCount=1, InstanceType=itype,
               TagSpecifications=[{'ResourceType': 'instance', 'Tags': tags}] if tags else [])
   
       for res in ec2.describe_instances()['Reservations']:
           for inst in res['Instances']:
               state = inst['State']['Name']
               if state == 'running':
                   verdict = 'billing now'
               elif state == 'stopped':
                   verdict = 'storage only'
               elif state == 'terminated':
                   verdict = 'free'
               else:
                   verdict = f'unexpected state {state!r}'
               print(f"{inst['InstanceType']:<10} {state:<12} {verdict}")
   
   if __name__ == '__main__':
       main()
   ```

   Note the conditional expression in `tags = [...] if env else []` — the same form you met on the Python track.
5. Add a tag-compliance scan using `continue` to skip what you do not care about:

   ```python
   REQUIRED = 'Env'
   
   for res in ec2.describe_instances()['Reservations']:
       for inst in res['Instances']:
           tags = {t['Key']: t['Value'] for t in inst.get('Tags', [])}
           if REQUIRED in tags:
               continue                      # Compliant — nothing to report
           print('MISSING TAG:', inst['InstanceId'], inst['InstanceType'])
   ```

   Note `inst.get('Tags', [])` — the same missing-key problem as `Contents`. Untagged instances have no `Tags` key at all.
6. Use `break` to stop at the first problem, for a fail-fast check:

   ```python
   first_bad = None
   for res in ec2.describe_instances()['Reservations']:
       for inst in res['Instances']:
           if not inst.get('Tags'):
               first_bad = inst['InstanceId']
               break
       if first_bad:
           break
   
   if first_bad:
       raise SystemExit(f'Untagged instance found: {first_bad}')
   print('All tagged')
   ```

   Note that `break` only leaves one loop. Nested loops need the second check — Lab 8 replaces this whole shape with a flattening comprehension.

**Checkpoint** — `empty.py` raises `KeyError` before your fix and prints nothing after it; `triage.py` lists four instances as `running` / `billing now` and flags exactly one untagged instance.

**Stretch** — Stop one instance with `ec2.stop_instances(InstanceIds=[...])` and rerun `triage.py` to exercise the `stopped` branch.

**Self-check**

- Why is `.get('Contents', [])` safer than `if 'Contents' in response`?
- Which AWS response keys have you now seen disappear when empty?

---

[← Lab 2](lab-02-aws-types-and-cost-arithmetic.md) · [AWS track index](../README.md) · [Paired Python track lab 3](../../python-track/labs/lab-03-conditionals-and-control-flow.md) · [Lab 4 →](lab-04-arn-and-s3-key-string-surgery.md)
