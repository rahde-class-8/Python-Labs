## Lab 12 — Package it, test it, and point it at real AWS

**Pairs with Python Lab 12 (§1.19–1.22) · 30 minutes**

Goal: package the AWS code properly, write a real test against the mock, and understand exactly what changes when the target is a live account.

**Steps**

1. Build the package and project layout:

   ```
   cd ~
   mkdir -p awstool-project/{awstool,tests,examples,policies}
   cd awstool-project
   touch awstool/__init__.py
   mv ~/pydistilled-aws/awsport.py awstool/
   mv ~/pydistilled-aws/portfolio_bucket.py awstool/
   cp ~/pydistilled-aws/portfolio.csv examples/
   ```

   You should have:

   ```
   awstool-project/
       awstool/
           __init__.py
           awsport.py
           portfolio_bucket.py
       tests/
       examples/
           portfolio.csv
       policies/
   ```
2. Fix the intra-package import with the relative form from §1.19:

   ```python
   # awstool/report.py
   from . import awsport
   from .portfolio_bucket import PortfolioBucket
   
   def summary(s3, bucket, key):
       holdings = awsport.read_portfolio(s3, bucket, key)
       return {
           'holdings': len(holdings),
           'total': sum(s * p for _, s, p in holdings),
       }
   ```

   `from . import awsport` does not name the package, so renaming `awstool` later breaks nothing.
3. Export a clean public surface from `__init__.py`:

   ```python
   # awstool/__init__.py
   from .awsport import read_portfolio, portfolio_cost
   from .portfolio_bucket import PortfolioBucket
   
   __all__ = ['read_portfolio', 'portfolio_cost', 'PortfolioBucket']
   ```

   Now callers write `from awstool import read_portfolio` without knowing which module it lives in — you are free to reorganize internals later.
4. Write a real test. This is where the mocking design from Lab 11 pays off:

   ```python
   # tests/test_awsport.py
   import unittest
   import boto3
   from moto import mock_aws
   
   from awstool import read_portfolio, portfolio_cost
   
   BUCKET = 'test-bucket'
   KEY = 'portfolio.csv'
   DATA = (b'AA,100,32.20\n'
           b'IBM,50,91.10\n'
           b'GE,95,N/A\n')
   
   class TestReadPortfolio(unittest.TestCase):
   
       @mock_aws
       def test_skips_bad_rows(self):
           s3 = boto3.client('s3', region_name='us-east-1')
           s3.create_bucket(Bucket=BUCKET)
           s3.put_object(Bucket=BUCKET, Key=KEY, Body=DATA)
   
           holdings = read_portfolio(s3, BUCKET, KEY)
           self.assertEqual(len(holdings), 2)
           self.assertEqual(holdings[0], ('AA', 100, 32.20))
   
       @mock_aws
       def test_total(self):
           s3 = boto3.client('s3', region_name='us-east-1')
           s3.create_bucket(Bucket=BUCKET)
           s3.put_object(Bucket=BUCKET, Key=KEY, Body=DATA)
   
           self.assertAlmostEqual(portfolio_cost(s3, BUCKET, KEY), 7775.0)
   
       @mock_aws
       def test_missing_key_exits(self):
           s3 = boto3.client('s3', region_name='us-east-1')
           s3.create_bucket(Bucket=BUCKET)
   
           with self.assertRaises(SystemExit):
               read_portfolio(s3, BUCKET, 'nope.csv')
   
   if __name__ == '__main__':
       unittest.main()
   ```

   Run it from the project root:

   ```
   python3 -m unittest discover tests -v
   ```

   Three tests, no AWS account, under a second. Each gets a clean empty AWS because `@mock_aws` resets per test.
5. Pin the dependencies:

   ```
   python3 -m venv venv
   source venv/bin/activate
   python3 -m pip install boto3 moto
   python3 -m pip freeze > requirements.txt
   grep -E '^(boto3|moto|botocore)' requirements.txt
   ```

   Then check where an import actually comes from, the §1.21 move:

   ```python
   import boto3, moto
   boto3.__file__
   moto.__file__
   ```

   Both now point inside `venv/`, not at the system Python. `boto3` belongs in `requirements.txt`; `moto` is a test-only dependency, so in a real project it goes in a separate dev requirements file.
6. Write the least-privilege policy as package data, using what Lab 7 computed:

   ```json
   {
     "Version": "2012-10-17",
     "Statement": [
       {
         "Sid": "ReadPortfolioObjects",
         "Effect": "Allow",
         "Action": ["s3:GetObject"],
         "Resource": "arn:aws:s3:::pydistilled-labs/*"
       },
       {
         "Sid": "ListBucketOnly",
         "Effect": "Allow",
         "Action": ["s3:ListBucket"],
         "Resource": "arn:aws:s3:::pydistilled-labs"
       }
     ]
   }
   ```

   Save as `policies/read-portfolio.json`. Note the two statements: `s3:GetObject` acts on objects (`/*`), `s3:ListBucket` acts on the bucket itself (no `/*`). That distinction is Lab 4's ARN lesson, and getting it wrong is the most common IAM policy error there is.
7. Now the real-account question. What changes, and what does not:

   | Concern | Under moto | Against real AWS |
   | --- | --- | --- |
   | Your code | unchanged | unchanged |
   | Credentials | fake env vars | a profile or IAM role |
   | `region_name` | ignored | decides latency, cost and data residency |
   | IAM policy | not evaluated | enforced — `AccessDenied` becomes real |
   | Bucket names | any valid name | globally unique, so yours is probably taken |
   | Consistency | immediate | immediate for S3, but not for every service |
   | Throttling | never | real, and your retry logic starts to matter |
   | Cost | zero | metered |

   The code column is the point. Nothing in `awstool/` mentions moto, so pointing it at a real account means dropping the `@mock_aws` decorator and supplying credentials — nothing more.
8. Close the chapter. §1.22 argues the core of Python fits in your head; the same is not true of AWS, and the gap is the lesson. From memory, without looking back, write `examples/report.py`:

   ```python
   # examples/report.py
   import boto3
   from moto import mock_aws
   from awstool import read_portfolio, portfolio_cost
   
   BUCKET = 'pydistilled-labs'
   KEY = 'data/portfolio.csv'
   
   @mock_aws
   def main():
       s3 = boto3.client('s3', region_name='us-east-1')
       s3.create_bucket(Bucket=BUCKET)
       s3.upload_file('examples/portfolio.csv', BUCKET, KEY)
   
       for name, shares, price in read_portfolio(s3, BUCKET, KEY):
           print(f'{name:>10s} {shares:10d} {price:10.2f}')
       print(f'{"TOTAL":>10s} {portfolio_cost(s3, BUCKET, KEY):21.2f}')
   
   if __name__ == '__main__':
       main()
   ```

   Run `python3 -m examples.report` from the project root. Whatever you had to look up splits into two lists: the Python you should drill, and the AWS API details nobody memorizes. Only the first list is worth revising.

**Checkpoint** — `python3 -m unittest discover tests -v` passes three tests, `python3 -m examples.report` prints six holdings and a total of `40836.00`, and `boto3.__file__` points inside `venv/`.

**Stretch** — Add a `tests/test_portfolio_bucket.py` covering `__len__`, `__contains__` and the `None` return from `get()` on a missing key.

**Self-check**

- Why does `s3:ListBucket` take a different Resource ARN from `s3:GetObject`?
- Which single line would you change to run this against a real account?

---

[← Lab 11](lab-11-a-module-and-a-cli.md) · [AWS track index](../README.md) · [Paired Python track lab 12](../../python-track/labs/lab-12-packages-structure-and-third-party-code.md) · [Paired GCP track lab 12](../../gcp-track/labs/lab-12-package-it-test-it-and-point-it-at-real-google-cloud.md)
