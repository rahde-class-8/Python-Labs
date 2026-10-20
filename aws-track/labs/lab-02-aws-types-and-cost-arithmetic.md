## Lab 2 — AWS types and cost arithmetic

**Pairs with Python Lab 2 (§1.3–1.4) · 30 minutes**

Goal: find out what types AWS actually hands you — which is not what you would guess — and do the division-operator work on billing math.

**Steps**

1. Create `types_tour.py` and look at the types in an S3 listing:

   ```python
   # types_tour.py
   import boto3
   from moto import mock_aws
   
   @mock_aws
   def main():
       s3 = boto3.client('s3', region_name='us-east-1')
       s3.create_bucket(Bucket='pydistilled-labs')
       s3.put_object(Bucket='pydistilled-labs', Key='portfolio.csv',
                     Body=open('portfolio.csv', 'rb'))
   
       obj = s3.list_objects_v2(Bucket='pydistilled-labs')['Contents'][0]
       for key, value in obj.items():
           print(f'{key:<15} {type(value).__name__:<10} {value}')
   
   if __name__ == '__main__':
       main()
   ```

   `Size` is an `int`, `LastModified` is a `datetime`, `ETag` is a `str` with literal quote characters inside it, and `Key` is a `str`. boto3 has already converted the wire format for you.
2. Now meet DynamoDB, which does something different. Add to the same mock:

   ```python
   from decimal import Decimal
   
   ddb = boto3.client('dynamodb', region_name='us-east-1')
   ddb.create_table(
       TableName='Holdings',
       KeySchema=[{'AttributeName': 'Symbol', 'KeyType': 'HASH'}],
       AttributeDefinitions=[{'AttributeName': 'Symbol', 'AttributeType': 'S'}],
       BillingMode='PAY_PER_REQUEST')
   
   table = boto3.resource('dynamodb', region_name='us-east-1').Table('Holdings')
   table.put_item(Item={'Symbol': 'AA', 'Shares': 100, 'Price': Decimal('32.20')})
   
   item = table.get_item(Key={'Symbol': 'AA'})['Item']
   print(item)
   print(type(item['Shares']), type(item['Price']))
   ```

   Both come back as `Decimal` — even `Shares`, which you stored as an `int`. DynamoDB has one numeric type and boto3 maps it to `Decimal` to avoid float rounding.
3. Hit the trap this creates:

   ```python
   price = item['Price']
   price * 100          # Fine — Decimal * int
   price * 1.5          # TypeError: unsupported operand type(s)
   float(price) * 1.5   # Fine — convert first
   ```

   `Decimal` refuses to mix with `float` on purpose: silently combining exact and inexact numbers is how money bugs happen. Converting is your decision to make explicitly.
4. Compute the portfolio value out of DynamoDB, keeping `Decimal` throughout:

   ```python
   table.put_item(Item={'Symbol': 'IBM', 'Shares': 50, 'Price': Decimal('91.10')})
   items = table.scan()['Items']
   total = sum(i['Shares'] * i['Price'] for i in items)
   print(total, type(total).__name__)
   ```

   You get `7775.00` as a `Decimal` — exact, with trailing zeros preserved, unlike the float total on the Python track.
5. Do storage cost arithmetic, exercising the operators from §1.4. Assume a rate of `0.023` per GB-month (substitute the real current rate if you want — the arithmetic is the lesson):

   ```python
   size_bytes = 1536 * 1024 * 1024
   
   gib = size_bytes / (1024 ** 3)      # 1.5   — binary gigabytes
   gb  = size_bytes / (1000 ** 3)      # 1.610612736 — decimal gigabytes
   print(gib, gb)
   
   rate = 0.023
   print(round(gib * rate, 4))
   ```

   The two answers differ by about 7%. AWS bills in decimal GB; most tools report binary GiB. This gap is a real source of invoice confusion.
6. Use truncating division and modulo on instance hours:

   ```python
   hours = 36
   days, leftover = divmod(hours, 24)
   print(f'{days} full days, {leftover} hours')
   
   hours // 24         # 1 — whole days
   hours % 24          # 12 — remainder
   -36 // 24           # -2, not -1 — truncates toward negative infinity
   ```
7. Watch float money go wrong, and fix it:

   ```python
   0.1 + 0.2 == 0.3                              # False
   Decimal('0.1') + Decimal('0.2') == Decimal('0.3')   # True
   Decimal(0.1)                                  # The float's real value — look at it
   ```

   `Decimal(0.1)` from a float keeps the float's error; `Decimal('0.1')` from a string does not. Always build `Decimal` from strings.

**Checkpoint** — `types_tour.py` prints `Size` as `int` and both DynamoDB numbers as `Decimal`, and the portfolio total is `7775.00`.

**Stretch** — Write `estimate_cost(size_bytes, rate=0.023, use_gib=False)` and show the two answers side by side for a 500 GB bucket.

**Self-check**

- Why does DynamoDB return `Decimal` where S3 returns `int`?
- Why does `Decimal('0.1')` behave differently from `Decimal(0.1)`?

---

[← Lab 1](lab-01-boto3-in-the-repl-and-your-first-mocked-script.md) · [AWS track index](../README.md) · [Paired Python track lab 2](../../python-track/labs/lab-02-primitives-variables-and-arithmetic.md) · [Lab 3 →](lab-03-conditionals-over-aws-state.md)
