# AWS track — the same twelve labs, applied

Oct 19, 2026 · @Rahde jones

*Each lab takes the Python concept from the same-numbered lab on the Python track and implements it against AWS with boto3. Runs entirely on mocked AWS — no account, no credentials, no cost.*

## How this track works

Each lab here is the AWS implementation of the same-numbered lab on the Python track. Lab 6 there builds a list of tuples from a CSV file; Lab 6 here builds one from an S3 `list_objects_v2` response. Do them on the same day, Python first, or run this track second as a review pass — either works, but the AWS lab assumes you have already met the Python concept.

All AWS calls run against **moto**, which intercepts boto3 at the HTTP layer and serves a fake AWS in memory. Your code is production boto3 — the same clients, the same parameters, the same exceptions — but nothing leaves your machine, nothing needs credentials, and nothing can cost money. Each lab resets to an empty AWS when the process exits.

**Setup (once, before Lab 1):**

```
mkdir -p ~/pydistilled-aws && cd ~/pydistilled-aws
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
python3 -m pip install boto3 moto
```

Then set fake credentials, so boto3 never reaches for a real profile:

```
export AWS_ACCESS_KEY_ID=testing
export AWS_SECRET_ACCESS_KEY=testing
export AWS_DEFAULT_REGION=us-east-1
```

Copy `portfolio.csv` from the Python track into this directory — it is still the data under every lab.

**The shape every lab uses:**

```python
import boto3
from moto import mock_aws

@mock_aws
def main():
    s3 = boto3.client('s3', region_name='us-east-1')
    ...

if __name__ == '__main__':
    main()
```

Everything AWS must happen inside the `@mock_aws` function. A client created outside it talks to the real AWS, which is exactly the bug you want to notice early.

**Honest scope:** moto gives you the API surface, not the system. You will practice boto3, response shapes, pagination, error codes and IAM policy *documents* — all of which show up on the CCP and SAA exams. You will not practice latency, eventual consistency, real IAM evaluation, network paths, or billing. Lab 12 covers what changes when you point the same code at a real account.

## Labs

| Lab | Title | Paired lab |
| --- | --- | --- |
| 1 | [boto3 in the REPL and your first mocked script](labs/lab-01-boto3-in-the-repl-and-your-first-mocked-script.md) | [The REPL and your first script](../python-track/labs/lab-01-the-repl-and-your-first-script.md) |
| 2 | [AWS types and cost arithmetic](labs/lab-02-aws-types-and-cost-arithmetic.md) | [Primitives, variables, and arithmetic](../python-track/labs/lab-02-primitives-variables-and-arithmetic.md) |
| 3 | [Conditionals over AWS state](labs/lab-03-conditionals-over-aws-state.md) | [Conditionals and control flow](../python-track/labs/lab-03-conditionals-and-control-flow.md) |
| 4 | [ARN and S3 key string surgery](labs/lab-04-arn-and-s3-key-string-surgery.md) | [Text strings and formatting](../python-track/labs/lab-04-text-strings-and-formatting.md) |
| 5 | [Local files to S3 and back](labs/lab-05-local-files-to-s3-and-back.md) | [File input and output](../python-track/labs/lab-05-file-input-and-output.md) |
| 6 | [Lists and tuples from AWS responses](labs/lab-06-lists-and-tuples-from-aws-responses.md) | [Lists and tuples](../python-track/labs/lab-06-lists-and-tuples.md) |
| 7 | [Sets for IAM policy diffing, dicts for tags](labs/lab-07-sets-for-iam-policy-diffing-dicts-for-tags.md) | [Sets and dictionaries](../python-track/labs/lab-07-sets-and-dictionaries.md) |
| 8 | [Paginators as iteration, functions as the fix](labs/lab-08-paginators-as-iteration-functions-as-the-fix.md) | [Iteration and functions](../python-track/labs/lab-08-iteration-and-functions.md) |
| 9 | [ClientError and error codes](labs/lab-09-clienterror-and-error-codes.md) | [Exceptions and program termination](../python-track/labs/lab-09-exceptions-and-program-termination.md) |
| 10 | [Wrapping boto3 in a class](labs/lab-10-wrapping-boto3-in-a-class.md) | [Objects and classes](../python-track/labs/lab-10-objects-and-classes.md) |
| 11 | [A module and a CLI](labs/lab-11-a-module-and-a-cli.md) | [Modules and script writing](../python-track/labs/lab-11-modules-and-script-writing.md) |
| 12 | [Package it, test it, and point it at real AWS](labs/lab-12-package-it-test-it-and-point-it-at-real-aws.md) | [Packages, structure, and third-party code](../python-track/labs/lab-12-packages-structure-and-third-party-code.md) |

## What each lab practices

| Lab | Chapter sections | AWS services | Key APIs |
| --- | --- | --- | --- |
| 1 | 1.1–1.2 | STS, S3 | `get_caller_identity`, `mock_aws` |
| 2 | 1.3–1.4 | S3, DynamoDB | `list_objects_v2`, `put_item`, `get_item` |
| 3 | 1.5 | S3, EC2 | `list_objects_v2`, `describe_instances` |
| 4 | 1.6 | — (string work) | ARN and key parsing |
| 5 | 1.7 | S3 | `upload_file`, `put_object`, `get_object` |
| 6 | 1.8–1.9 | S3, EC2 | `list_objects_v2` with `Prefix`, `run_instances` |
| 7 | 1.10–1.11 | IAM, EC2 | `create_policy`, `get_policy_version` |
| 8 | 1.12–1.13 | S3 | `get_paginator`, `paginate` |
| 9 | 1.14–1.15 | S3, DynamoDB | `ClientError`, `delete_object`, `delete_bucket` |
| 10 | 1.16 | S3 | client composition, `__len__`, `__repr__` |
| 11 | 1.17–1.18 | S3 | `csv` + `io.StringIO` over `get_object` |
| 12 | 1.19–1.22 | S3, IAM | `unittest` + `mock_aws`, policy documents |

**Where this helps with the exams**

Labs 4, 7 and 12 are the ones that carry directly into SAA and SEIR-1 material: ARN structure, the object-versus-bucket Resource distinction, and least privilege as a set difference. Labs 3, 8 and 9 teach the operational reflexes — missing keys, truncated responses, which errors are retryable — that the exams ask about obliquely and real work asks about constantly.

**What moto cannot teach you**

IAM policies are *stored* here, never *evaluated*. A policy that would deny you in production succeeds under moto, so these labs cannot verify a policy is correct — only that your code builds and parses one. The same goes for VPC reachability, cross-account trust, encryption enforcement and service quotas. For those, use the real console once you have a free-tier account, and treat the policy files from Lab 12 as drafts to test there.

Everything else — boto3 call shapes, response structures, pagination, error codes, the `bytes`/`str` boundary — behaves the same way here as in production, which is most of what makes AWS code hard to write.
