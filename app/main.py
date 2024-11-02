from fastapi import FastAPI, Response, status, HTTPException
from fastapi.params import Body
from pydantic import BaseModel
from typing import Optional
from random import randrange
import psycopg2
import os 
from dotenv import load_dotenv
from psycopg2.extras import RealDictCursor # Because it doesn't give you the column names, just the values of the columns. Hence why this is needed
import time
import sys

load_dotenv()
p_host = 'localhost'
p_database = 'fastapi'
p_user = 'postgres'
p_password = os.getenv("postgres_password")
p_port = 5433

try:
    conn = psycopg2.connect(host = p_host, dbname = p_database, user = p_user, password = p_password, port = p_port, cursor_factory=RealDictCursor)
    cursor = conn.cursor
    print("Database connection was successful")
except Exception as error:
    raise SystemExit(f"Connecting to database failed \nError: {error}")

app = FastAPI()

# Schema. Title str, content str,
class Post(BaseModel):
    title: str
    content: str
    publish: bool = True
    rating: Optional[int] = None
    id: Optional[int] = randrange(0, 100000)


@app.get("/")
async def root():
    return {"message": "Hello World"}


my_posts = [{"title": "title of post 1", "content": "content of post 1", "id": 1},
            {"title": "favorite foods", "content": "I like pizza", "id": 2}]


@app.get("/posts")
def get_posts():
    return {"data": my_posts}


@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_post(new_post: Post):
    new_post_dict = new_post.model_dump()
    print(new_post_dict)
    # manually adding new id to posts in th absence of dictionaries

    # no longer needed since it has been added to the pydantic schema model. It's actually needed if not, it will give the same Id twice
    new_post_dict['id'] = randrange(0, 100000)
    print(new_post_dict)
    my_posts.append(new_post_dict)
    print(my_posts)
    return {"data": new_post_dict}


# My Experiment
@app.post("/posts/{id}")
def send_post(id, new_post: Post):
    print(id)
    new_post_dict = new_post.model_dump()
    print(new_post_dict)
    # manually adding new id to posts in th absence of dictionaries
    # new_post_dict['id'] = id # no longer needed since it has been added to the pydantic schema model.
    print(new_post_dict)
    my_posts.append(new_post_dict)
    print(my_posts)
    return {"data": f'Your post has been sent'}


def find_post(id):
    for p in my_posts:
        if p["id"] == id:
            return p


@app.get("/posts/{id}")
def get_post(id: int):  # , response: Response):
    # print(id)
    # Path parameter is always returned as a string. Needs to be converted to integer if need be.
    post = find_post(id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Post {id} not found")
        # response.status_code = status.HTTP_404_NOT_FOUND
        # return {'message': f"Post {id} not found"}
    return {"data": post}


def find_index_post(id):
    for i, p in enumerate(my_posts):
        if p['id'] == id:
            return i


# with HTTP_204_NO_CONTENT ;  Any output in return is not shown.
@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int):
    # find the index in the array that has required id
    # my_post.pop to remove it.
    post_index = find_index_post(id)
    if not post_index:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"This post Id '{id}' doesn't exist")

    # Variation #2
    # if post_index == None:
    #     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
    #                         detail="This post Id doesn't exist")
    my_posts.pop(post_index)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.put("/posts/{id}", status_code=status.HTTP_201_CREATED)
def update_post(id: int, post: Post):
    post_index = find_index_post(id)
    if not post_index:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"This post Id '{id}' doesn't exist")
    # my_posts[post_index] = post -- DOESN'T WORK. Works once, then won't work again. Gives this error "TypeError: 'Post' object is not subscriptable"
    # return {"Message": f"Post {id} updated"}, my_posts
    post_dict = post.model_dump()  # convert front end input into a dictionary
    # post_dict['id'] = id = Not necessary since I define the id in the input
    my_posts[post_index] = post_dict
    # return my_posts
    return {"data": post_dict}
