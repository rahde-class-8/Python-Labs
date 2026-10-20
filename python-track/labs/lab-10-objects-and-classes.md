## Lab 10 — Objects and classes

**Section §1.16 · 30 minutes**

Goal: write a class with special methods, extend it by inheritance, and then see why composition is usually the better answer.

**Steps**

1. Confirm that everything is an object, and that operators are methods:

   ```python
   items = [37, 42]
   items.append(73)
   dir(items)
   items.__add__([73, 101])      # Same as items + [73, 101]
   (5).__add__(3)
   'abc'.__len__()
   ```

   `dir()` is the tool for interactive exploration when you have no IDE.
2. Create `stack.py` with the chapter's `Stack` class:

   ```python
   # stack.py
   
   class Stack:
       def __init__(self):              # Initialize the stack
           self._items = []
   
       def push(self, item):
           self._items.append(item)
   
       def pop(self):
           return self._items.pop()
   
       def __repr__(self):
           return f'<{type(self).__name__} at 0x{id(self):x}, size={len(self)}>'
   
       def __len__(self):
           return len(self._items)
   ```
3. Use it, and see what the two special methods bought you:

   ```python
   s = Stack()
   s.push('Dave')
   s.push(42)
   s.push([3, 4, 5])
   len(s)             # __len__ makes the built-in work
   s                  # __repr__ makes it readable — always define this
   x = s.pop()        # [3, 4, 5]
   y = s.pop()        # 42
   ```
4. Test the privacy convention — and its lack of teeth:

   ```python
   s._items           # Works. Nothing is actually hidden.
   s._items.clear()   # Also works. Your code reviewer is the enforcement.
   ```
5. Extend by inheritance, adding a method:

   ```python
   class MyStack(Stack):
       def swap(self):
           a = self.pop()
           b = self.pop()
           self.push(a)
           self.push(b)
   
   s = MyStack()
   s.push('Dave')
   s.push(42)
   s.swap()
   s.pop()            # 'Dave'
   ```
6. Override a method and call back into the original with `super()`:

   ```python
   class NumericStack(Stack):
       def push(self, item):
           if not isinstance(item, (int, float)):
               raise TypeError('Expected an int or float')
           super().push(item)
   
   s = NumericStack()
   s.push(42)
   s.push('Dave')     # TypeError
   ```
7. Now build a `Calculator` by composition rather than inheritance. It uses a stack but is not one:

   ```python
   class Calculator:
       def __init__(self):
           self._stack = Stack()
   
       def push(self, item):
           self._stack.push(item)
   
       def pop(self):
           return self._stack.pop()
   
       def add(self):
           self.push(self.pop() + self.pop())
   
       def mul(self):
           self.push(self.pop() * self.pop())
   
       def sub(self):
           right = self.pop()
           self.push(self.pop() - right)
   
       def div(self):
           right = self.pop()
           self.push(self.pop() / right)
   ```
8. Calculate `2 + 3 * 4` in postfix:

   ```python
   calc = Calculator()
   calc.push(2)
   calc.push(3)
   calc.push(4)
   calc.mul()
   calc.add()
   calc.pop()         # 14
   ```

   Then ask yourself why `sub()` and `div()` need the `right` variable while `add()` and `mul()` do not.

**Checkpoint** — `calc.pop()` returns `14`, and printing a `Stack` shows the `<Stack at 0x..., size=N>` form.

**Stretch** — Give `Calculator` a `__repr__` that shows the current stack depth.

**Self-check**

- Why is `Calculator` not written as a subclass of `Stack`?
- What breaks if you omit `super().push(item)` from `NumericStack`?

---

[← Lab 9](lab-09-exceptions-and-program-termination.md) · [Python track index](../README.md) · [Paired AWS track lab 10](../../aws-track/labs/lab-10-wrapping-boto3-in-a-class.md) · [Lab 11 →](lab-11-modules-and-script-writing.md)
