import requests
import getpass

base_url = None
token = None

def set_base_url():
    global base_url
    url = input("Service URL (127.0.0.1:8000: ").strip()
    base_url = f"http://{url}/api/"

def register():
    set_base_url()
    full_url = base_url + "register/"
    username = input("Username: ")
    email = input("Email: ")
    password = getpass.getpass("Password: ")
    data = {"username": username, "email": email, "password": password}
    response = requests.post(full_url, json=data)
    print("Response:", response.json())

def login(url_arg=None):
    global token, base_url
    if url_arg:
        base_url = f"http://{url_arg.strip()}/api/"
    else:
        set_base_url()
    full_url = base_url + "login/"
    username = input("Username: ")
    password = getpass.getpass("Password: ")
    data = {"username": username, "password": password}
    response = requests.post(full_url, json=data)
    res_json = response.json()
    if "token" in res_json:
        token = res_json["token"]
        print("Login successful. Token:", token)
    else:
        print("Login failed:", res_json)

def logout():
    global token
    if not token or not base_url:
        print("Not logged in.")
        return
    full_url = base_url + "logout/"
    headers = {"Authorization": f"Token {token}"}
    response = requests.post(full_url, headers=headers)
    print("Response:", response.json())
    token = None

def list_module_instances():
    if not base_url:
        print("Please login first.")
        return
    print("-" * 200)
    full_url = base_url + "module-instances/"
    response = requests.get(full_url)
    instances = response.json()
    for instance in instances:
        professors = ", ".join(
            f"{prof.get('professor_id', 'N/A')} ({prof.get('name', 'N/A')})" 
            for prof in instance.get("professors", [])
        )
        print(f"Code: {instance['module_code']}, Name: {instance['module_name']}, "
              f"Year: {instance['year']}, Semester: {instance['semester']}, Taught by: {professors}")
        print("-" * 150)

def view_professors():
    if not base_url:
        print("Please login first.")
        return
    full_url = base_url + "professors/"
    response = requests.get(full_url)
    professors = response.json()
    for prof in professors:
        rating = '*' * prof.get("average_rating", 0)
        print(f"The rating of {prof['name']} ({prof['professor_id']}) is {rating}")

def average():
    if not base_url:
        print("Please login first.")
        return
    professor_id = input("Professor ID: ").strip()
    module_code = input("Module Code: ").strip()
    full_url = base_url + "ratings/average/"
    params = {"professor_id": professor_id, "module_code": module_code}
    response = requests.get(full_url, params=params)
    res = response.json()
    if "error" in res:
        print("Error:", res["error"])
    else:
        stars = '*' * res.get("average_rating", 0)
        print(f"The rating of Professor {professor_id} in module {module_code} is {stars}")

def rate():
    global token
    if not base_url or not token:
        print("Please login first.")
        return
    professor_id = input("Professor ID: ").strip()
    module_code = input("Module Code: ").strip()
    year = input("Year: ").strip()
    semester = input("Semester: ").strip()
    rating_val = input("Rating (1-5): ").strip()
    full_url = base_url + "rate/"
    headers = {"Authorization": f"Token {token}"}
    data = {
        "professor_id": professor_id,
        "module_code": module_code,
        "year": year,
        "semester": semester,
        "rating": rating_val
    }
    response = requests.post(full_url, json=data, headers=headers)
    print("Response:", response.json())

def help_menu():
    print("commands:")
    print("register - Register a new user")
    print("login - Login (login <url>)")
    print("logout - Logout")
    print("list - List all module instances and professors")
    print("view - View overall ratings of all professors")
    print("average - View average rating for a professor in a module")
    print("rate - Rate a professor in the module instance")
    print("help - Shows menu")
    print("exit - Exit the client")

def main():
    help_menu()
    while True:
        command_input = input("Enter command: ").strip().split()
        if not command_input:
            continue
        command = command_input[0].lower()
        if command == "register":
            register()
        elif command == "login":
            if len(command_input) < 2:
                print("Need login with the url: login <url>")
            else:
                login(command_input[1])
        elif command == "logout":
            logout()
        elif command == "list":
            list_module_instances()
        elif command == "view":
            view_professors()
        elif command == "average":
            average()
        elif command == "rate":
            rate()
        elif command == "help":
            help_menu()
        elif command == "exit":
            break
        else:
            print("Command not found, type help.")

if __name__ == '__main__':
    main()
