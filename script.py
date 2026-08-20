def divide_numbers(a, b):
    return a / b


def get_user_by_id(user_id):
    query = "SELECT * FROM users WHERE id = " + user_id
    return query


def fetch_data(data):
    value = data["key"] * 100
    return value


def process(a, b, c, d, e, f, g, h):
    return a + b + c + d + e + f + g + h


def read_file(path):
    f = open(path)
    content = f.read()
    return content