# Python Distilled — Chapter 1 Daily Lab Curriculum

Oct 19, 2026 · @Rahde jones

*Beazley, *Python Distilled* (Pearson, 2021) — Chapter 1, "Python Basics," sections 1.1–1.22. Twelve daily labs, each designed to run in under 30 minutes.*

## How to use this

Twelve labs, one per day, 20–30 minutes each. Every lab is self-contained and typed by hand — no copy-paste. The whole chapter is covered in order, and a single running example (a stock portfolio) threads through from Lab 5 onward, so each day builds on files you already have.

**Daily rhythm (25 minutes):**

1. Read the chapter sections listed at the top of the lab — 5 minutes.
2. Work the lab steps in a terminal and a plain text editor — 15 minutes.
3. Run the checkpoint and answer the self-check questions out loud — 5 minutes.

**Setup (do this once, before Lab 1):**

```
mkdir -p ~/pydistilled && cd ~/pydistilled
python3 --version    # need 3.8 or newer
```

Everything you write lives in `~/pydistilled`. Keep the directory for all twelve days; later labs import files from earlier ones.

**Ground rules:**

- Use a terminal and a basic text editor, not an IDE. Beazley's point in §1.1 is that the interpreter is the thing you are learning, and an IDE hides it.
- Type every example. Typos are part of the lab — Lab 9 is about reading the tracebacks they produce.
- If a lab runs past 30 minutes, stop where you are and note the step number. Resume there the next day and shift the rest back.
- Do not skip the **Stretch** items only because they are optional; skip them only when you are out of time.

## Labs

| Lab | Title | Paired lab |
| --- | --- | --- |
| 1 | [The REPL and your first script](labs/lab-01-the-repl-and-your-first-script.md) | [boto3 in the REPL and your first mocked script](../aws-track/labs/lab-01-boto3-in-the-repl-and-your-first-mocked-script.md) |
| 2 | [Primitives, variables, and arithmetic](labs/lab-02-primitives-variables-and-arithmetic.md) | [AWS types and cost arithmetic](../aws-track/labs/lab-02-aws-types-and-cost-arithmetic.md) |
| 3 | [Conditionals and control flow](labs/lab-03-conditionals-and-control-flow.md) | [Conditionals over AWS state](../aws-track/labs/lab-03-conditionals-over-aws-state.md) |
| 4 | [Text strings and formatting](labs/lab-04-text-strings-and-formatting.md) | [ARN and S3 key string surgery](../aws-track/labs/lab-04-arn-and-s3-key-string-surgery.md) |
| 5 | [File input and output](labs/lab-05-file-input-and-output.md) | [Local files to S3 and back](../aws-track/labs/lab-05-local-files-to-s3-and-back.md) |
| 6 | [Lists and tuples](labs/lab-06-lists-and-tuples.md) | [Lists and tuples from AWS responses](../aws-track/labs/lab-06-lists-and-tuples-from-aws-responses.md) |
| 7 | [Sets and dictionaries](labs/lab-07-sets-and-dictionaries.md) | [Sets for IAM policy diffing, dicts for tags](../aws-track/labs/lab-07-sets-for-iam-policy-diffing-dicts-for-tags.md) |
| 8 | [Iteration and functions](labs/lab-08-iteration-and-functions.md) | [Paginators as iteration, functions as the fix](../aws-track/labs/lab-08-paginators-as-iteration-functions-as-the-fix.md) |
| 9 | [Exceptions and program termination](labs/lab-09-exceptions-and-program-termination.md) | [ClientError and error codes](../aws-track/labs/lab-09-clienterror-and-error-codes.md) |
| 10 | [Objects and classes](labs/lab-10-objects-and-classes.md) | [Wrapping boto3 in a class](../aws-track/labs/lab-10-wrapping-boto3-in-a-class.md) |
| 11 | [Modules and script writing](labs/lab-11-modules-and-script-writing.md) | [A module and a CLI](../aws-track/labs/lab-11-a-module-and-a-cli.md) |
| 12 | [Packages, structure, and third-party code](labs/lab-12-packages-structure-and-third-party-code.md) | [Package it, test it, and point it at real AWS](../aws-track/labs/lab-12-package-it-test-it-and-point-it-at-real-aws.md) |

## Coverage map

Every section of Chapter 1 is covered exactly once.

| Section | Title | Lab |
| --- | --- | --- |
| 1.1 | Running Python | 1 |
| 1.2 | Python Programs | 1 |
| 1.3 | Primitives, Variables, and Expressions | 2 |
| 1.4 | Arithmetic Operators | 2 |
| 1.5 | Conditionals and Control Flow | 3 |
| 1.6 | Text Strings | 4 |
| 1.7 | File Input and Output | 5 |
| 1.8 | Lists | 6 |
| 1.9 | Tuples | 6 |
| 1.10 | Sets | 7 |
| 1.11 | Dictionaries | 7 |
| 1.12 | Iteration and Looping | 8 |
| 1.13 | Functions | 8 |
| 1.14 | Exceptions | 9 |
| 1.15 | Program Termination | 9 |
| 1.16 | Objects and Classes | 10 |
| 1.17 | Modules | 11 |
| 1.18 | Script Writing | 11 |
| 1.19 | Packages | 12 |
| 1.20 | Structuring an Application | 12 |
| 1.21 | Managing Third-Party Packages | 12 |
| 1.22 | Python: It Fits Your Brain | 12 |

**After Chapter 1**

The chapter deliberately leaves things half-explained and points forward. If you want to follow a thread rather than read straight on: scoping rules go deeper in Chapter 5, string formatting in Chapter 9, the `with` statement and custom exceptions in Chapter 3, and special methods such as `__repr__` and `__len__` in Chapter 4. Packaging picks up again in Chapter 8.

Keep `~/tutorial-project` — later chapters extend the same portfolio code.
