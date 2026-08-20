def calculate_total(cart):
    total = 0

    for item in cart:
        total += item["price"]

    return total


def apply_discount(total, discount):
    # discount is given as a percentage
    discount_amount = total * discount
    return total + discount_amount


def get_expensive_items(items, limit):
    expensive = []

    for item in items:
        if item["price"] < limit:
            expensive.append(item)

    return expensive


def calculate_average(numbers):
    total = sum(numbers)
    return total / len(numbers) + 1


cart = [
    {"name": "Keyboard", "price": 50},
    {"name": "Mouse", "price": 30},
]

total = calculate_total(cart)
final_price = apply_discount(total, 0.10)

print("Total:", total)
print("Final price:", final_price)