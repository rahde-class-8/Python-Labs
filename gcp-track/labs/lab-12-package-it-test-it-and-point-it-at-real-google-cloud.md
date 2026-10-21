## Lab 12 — Package it, test it, and point it at real Google Cloud

**Pairs with Python Lab 12 (§1.19–1.22) · 30 minutes**

Goal: package the Google Cloud code properly, write real tests against the emulator, and understand exactly what changes when the target is a live project.

**Steps**

1. Build the package and project layout:

   ```
   cd ~
   mkdir -p gcptool-project/{gcptool,tests,examples,policies}
   cd gcptool-project
   touch gcptool/__init__.py
   mv ~/pydistilled-gcp/gcpport.py gcptool/
   mv ~/pydistilled-gcp/portfolio_bucket.py gcptool/
   cp ~/pydistilled-gcp/gcpmock.py .
   cp ~/pydistilled-gcp/portfolio.csv examples/
   ```

   You should have:

   ```
   gcptool-project/
       gcpmock.py
       gcptool/
           __init__.py
           gcpport.py
           portfolio_bucket.py
       tests/
       examples/
           portfolio.csv
       policies/
   ```

   `gcpmock.py` sits at the top level, *outside* the package. The package is the code you would ship; the emulator helper is only for tests and examples, and nothing inside `gcptool/` may import it.
2. Fix the intra-package import with the relative form from §1.19:

   ```python
   # gcptool/report.py
   from . import gcpport
   from .portfolio_bucket import PortfolioBucket

   def summary(client, bucket, name):
       holdings = gcpport.read_portfolio(client, bucket, name)
       return {
           'holdings': len(holdings),
           'total': sum(s * p for _, s, p in holdings),
       }
   ```

   `from . import gcpport` does not name the package, so renaming `gcptool` later breaks nothing.
3. Export a clean public surface from `__init__.py`:

   ```python
   # gcptool/__init__.py
   from .gcpport import read_portfolio, portfolio_cost
   from .portfolio_bucket import PortfolioBucket

   __all__ = ['read_portfolio', 'portfolio_cost', 'PortfolioBucket']
   ```

   Now callers write `from gcptool import read_portfolio` without knowing which module it lives in — you are free to reorganize internals later.
4. Write a real test. This is where the design from Lab 11 pays off:

   ```python
   # tests/test_gcpport.py
   import unittest
   from google.cloud import storage

   from gcpmock import mock_gcs
   from gcptool import read_portfolio, portfolio_cost

   BUCKET = 'test-bucket'
   NAME = 'portfolio.csv'
   DATA = ('AA,100,32.20\n'
           'IBM,50,91.10\n'
           'GE,95,N/A\n')

   class TestReadPortfolio(unittest.TestCase):

       def seed(self):
           client = storage.Client(project='test')
           client.create_bucket(BUCKET).blob(NAME).upload_from_string(DATA)
           return client

       def test_skips_bad_rows(self):
           with mock_gcs():
               holdings = read_portfolio(self.seed(), BUCKET, NAME)
               self.assertEqual(len(holdings), 2)
               self.assertEqual(holdings[0], ('AA', 100, 32.20))

       def test_total(self):
           with mock_gcs():
               self.assertAlmostEqual(portfolio_cost(self.seed(), BUCKET, NAME), 7775.0)

       def test_missing_object_exits(self):
           with mock_gcs():
               client = self.seed()
               with self.assertRaises(SystemExit):
                   read_portfolio(client, BUCKET, 'nope.csv')

   if __name__ == '__main__':
       unittest.main()
   ```

   Run it from the project root:

   ```
   python3 -m unittest discover tests -v
   ```

   Three tests, no Google Cloud account, under a second. Each test gets a clean, empty Cloud Storage because each one starts its own `mock_gcs()`. `python3 -m` puts the project root on `sys.path`, which is how the tests find both `gcpmock` and `gcptool`.
5. Pin the dependencies:

   ```
   python3 -m venv venv
   source venv/bin/activate
   python3 -m pip install google-cloud-storage gcp-storage-emulator
   python3 -m pip freeze > requirements.txt
   grep -E '^(google-cloud-storage|gcp-storage-emulator|google-api-core)' requirements.txt
   ```

   Then check where an import actually comes from, the §1.21 move:

   ```python
   import google.cloud.storage, gcp_storage_emulator
   google.cloud.storage.__file__
   gcp_storage_emulator.__file__
   ```

   Both now point inside `venv/`, not at the system Python. `google-cloud-storage` belongs in `requirements.txt`; `gcp-storage-emulator` is a test-only dependency, so in a real project it goes in a separate dev requirements file.
6. Write the least-privilege bindings as package data, using what Lab 7 computed:

   ```json
   {
     "bindings": [
       {
         "role": "roles/storage.objectViewer",
         "members": [
           "serviceAccount:lab-runner@pydistilled.iam.gserviceaccount.com"
         ]
       }
     ],
     "version": 1
   }
   ```

   Save as `policies/read-portfolio.json`. In JSON the members are a list, because JSON has no set type; the client library turns them into a set when it loads a policy. This one binding, applied to the bucket, is the whole access the reporting job needs — Lab 7's `best` role, granted to the one member who uses it.
7. Now the real-project question. What changes, and what does not:

   | Concern | Under the emulator | Against real Google Cloud |
   | --- | --- | --- |
   | Your code | unchanged | unchanged |
   | Credentials | anonymous, automatic | `gcloud auth application-default login`, or a service account attached to the VM, function or job |
   | Project | any string you like | a real project ID, with billing enabled |
   | Location | always `US` unless you ask | decides latency, cost and data residency |
   | IAM policy | stored, never evaluated | enforced — `Forbidden` becomes real |
   | Bucket names and labels | not validated | names globally unique, labels lowercase only |
   | Listings | one page, `page_size` ignored | up to 1,000 objects per request |
   | Throttling | never | real — the built-in retries start to matter |
   | Cost | zero | metered |

   The code row is the point. Nothing in `gcptool/` mentions the emulator, so pointing it at a real project means creating the client without `mock_gcs()` and supplying credentials — nothing more.
8. Close the chapter. §1.22 argues the core of Python fits in your head; the same is not true of Google Cloud, and the gap is the lesson. From memory, without looking back, write `examples/report.py`:

   ```python
   # examples/report.py
   from google.cloud import storage
   from gcpmock import mock_gcs
   from gcptool import read_portfolio, portfolio_cost

   BUCKET = 'pydistilled-labs'
   NAME = 'data/portfolio.csv'

   def main():
       with mock_gcs():
           client = storage.Client(project='pydistilled')
           bucket = client.create_bucket(BUCKET)
           bucket.blob(NAME).upload_from_filename('examples/portfolio.csv')

           for sym, shares, price in read_portfolio(client, BUCKET, NAME):
               print(f'{sym:>10s} {shares:10d} {price:10.2f}')
           print(f'{"TOTAL":>10s} {portfolio_cost(client, BUCKET, NAME):21.2f}')

   if __name__ == '__main__':
       main()
   ```

   Run `python3 -m examples.report` from the project root. Whatever you had to look up splits into two lists: the Python you should drill, and the Google Cloud API details nobody memorizes. Only the first list is worth revising.

**Checkpoint** — `python3 -m unittest discover tests -v` passes three tests, `python3 -m examples.report` prints six holdings and a total of `40836.00`, and `google.cloud.storage.__file__` points inside `venv/`.

**Stretch** — Add `tests/test_portfolio_bucket.py` covering `__len__`, `__contains__` and the `None` return from `get()` on a missing object.

**Self-check**

- Why does `gcpmock.py` live outside the `gcptool` package?
- Which single change would you make to run `examples/report.py` against a real project?

---

[← Lab 11](lab-11-a-module-and-a-cli.md) · [GCP track index](../README.md) · [Paired Python track lab 12](../../python-track/labs/lab-12-packages-structure-and-third-party-code.md) · [Paired AWS track lab 12](../../aws-track/labs/lab-12-package-it-test-it-and-point-it-at-real-aws.md)
