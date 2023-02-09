import requests
import json
import random


# Helper function to signup a user
def signup_user():
    response = requests.post("http://localhost:8000/api/users/signup/", json={
        "user":
            {
                "username": "user" + str(random.randint(0, 1000000)),
                "email": "user" + str(random.randint(0, 1000000)) + "@example.com",
                "password": "password"
            }
    })
    print(f'User {response.json()["user"]["username"]} created')
    return response.json()

# Helper function to login a user
def login_user(email, password):
    response = requests.post("http://localhost:8000/api/users/login/", json = {
        "user":
            {
                "email": email,
                "password": password
            }
    })
    print(f'User {response.json()["user"]["username"]} logged in')
    return response.json()

# Helper function to create a post
def create_post(token):
    response = requests.post("http://localhost:8000/api/posts/", json={
        "title": "sample_title",
        "content": "This is a sample post"
    }, 
    headers={
        "Content-Type": "application/json",
        "Authorization": "Token " + token
    })

    if response.ok:
        print(f'Post {response.json()["id"]} created by user {response.json()["user"]}')
        return response.json()
    print(response.json()["errors"])

# Helper function to like a post
def like_post(post, token):
    response = requests.post("http://localhost:8000/api/posts/" + str(post["id"]) + "/likes/", headers={
        "Authorization": "Token " + token
    })
    
    if response.ok:
        print(f'Post {post["id"]} liked by user {response.json()["user"]}')
        return
    print(response.json()["errors"])

# Signup and login the number of users specified in the config file
def signup_all_users(number_of_users: int):

    tokens = {}

    for i in range(number_of_users):
        signup_response = signup_user()
        email = signup_response["user"]["email"]
        login_response = login_user(email, "password")
        tokens[signup_response["user"]["username"]] = login_response["user"]["token"]

    return tokens

# Create posts for each user
def create_posts_for_all_users(tokens: dict(), max_posts_per_user: int):

    posts = []

    for user, token in tokens.items():
        num_posts = random.randint(1, max_posts_per_user)
        posts += [create_post(token) for j in range(num_posts)]

    return posts

# Like posts randomly
def like_posts_for_all_users(posts: list, tokens: dict, most_likes_per_user: int):

    for i in range(most_likes_per_user):
        like_post(random.choice(posts), random.choice(list(tokens.values())))


def create_random_activity(config_path: str):

    config = json.loads(open(config_path).read())
    number_of_users = config["number_of_users"]
    max_posts_per_user = config["max_posts_per_user"]
    most_likes_per_user = config["most_likes_per_user"]

    tokens = signup_all_users(number_of_users=number_of_users)
    posts = create_posts_for_all_users(tokens=tokens, max_posts_per_user=max_posts_per_user)
    like_posts_for_all_users(posts=posts, tokens=tokens, most_likes_per_user=most_likes_per_user)



if __name__ == '__main__':

    create_random_activity('bot_config.json')
