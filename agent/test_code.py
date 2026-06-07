def get_user(user_id):
    # SQL injection risk
    query = "SELECT * FROM users WHERE id = " + user_id
    return query

def process_data(data):
    result = data["key"] * 100
    return result

def bad_function(a,b,c,d,e,f,g,h):
    return a+b+c+d+e+f+g+h