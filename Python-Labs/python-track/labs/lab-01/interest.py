principal = 1000
rate = 0.05
numYears = 5
year = 1

while year <= numYears:
    principal = principal * (1 + rate)
    print(year, principal)
    year += 1