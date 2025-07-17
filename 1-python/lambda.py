# 1. Add two numbers
add = lambda x, y: x + y
print(add(3, 4))  # ➜ 7

# 2. Square a number
square = lambda x: x ** 2
print(square(5))  # ➜ 25

# 3.Filter even numbers in a list
evens = list(filter(lambda x: x % 2 == 0, [1,2,3,4,5,6]))
print(evens)  # ➜ [2, 4, 6]

# 4. Square all numbers in a list
squares = list(map(lambda x: x ** 2, [1,2,3,4]))
print(squares)  # ➜ [1, 4, 9, 16]

# 5. Convert names to lowercase
fruits = ["Apple", "Banana", "Orange"]
lower = list(map(lambda s: s.lower(), fruits))
print(lower)

# 6. Sort tuples by their second element
data = [(1, 30), (2, 10), (3, 20)]
sorted_data = sorted(data, key=lambda t: t[1])
print(sorted_data)  # ➜ [(2, 10), (3, 20), (1, 30)]

# 7. Inline lambda called immediately
print((lambda x, y: x * y)(3, 5))  # ➜ 15

# 8. Conditional logic with lambda
is_even = lambda x: "Even" if x % 2 == 0 else "Odd"
print(is_even(4))  # ➜ "Even"

# 9. Create a multiplier function
def make_multiplier(n):
    return lambda x: x * n
doubler = make_multiplier(2)
print(doubler(11))  # ➜ 22

# 10. Find the highest price item in a price dict
prices = {'apple': 2, 'banana': 1, 'cherry': 3}
most_expensive = max(prices, key=lambda k: prices[k])
print(most_expensive)  # ➜ 'cherry'