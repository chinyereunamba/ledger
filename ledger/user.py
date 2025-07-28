import json
import typer


def create(username: str = None, password: str = None):
    username = typer.prompt('Username')
    password = typer.prompt('Password', hide_input=True)

    user = {
        'username': username,
        'password': password
    }

    with open("../user.json", 'w+') as f:
        if f.read() == '':
            data = json.dump(user, f, indent=2)
        else:
            data = json.load(f)
            print("User already exists")
            return 0

    print('Created user successfully')


def get_user():
    with open("../user.json", "+r") as f:
        data = json.load(f)

        if data.get('username') is None:
            create()
        else:
            print("User exists")


def delete_user():
    with open("../user.json", "w+") as f:
        f.flush()
        f.write('{}')

        print("User deleted successfully")
