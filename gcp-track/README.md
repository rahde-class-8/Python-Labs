# GCP track — the same twelve labs, on Google Cloud

*Each lab takes the Python concept from the same-numbered lab on the Python track and implements it against Google Cloud with the `google-cloud-storage` client library. Runs entirely on an emulator and saved responses — no account, no credentials, no cost.*

## How this track works

Each lab here is the Google Cloud implementation of the same-numbered lab on the Python track, and it follows the same shape as the same-numbered lab on the AWS track. Do the Python lab first. If you have also done the AWS lab, watch for the places where Google made the opposite design decision. Those contrasts are called out as they come up, and they are most of what makes a second cloud worth learning.

Cloud Storage calls run against **gcp-storage-emulator**, a small Python program that serves a fake Cloud Storage API from memory. Your code is production `google-cloud-storage` code: the same client, the same methods, the same exceptions. Nothing leaves your machine, nothing needs credentials, and nothing can cost money. Every lab starts from an empty Cloud Storage and loses everything when the `with` block ends.

Compute Engine has no emulator. For the labs that need virtual machines, `data/instances.json` and `data/aggregated.json` are saved responses in exactly the shape that `gcloud compute instances list --format=json` and the Compute Engine REST API return. You load them with `json.load` and work on them as plain Python data, which is what your code does with a real response anyway.

**Setup (once, before Lab 1):**

```
mkdir -p ~/pydistilled-gcp && cd ~/pydistilled-gcp
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
python3 -m pip install google-cloud-storage gcp-storage-emulator
```

This track needs Python 3.10 or newer, two versions above the Python track's minimum: Lab 4 uses `str.removeprefix` (3.9) and Lab 8 uses the `X | None` annotation form (3.10).

Copy `portfolio.csv` from the Python track, and `instances.json` and `aggregated.json` from this track's `data/` folder, into this directory.

Then type in `gcpmock.py`. Every lab imports it:

```python
# gcpmock.py
#
# Runs a fake Cloud Storage server in memory for the length of a with block.

import os
from contextlib import contextmanager
from gcp_storage_emulator.server import create_server

HOST = 'localhost'
PORT = 9023

@contextmanager
def mock_gcs():
    server = create_server(HOST, PORT, in_memory=True)
    server.start()
    os.environ['STORAGE_EMULATOR_HOST'] = f'http://{HOST}:{PORT}'
    try:
        yield server
    finally:
        server.stop()
        del os.environ['STORAGE_EMULATOR_HOST']
```

You do not need to understand every line yet. It starts the emulator, sets the `STORAGE_EMULATOR_HOST` environment variable that `google-cloud-storage` checks when you create a client, and undoes both when the block ends. The `try`/`finally` inside it is Lab 9 material, and Lab 12 explains why it lives in its own file.

**The shape every lab uses:**

```python
from google.cloud import storage
from gcpmock import mock_gcs

def main():
    with mock_gcs():
        client = storage.Client(project='pydistilled')
        ...

if __name__ == '__main__':
    main()
```

Everything Google Cloud must happen inside the `with mock_gcs():` block. A client created outside it looks for real credentials and either fails or talks to your real account, which is exactly the bug you want to notice early.

The emulator prints `Resource not found:` and the missing object's name whenever a lookup fails. That is the emulator logging, not your code. Ignore it.

**Honest scope:** the emulator gives you the API surface, not the system. You will practice the client library, object metadata, iterators, exception classes, and IAM policy *documents*. Those are the parts the Cloud Digital Leader and Associate Cloud Engineer exams lean on. You will not practice latency, real IAM evaluation, bucket-name and label validation, server-side pagination, network paths, or billing. Lab 8 and Lab 12 say exactly where the emulator differs from the real service.

## Labs

| Lab | Title | Paired Python lab | Paired AWS lab |
| --- | --- | --- | --- |
| 1 | [The client library and your first emulated script](labs/lab-01-the-client-library-and-your-first-emulated-script.md) | [The REPL and your first script](../python-track/labs/lab-01-the-repl-and-your-first-script.md) | [boto3 in the REPL and your first mocked script](../aws-track/labs/lab-01-boto3-in-the-repl-and-your-first-mocked-script.md) |
| 2 | [Cloud types and cost arithmetic](labs/lab-02-cloud-types-and-cost-arithmetic.md) | [Primitives, variables, and arithmetic](../python-track/labs/lab-02-primitives-variables-and-arithmetic.md) | [AWS types and cost arithmetic](../aws-track/labs/lab-02-aws-types-and-cost-arithmetic.md) |
| 3 | [Conditionals over cloud state](labs/lab-03-conditionals-over-cloud-state.md) | [Conditionals and control flow](../python-track/labs/lab-03-conditionals-and-control-flow.md) | [Conditionals over AWS state](../aws-track/labs/lab-03-conditionals-over-aws-state.md) |
| 4 | [Resource names, URLs and gs:// string surgery](labs/lab-04-resource-names-urls-and-gs-string-surgery.md) | [Text strings and formatting](../python-track/labs/lab-04-text-strings-and-formatting.md) | [ARN and S3 key string surgery](../aws-track/labs/lab-04-arn-and-s3-key-string-surgery.md) |
| 5 | [Local files to Cloud Storage and back](labs/lab-05-local-files-to-cloud-storage-and-back.md) | [File input and output](../python-track/labs/lab-05-file-input-and-output.md) | [Local files to S3 and back](../aws-track/labs/lab-05-local-files-to-s3-and-back.md) |
| 6 | [Lists and tuples from cloud listings](labs/lab-06-lists-and-tuples-from-cloud-listings.md) | [Lists and tuples](../python-track/labs/lab-06-lists-and-tuples.md) | [Lists and tuples from AWS responses](../aws-track/labs/lab-06-lists-and-tuples-from-aws-responses.md) |
| 7 | [Sets for IAM bindings, dicts for labels](labs/lab-07-sets-for-iam-bindings-dicts-for-labels.md) | [Sets and dictionaries](../python-track/labs/lab-07-sets-and-dictionaries.md) | [Sets for IAM policy diffing, dicts for tags](../aws-track/labs/lab-07-sets-for-iam-policy-diffing-dicts-for-tags.md) |
| 8 | [Iterators as iteration, functions as the fix](labs/lab-08-iterators-as-iteration-functions-as-the-fix.md) | [Iteration and functions](../python-track/labs/lab-08-iteration-and-functions.md) | [Paginators as iteration, functions as the fix](../aws-track/labs/lab-08-paginators-as-iteration-functions-as-the-fix.md) |
| 9 | [API exceptions and status codes](labs/lab-09-api-exceptions-and-status-codes.md) | [Exceptions and program termination](../python-track/labs/lab-09-exceptions-and-program-termination.md) | [ClientError and error codes](../aws-track/labs/lab-09-clienterror-and-error-codes.md) |
| 10 | [Wrapping the client in a class](labs/lab-10-wrapping-the-client-in-a-class.md) | [Objects and classes](../python-track/labs/lab-10-objects-and-classes.md) | [Wrapping boto3 in a class](../aws-track/labs/lab-10-wrapping-boto3-in-a-class.md) |
| 11 | [A module and a CLI](labs/lab-11-a-module-and-a-cli.md) | [Modules and script writing](../python-track/labs/lab-11-modules-and-script-writing.md) | [A module and a CLI](../aws-track/labs/lab-11-a-module-and-a-cli.md) |
| 12 | [Package it, test it, and point it at real Google Cloud](labs/lab-12-package-it-test-it-and-point-it-at-real-google-cloud.md) | [Packages, structure, and third-party code](../python-track/labs/lab-12-packages-structure-and-third-party-code.md) | [Package it, test it, and point it at real AWS](../aws-track/labs/lab-12-package-it-test-it-and-point-it-at-real-aws.md) |

## What each lab practices

| Lab | Chapter sections | Google Cloud services | Key APIs |
| --- | --- | --- | --- |
| 1 | 1.1–1.2 | Cloud Storage | `storage.Client`, `create_bucket`, `bucket` vs `get_bucket` |
| 2 | 1.3–1.4 | Cloud Storage, Compute Engine | blob attributes, custom `metadata`, 64-bit IDs as strings |
| 3 | 1.5 | Cloud Storage, Compute Engine | `get_blob`, `lookup_bucket`, instance `status` |
| 4 | 1.6 | — (string work) | `gs://` URIs, resource names, `selfLink` URLs |
| 5 | 1.7 | Cloud Storage | `upload_from_*`, `download_as_*`, `blob.open` |
| 6 | 1.8–1.9 | Cloud Storage, Compute Engine | `list_blobs` with `prefix` and `delimiter`, aggregated lists |
| 7 | 1.10–1.11 | IAM, Cloud Storage | `get_iam_policy`, `set_iam_policy`, labels |
| 8 | 1.12–1.13 | Cloud Storage | `HTTPIterator`, `.pages`, `page_size` |
| 9 | 1.14–1.15 | Cloud Storage | `NotFound`, `Conflict`, `Forbidden`, `delete(force=True)` |
| 10 | 1.16 | Cloud Storage | client composition, `__len__`, `__contains__`, `__repr__` |
| 11 | 1.17–1.18 | Cloud Storage | `csv` over `blob.open('r')` |
| 12 | 1.19–1.22 | Cloud Storage, IAM | `unittest` + `mock_gcs`, policy bindings |

**Where this helps with the exams**

Labs 4, 7 and 12 carry directly into Associate Cloud Engineer material: resource names and service-account identities, IAM bindings and predefined roles, and least privilege as a set difference and a subset test. Labs 3, 8 and 9 teach the operational reflexes — missing fields, stopped-but-billed instances, which errors are retryable — that the exams ask about obliquely and real work asks about constantly.

**What the emulator cannot teach you**

IAM policies are *stored* here, never *evaluated*. A policy that would deny you in production succeeds under the emulator, so these labs cannot verify that a policy is correct — only that your code builds and reads one. The same goes for VPC reachability, organization policies, encryption settings and quotas. For those, use a real project with the free trial or free tier, and treat the policy file from Lab 12 as a draft to test there.

Everything else — client-library call shapes, blob attributes, iterators, exception classes, the `bytes`/`str` boundary — behaves the same way here as in production, which is most of what makes cloud code hard to write.
