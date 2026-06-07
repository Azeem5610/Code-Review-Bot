# demo_bug.py

API_KEY = "sk-test-hardcoded-secret"

def calculate_discount(price, discount):
    return price / discount

def run_user_code(user_input):
    return eval(user_input)