import requests


def get_user_name(username):
    response = requests.get(f"https://api.github.com/users/{username}")
    json_data = response.json()
    return json_data['name']


def get_contributors_data():
    response = requests.get(
        "https://api.github.com/repos/vigneshshettyin/Bulk-Mailer/contributors?per_page=1000")
    json_data = response.json()
    unique_contributors = {}
    mentors = ['vigneshshettyin', 'data-charya', 'laureenf', 'shettyraksharaj']
    for d in json_data:
        if d["login"] not in unique_contributors.keys() and d["login"] not in mentors:
            new_data = {
                "username": d["login"],
                "image": d["avatar_url"],
                "profile_url": d["html_url"],
                "name": get_user_name(d["login"])
            }
            unique_contributors[d["login"]] = new_data
    return unique_contributors

    def get_mentors_data():

        mentors = ['vigneshshettyin', 'data-charya',
                   'laureenf', 'shettyraksharaj']
        for d in mentors:
            response = requests.get(f"https://api.github.com/users/{username}")
            json_data = response.json()
            new_data = {
                "username": json_data["login"],
                "image": json_data["avatar_url"],
                "profile_url": json_data["html_url"],
                "name": json_data["name"]
            }
    return unique_contributors
