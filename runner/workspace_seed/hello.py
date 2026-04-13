def greet(name, greeting="Hello"):
    return f"{greeting}, {name}!"


def add(a, b):
    return a + b


def multiply(a, b):
    return a * b


def fizzbuzz(n):
    results = []
    for i in range(1, n + 1):
        if i % 15 == 0:
            results.append("FizzBuzz")
        elif i % 3 == 0:
            results.append("Fizz")
        elif i % 5 == 0:
            results.append("Buzz")
        else:
            results.append(str(i))
    return results


if __name__ == "__main__":
    print(greet("World"))
    print(add(2, 3))
    print(fizzbuzz(20))
