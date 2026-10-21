# Python Distilled Labs

Twelve daily labs for Chapter 1 ("Python Basics") of David Beazley's *Python Distilled* (Pearson, 2021), in three parallel tracks:

- **[Python track](python-track/README.md)** works through the chapter's concepts in plain Python, using a stock portfolio as the running example.
- **[AWS track](aws-track/README.md)** applies the concepts from the Python lab with the same number to AWS through boto3. Every call runs against [moto](https://github.com/getmoto/moto), so you need no AWS account, no credentials and no spending.
- **[GCP track](gcp-track/README.md)** applies the same concepts to Google Cloud through the `google-cloud-storage` library. Cloud Storage calls run against [gcp-storage-emulator](https://github.com/oittaa/gcp-storage-emulator), and Compute Engine labs use saved API responses, so you need no Google Cloud account either.

Each lab takes 20–30 minutes. Do the Python lab first, then the AWS or GCP lab with the same number, either on the same day or as a review pass later. The two cloud tracks are independent, so you can do either one or both. Each GCP lab points out where Google made the opposite design choice from AWS.

## Repository layout

```
data/portfolio.csv     The original data file, bad GE row included. Copy it; don't edit it.
python-track/
    README.md          Setup, ground rules, coverage map
    labs/              One page per lab
    workspace/         Your code (stands in for ~/pydistilled)
aws-track/
    README.md          moto/boto3 setup and the lab template
    requirements.txt   boto3, moto
    labs/              One page per lab
    workspace/         Your code (stands in for ~/pydistilled-aws)
gcp-track/
    README.md          Emulator setup, gcpmock.py and the lab template
    requirements.txt   google-cloud-storage, gcp-storage-emulator
    data/              Saved Compute Engine responses used in Labs 2–7
    labs/              One page per lab
    workspace/         Your code (stands in for ~/pydistilled-gcp)
```

The labs refer to `~/pydistilled`, `~/pydistilled-aws` and `~/pydistilled-gcp`. Use the matching `workspace/` folder instead, so your work is saved in this repo:

```
cd python-track/workspace
cp ../../data/portfolio.csv .
```

Type every example by hand. Don't copy and paste from the lab pages.

## Progress

Commit at each checkpoint and tag it, for example `git tag python-lab-06`. Then a command like `git diff python-lab-08 python-lab-11 -- python-track/workspace/readport.py` shows how a file changed between labs.

| Day | Python track | ✓ | AWS track | ✓ | GCP track | ✓ |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | [The REPL and your first script](python-track/labs/lab-01-the-repl-and-your-first-script.md) | ☐ | [boto3 in the REPL and your first mocked script](aws-track/labs/lab-01-boto3-in-the-repl-and-your-first-mocked-script.md) | ☐ | [The client library and your first emulated script](gcp-track/labs/lab-01-the-client-library-and-your-first-emulated-script.md) | ☐ |
| 2 | [Primitives, variables, and arithmetic](python-track/labs/lab-02-primitives-variables-and-arithmetic.md) | ☐ | [AWS types and cost arithmetic](aws-track/labs/lab-02-aws-types-and-cost-arithmetic.md) | ☐ | [Cloud types and cost arithmetic](gcp-track/labs/lab-02-cloud-types-and-cost-arithmetic.md) | ☐ |
| 3 | [Conditionals and control flow](python-track/labs/lab-03-conditionals-and-control-flow.md) | ☐ | [Conditionals over AWS state](aws-track/labs/lab-03-conditionals-over-aws-state.md) | ☐ | [Conditionals over cloud state](gcp-track/labs/lab-03-conditionals-over-cloud-state.md) | ☐ |
| 4 | [Text strings and formatting](python-track/labs/lab-04-text-strings-and-formatting.md) | ☐ | [ARN and S3 key string surgery](aws-track/labs/lab-04-arn-and-s3-key-string-surgery.md) | ☐ | [Resource names, URLs and gs:// string surgery](gcp-track/labs/lab-04-resource-names-urls-and-gs-string-surgery.md) | ☐ |
| 5 | [File input and output](python-track/labs/lab-05-file-input-and-output.md) | ☐ | [Local files to S3 and back](aws-track/labs/lab-05-local-files-to-s3-and-back.md) | ☐ | [Local files to Cloud Storage and back](gcp-track/labs/lab-05-local-files-to-cloud-storage-and-back.md) | ☐ |
| 6 | [Lists and tuples](python-track/labs/lab-06-lists-and-tuples.md) | ☐ | [Lists and tuples from AWS responses](aws-track/labs/lab-06-lists-and-tuples-from-aws-responses.md) | ☐ | [Lists and tuples from cloud listings](gcp-track/labs/lab-06-lists-and-tuples-from-cloud-listings.md) | ☐ |
| 7 | [Sets and dictionaries](python-track/labs/lab-07-sets-and-dictionaries.md) | ☐ | [Sets for IAM policy diffing, dicts for tags](aws-track/labs/lab-07-sets-for-iam-policy-diffing-dicts-for-tags.md) | ☐ | [Sets for IAM bindings, dicts for labels](gcp-track/labs/lab-07-sets-for-iam-bindings-dicts-for-labels.md) | ☐ |
| 8 | [Iteration and functions](python-track/labs/lab-08-iteration-and-functions.md) | ☐ | [Paginators as iteration, functions as the fix](aws-track/labs/lab-08-paginators-as-iteration-functions-as-the-fix.md) | ☐ | [Iterators as iteration, functions as the fix](gcp-track/labs/lab-08-iterators-as-iteration-functions-as-the-fix.md) | ☐ |
| 9 | [Exceptions and program termination](python-track/labs/lab-09-exceptions-and-program-termination.md) | ☐ | [ClientError and error codes](aws-track/labs/lab-09-clienterror-and-error-codes.md) | ☐ | [API exceptions and status codes](gcp-track/labs/lab-09-api-exceptions-and-status-codes.md) | ☐ |
| 10 | [Objects and classes](python-track/labs/lab-10-objects-and-classes.md) | ☐ | [Wrapping boto3 in a class](aws-track/labs/lab-10-wrapping-boto3-in-a-class.md) | ☐ | [Wrapping the client in a class](gcp-track/labs/lab-10-wrapping-the-client-in-a-class.md) | ☐ |
| 11 | [Modules and script writing](python-track/labs/lab-11-modules-and-script-writing.md) | ☐ | [A module and a CLI](aws-track/labs/lab-11-a-module-and-a-cli.md) | ☐ | [A module and a CLI](gcp-track/labs/lab-11-a-module-and-a-cli.md) | ☐ |
| 12 | [Packages, structure, and third-party code](python-track/labs/lab-12-packages-structure-and-third-party-code.md) | ☐ | [Package it, test it, and point it at real AWS](aws-track/labs/lab-12-package-it-test-it-and-point-it-at-real-aws.md) | ☐ | [Package it, test it, and point it at real Google Cloud](gcp-track/labs/lab-12-package-it-test-it-and-point-it-at-real-google-cloud.md) | ☐ |

## Safety note

The AWS track uses the fake credentials `testing`/`testing`, which are safe to commit. Lab 12 points the code at real AWS. Keep real credentials in `~/.aws/` or in a `.env` file, both of which `.gitignore` excludes, and never put them in this repository.

The GCP track needs no credentials at all while you use the emulator. When Lab 12 points the code at a real project, use `gcloud auth application-default login`, which stores credentials in your home directory, outside this repository. Never download a service-account key file into this repository.
