## Lab 7 — Sets for IAM policy diffing, dicts for tags

**Pairs with Python Lab 7 (§1.10–1.11) · 30 minutes**

Goal: this is the lab where §1.10 stops being abstract. Set algebra *is* how you reason about least privilege, and it maps straight onto SEIR-1 and SAA material.

**Steps**

1. Create `policydiff.py` with two policies — what a role was granted, and what it actually used:

   ```python
   # policydiff.py
   import boto3, json
   from moto import mock_aws
   
   GRANTED = {
       'Version': '2012-10-17',
       'Statement': [{
           'Effect': 'Allow',
           'Action': ['s3:GetObject', 's3:PutObject', 's3:DeleteObject',
                      's3:ListBucket', 's3:PutBucketPolicy'],
           'Resource': 'arn:aws:s3:::pydistilled-labs/*'}]}
   
   # What CloudTrail showed the role actually calling over 90 days
   USED = {'s3:GetObject', 's3:ListBucket'}
   
   @mock_aws
   def main():
       iam = boto3.client('iam')
       policy = iam.create_policy(PolicyName='LabAccess',
                                  PolicyDocument=json.dumps(GRANTED))
       arn = policy['Policy']['Arn']
       print('created', arn)
   
       meta = iam.get_policy(PolicyArn=arn)['Policy']
       doc = iam.get_policy_version(
           PolicyArn=arn,
           VersionId=meta['DefaultVersionId'])['PolicyVersion']['Document']
   
       granted = set(doc['Statement'][0]['Action'])
       print('granted:', granted)
   
   if __name__ == '__main__':
       main()
   ```

   Note that the policy document comes back as a parsed `dict`, not the JSON string you sent. The actions are a plain list, so `set()` takes it directly.
2. Do the least-privilege calculation with one set operation:

   ```python
   unused = granted - USED
   print('REVOKE these:', unused)
   
   missing = USED - granted
   print('Calls that would be denied:', missing)
   
   keep = granted & USED
   print('Keep:', keep)
   ```

   `granted - USED` is over-provisioning. `USED - granted` is a broken permission. Those two lines are the whole of a least-privilege review, and they are the difference operator from §1.10.
3. Write the tightened policy back and confirm it shrank:

   ```python
   tightened = {
       'Version': '2012-10-17',
       'Statement': [{
           'Effect': 'Allow',
           'Action': sorted(keep),
           'Resource': 'arn:aws:s3:::pydistilled-labs/*'}]}
   
   print(json.dumps(tightened, indent=2))
   ```

   `sorted(keep)` converts the set back to a list — sets have no order, and a policy document needs something JSON-serializable and stable for diffing.
4. Compare two roles for drift:

   ```python
   dev  = {'s3:GetObject', 's3:PutObject', 's3:ListBucket'}
   prod = {'s3:GetObject', 's3:ListBucket', 'kms:Decrypt'}
   
   dev | prod      # Union — everything either role can do
   dev & prod      # Intersection — the common baseline
   dev - prod      # In dev only — is PutObject deliberate?
   prod - dev      # In prod only — dev cannot test KMS paths
   dev ^ prod      # Symmetric difference — the full drift report
   ```

   `dev ^ prod` in one line is the environment-drift report people usually build a spreadsheet for.
5. Switch to dicts. AWS tags arrive as a list of dicts, which is awkward — convert them:

   ```python
   tag_list = [{'Key': 'Env', 'Value': 'prod'},
               {'Key': 'Owner', 'Value': 'rahde'},
               {'Key': 'Project', 'Value': 'seir1'}]
   
   tags = {t['Key']: t['Value'] for t in tag_list}
   tags['Env']
   tags.get('CostCenter', 'unassigned')      # Missing tag, with a default
   ```

   That dict comprehension is the first thing to write after any `describe_*` call that returns tags.
6. Convert back, because that is what the API wants when you write:

   ```python
   tag_list = [{'Key': k, 'Value': v} for k, v in tags.items()]
   ```

   List of dicts to dict and back. You will write both directions constantly.
7. Audit tag compliance with set operations on keys:

   ```python
   REQUIRED = {'Env', 'Owner', 'CostCenter'}
   
   present = set(tags)              # Same as set(tags.keys())
   missing = REQUIRED - present
   extra   = present - REQUIRED
   
   print('missing:', missing)       # {'CostCenter'}
   print('non-standard:', extra)    # {'Project'}
   ```

   `set(tags)` on a dict gives its keys — the same conversion from §1.11.
8. Tabulate instances per environment with `Counter`:

   ```python
   from collections import Counter
   
   ec2 = boto3.client('ec2', region_name='us-east-1')
   ami = ec2.describe_images()['Images'][0]['ImageId']
   for env in ['prod', 'dev', 'prod', None]:
       spec = ([{'ResourceType': 'instance',
                 'Tags': [{'Key': 'Env', 'Value': env}]}] if env else [])
       ec2.run_instances(ImageId=ami, MinCount=1, MaxCount=1,
                         InstanceType='t3.micro', TagSpecifications=spec)
   
   by_env = Counter()
   for res in ec2.describe_instances()['Reservations']:
       for inst in res['Instances']:
           t = {x['Key']: x['Value'] for x in inst.get('Tags', [])}
           by_env[t.get('Env', 'UNTAGGED')] += 1
   
   print(by_env)
   ```

   `Counter` needs no initialization and `t.get('Env', 'UNTAGGED')` folds the missing-tag case into the tally instead of crashing.

**Checkpoint** — `unused` is `{'s3:PutObject', 's3:DeleteObject', 's3:PutBucketPolicy'}`, `missing` is empty, and `by_env` reports `{'prod': 2, 'dev': 1, 'UNTAGGED': 1}`.

**Stretch** — Add a second statement to `GRANTED` with a `Deny` effect and work out why `set(doc['Statement'][0]['Action'])` is now not the whole picture.

**Self-check**

- Which set operation answers "what can I safely revoke?"
- Why does AWS return tags as a list of dicts rather than a dict?

---

[← Lab 6](lab-06-lists-and-tuples-from-aws-responses.md) · [AWS track index](../README.md) · [Paired Python track lab 7](../../python-track/labs/lab-07-sets-and-dictionaries.md) · [Lab 8 →](lab-08-paginators-as-iteration-functions-as-the-fix.md)
