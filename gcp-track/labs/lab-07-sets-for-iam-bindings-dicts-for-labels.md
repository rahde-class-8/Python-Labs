## Lab 7 — Sets for IAM bindings, dicts for labels

**Pairs with Python Lab 7 (§1.10–1.11) · 30 minutes**

Goal: this is the lab where §1.10 stops being abstract. Google Cloud IAM is built from sets — members in a role, permissions in a role — and set algebra is how you reason about least privilege.

**Steps**

1. Create `policydiff.py`. A Google Cloud IAM policy is a list of **bindings**, each tying one role to a set of members:

   ```python
   # policydiff.py
   from google.cloud import storage
   from gcpmock import mock_gcs

   SA = 'serviceAccount:lab-runner@pydistilled.iam.gserviceaccount.com'

   def main():
       with mock_gcs():
           client = storage.Client(project='pydistilled')
           bucket = client.create_bucket('pydistilled-labs')

           policy = bucket.get_iam_policy(requested_policy_version=3)
           policy.bindings.append({'role': 'roles/storage.objectAdmin',
                                   'members': {SA}})
           policy.bindings.append({'role': 'roles/storage.objectViewer',
                                   'members': {'user:rahde@example.com',
                                               'group:analysts@example.com'}})
           bucket.set_iam_policy(policy)

           for binding in bucket.get_iam_policy(requested_policy_version=3).bindings:
               print(binding['role'], binding['members'])

   if __name__ == '__main__':
       main()
   ```

   Note that `members` is a Python `set`, both when you write it and when it comes back. Google's own client library models "who has this role" as a set, because order does not matter and duplicates are meaningless.
2. Ask the questions a reviewer asks, with set operations:

   ```python
   bindings = {b['role']: b['members'] for b in policy.bindings}

   viewers = bindings['roles/storage.objectViewer']
   admins = bindings['roles/storage.objectAdmin']

   viewers | admins                 # Everyone with any access
   viewers & admins                 # Anyone granted twice — set()
   'user:rahde@example.com' in viewers
   ```

   That first line turns the list of bindings into a dict of `role → members`, which is the shape every later question wants.
3. Do the least-privilege calculation. A role is a set of permissions. These are abridged — the full lists are in the IAM roles reference — but the logic is the real one:

   ```python
   ROLE_PERMISSIONS = {
       'roles/storage.objectViewer': {'storage.objects.get', 'storage.objects.list'},
       'roles/storage.objectCreator': {'storage.objects.create'},
       'roles/storage.objectAdmin': {'storage.objects.get', 'storage.objects.list',
                                     'storage.objects.create', 'storage.objects.delete',
                                     'storage.objects.update',
                                     'storage.objects.getIamPolicy',
                                     'storage.objects.setIamPolicy'},
   }

   # What the audit logs showed the service account actually using over 90 days
   USED = {'storage.objects.get', 'storage.objects.list'}

   granted = ROLE_PERMISSIONS['roles/storage.objectAdmin']

   unused = granted - USED
   print('Never used:', sorted(unused))

   missing = USED - granted
   print('Would be denied:', missing)
   ```

   `granted - USED` is over-provisioning. `USED - granted` is a broken permission. Those two lines are the whole of a least-privilege review, and they are the difference operator from §1.10.
4. Find the smallest predefined role that still covers what was used:

   ```python
   fits = [role for role, perms in ROLE_PERMISSIONS.items() if USED <= perms]
   best = min(fits, key=lambda role: len(ROLE_PERMISSIONS[role]))
   print(best)                      # roles/storage.objectViewer
   ```

   `USED <= perms` is the *subset* test: "is everything in `USED` also in `perms`?". Google Cloud's own role recommender asks the same question at scale.
5. Compare two environments for drift:

   ```python
   dev  = {'user:rahde@example.com', 'group:analysts@example.com', 'user:intern@example.com'}
   prod = {'user:rahde@example.com', 'group:analysts@example.com', SA}

   dev | prod      # Union — everyone with access somewhere
   dev & prod      # Intersection — the common baseline
   dev - prod      # In dev only — is the intern deliberate?
   prod - dev      # In prod only — dev cannot test as the service account
   dev ^ prod      # Symmetric difference — the full drift report
   ```

   `dev ^ prod` in one line is the drift report people usually build a spreadsheet for.
6. Switch to dicts. Labels are already a dictionary, on buckets and on instances alike:

   ```python
   bucket.labels = {'env': 'prod', 'owner': 'rahde', 'project': 'ace-prep'}
   bucket.patch()

   labels = client.get_bucket('pydistilled-labs').labels
   labels['env']
   labels.get('cost-center', 'unassigned')       # Missing label, with a default
   ```

   `patch()` sends only the fields you changed. If you did the AWS track, there is no list-of-dicts conversion here in either direction — Google chose the dictionary shape for the API itself. The price is stricter rules: real label keys must be lowercase, and the emulator does not check that, so a key like `CostCenter` that works here is rejected by the real service.
7. Audit label compliance with set operations on keys:

   ```python
   REQUIRED = {'env', 'owner', 'cost-center'}

   present = set(labels)            # Same as set(labels.keys())
   missing = REQUIRED - present
   extra   = present - REQUIRED

   print('missing:', missing)       # {'cost-center'}
   print('non-standard:', extra)    # {'project'}
   ```

   `set(labels)` on a dict gives its keys — the same conversion from §1.11.
8. Tabulate instances per environment with `Counter`:

   ```python
   import json
   from collections import Counter

   with open('instances.json') as f:
       instances = json.load(f)

   by_env = Counter()
   for inst in instances:
       by_env[inst.get('labels', {}).get('env', 'UNLABELLED')] += 1

   print(by_env)
   ```

   Two `.get()` calls chained: the first handles an instance with no `labels` key, the second a `labels` dict with no `env`. `Counter` needs no initialization, so the missing case is folded into the tally instead of crashing.

**Checkpoint** — `unused` has five permissions, `missing` is empty, `best` is `roles/storage.objectViewer`, and `by_env` reports `{'prod': 2, 'dev': 1, 'UNLABELLED': 1}`.

**Stretch** — Add a binding with an IAM *condition* (version 3 policies allow `'condition': {...}` on a binding) and work out why a set of members is no longer the whole picture of who can do what.

**Self-check**

- Which set operation answers "what can I safely revoke?", and which one answers "which role is big enough?"
- Why is `members` a set rather than a list?

---

[← Lab 6](lab-06-lists-and-tuples-from-cloud-listings.md) · [GCP track index](../README.md) · [Paired Python track lab 7](../../python-track/labs/lab-07-sets-and-dictionaries.md) · [Paired AWS track lab 7](../../aws-track/labs/lab-07-sets-for-iam-policy-diffing-dicts-for-tags.md) · [Lab 8 →](lab-08-iterators-as-iteration-functions-as-the-fix.md)
