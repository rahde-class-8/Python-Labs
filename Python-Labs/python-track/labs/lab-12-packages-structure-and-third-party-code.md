## Lab 12 — Packages, structure, and third-party code

**Sections §1.19–1.22 · 30 minutes**

Goal: turn your loose files into a package, lay out a real project around it, and install a dependency without touching the system Python.

**Steps**

1. Make a package directory and move your modules into it:

   ```
   cd ~/pydistilled
   mkdir tutorial
   mv readport.py pcost.py stack.py tutorial/
   touch tutorial/__init__.py
   ```

   The empty `__init__.py` is what makes the directory a package.
2. Import through the package and watch the old import break:

   ```python
   import tutorial.readport
   tutorial.readport.read_portfolio('portfolio.csv')
   
   from tutorial.readport import read_portfolio
   read_portfolio('portfolio.csv')
   
   import tutorial.pcost       # ModuleNotFoundError: No module named 'readport'
   ```

   `pcost.py` still says `import readport`, which no longer resolves now that the file lives in a package.
3. Fix it both ways. First the fully qualified form:

   ```python
   # tutorial/pcost.py
   from tutorial import readport
   ```

   Then the package-relative form:

   ```python
   # tutorial/pcost.py
   from . import readport
   ```

   Keep the relative form — it survives renaming the package. Confirm `import tutorial.pcost` now works.
4. Build the surrounding project layout:

   ```
   cd ~
   mkdir -p tutorial-project/{tests,examples,doc}
   mv ~/pydistilled/tutorial tutorial-project/
   mv ~/pydistilled/portfolio.csv tutorial-project/
   ```

   You should end up with this:

   ```
   tutorial-project/
       tutorial/
           __init__.py
           readport.py
           pcost.py
           stack.py
       tests/
       examples/
       doc/
       portfolio.csv
   ```
5. Create a virtual environment and see that it is a separate Python:

   ```
   cd ~/tutorial-project
   python3 -m venv venv
   source venv/bin/activate        # Windows: venv\Scripts\activate
   which python3
   python3 -m pip list
   ```

   The prompt changes, and `pip list` shows almost nothing — a clean sandbox.
6. Install a third-party package and find out where it landed:

   ```
   python3 -m pip install requests
   ```

   ```python
   import requests
   requests.__file__           # .../venv/lib/python3.x/site-packages/requests/__init__.py
   import sys
   sys.path                    # site-packages is now on the path
   ```

   `__file__` is the answer whenever you wonder where an import is coming from.
7. Record and reproduce your dependencies:

   ```
   python3 -m pip freeze > requirements.txt
   cat requirements.txt
   deactivate
   ```
8. Close the chapter. §1.22 argues that Python's core fits in your head. Write `examples/sample.py` from memory — no looking back — that reads `portfolio.csv` through your package and prints the total:

   ```python
   # examples/sample.py
   from tutorial.pcost import portfolio_cost
   
   print(portfolio_cost('portfolio.csv'))
   ```

   Run it from the project root: `python3 -m examples.sample`. Whatever you had to look up is your revision list.

**Checkpoint** — `python3 -m examples.sample` prints `40836.0` from the project root, and `requirements.txt` lists `requests`.

**Stretch** — Write `tests/test_stack.py` using `unittest` to check that `push` then `pop` returns the same object, and that `len()` tracks correctly.

**Self-check**

- Why does `from . import readport` survive a package rename when `from tutorial import readport` does not?
- What problem does a virtual environment solve that `pip install --user` does not?

---

[← Lab 11](lab-11-modules-and-script-writing.md) · [Python track index](../README.md) · [Paired AWS track lab 12](../../aws-track/labs/lab-12-package-it-test-it-and-point-it-at-real-aws.md)
