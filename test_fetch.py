import requests

# 1. Login as the admin we just created (email is test@test.com)
resp = requests.post("http://127.0.0.1:8000/api/v1/login/access-token", data={"username": "test@test.com", "password": "123"})
if not resp.ok:
    print("Login failed:", resp.text)
    exit()

token = resp.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# 2. Get tasks
resp = requests.get("http://127.0.0.1:8000/api/v1/tasks/", headers=headers)
print("Tasks response status:", resp.status_code)
if resp.status_code != 200:
    print("Error Details:", resp.text)
else:
    print("Success:", resp.json())
