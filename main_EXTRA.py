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

################################################################################
# VERSION 1 - Experimentation
################################################################################

from fastapi import FastAPI
from fastapi.params import Body
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

# Schema. Title str, content str,
class Post(BaseModel):
    title: str
    content: str
    publish: bool = True
    rating: Optional[int] = None

@app.get("/")
async def root():
    return {"message": "Hello World"}


# @app.get("/posts") # Follow best practices "/posts"
# def get_posts():
#     return {"data": "This is your posts"}

# Posts -V1 ; No Base Model
# @app.post("/createposts")
# def create_post(payload: dict = Body(...)):
#     print(payload)
#     result = {"Message": "successfully created a post"}
#     #result  = {"new_post": f"Title {payload['title']}. Content: {payload['content']}"}
#     return result


# @app.post("/createposts")
# def create_post(new_post: Post):
#     # print(new_post)
#     # print(new_post.title)
#     # print(new_post.publish)
#     #result  = {"new_post": f"Title {payload['title']}. Content: {payload['content']}"}
#     new_dictionary = new_post.model_dump()
#     print(new_dictionary)
#     result  = {"new_post": "New data for the post"}
#     result  = {"new_post": new_dictionary}    
#     return result

my_posts = [{"title": "title of post 1", "content": "content of post 1", "id": 1}, 
            {"title": "favorite foods", "content": "I like pizza", "id": 2}]


@app.get("/posts") # Follow best practices "/posts"
def get_posts():
    return {"data": my_posts}

@app.post("/posts") # Follow best practices "/posts"
def create_post(new_post: Post):
    # print(new_post)
    # print(new_post.title)
    # print(new_post.publish)
    #result  = {"new_post": f"Title {payload['title']}. Content: {payload['content']}"}
    # new_dictionary = new_post.model_dump()
    # print(new_dictionary)
    # result  = {"new_post": "New data for the post"}
    # result  = {"new_post": new_dictionary}    
    return {"data": my_posts}


################################################################################
# VERSION 2 BEFORE CLEAN UP
################################################################################

from fastapi import FastAPI, Response, status, HTTPException
from fastapi.params import Body
from pydantic import BaseModel
from typing import Optional
from random import randrange

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


################################################################################
# VERSION 3 - Connecting to Psygopg2 AND Exiting the program. 
################################################################################

while True:
    try:
        conn = psycopg2.connect(host = p_host, dbname = p_database, user = p_user, password = p_password, port = p_port, cursor_factory=RealDictCursor)
        cursor = conn.cursor
        print("Database connection was successful")
        break
    except Exception as error:
        # print("Connecting to database failed")
        # print("Error: ", error)
        time.sleep(2) # wait 2 seconds before retrying
        raise SystemExit(f"Connecting to database failed \nError: {error}")
        #sys.exit()

## Version 2 that retries twice more before exiting

retry_count = 0
max_retries = 2


while retry_count <= max_retries:
    try:
        conn = psycopg2.connect(host = p_host, dbname = p_database, user = p_user, password = p_password, port = p_port, cursor_factory=RealDictCursor)
        cursor = conn.cursor
        print("Database connection was successful")
        break
    except Exception as error:
        print(f"Attempt {retry_count + 1} failed: {error}")
        retry_count += 1
        if retry_count > max_retries:
            message = f"Connecting to database failed after {max_retries + 1} attempts\nError: {error}"
            print(message)
            sys.exit(1)        
        time.sleep(2) # wait 2 seconds before retrying
        # raise SystemExit(f"Connecting to database failed \nError: {error}")
        #sys.exit()      

#SIMPLIEST Connection String

try:
    conn = psycopg2.connect(host = p_host, dbname = p_database, user = p_user, password = p_password, port = p_port, cursor_factory=RealDictCursor)
    cursor = conn.cursor
    print("Database connection was successful")
except Exception as error:
    raise SystemExit(f"Connecting to database failed \nError: {error}")
################################################################################
# VERSION 4 - Psycopg2
###############################################################################

@app.get("/posts")
def get_posts():
    cursor.execute("""
                          SELECT * FROM public."POSTS"
                          """)
    post = cursor.fetchall()
    return post

# Version 1
# @app.post("/posts", status_code=status.HTTP_201_CREATED)
# def create_post(new_post: Post):
#     cursor.execute(""" INSERT INTO  public."POSTS" ("TITLE", "CONTENT", "published") VALUES (%s, %s, %s)""", ('py_post', 'Posting from python', 'false'))
#     conn.commit()
#     cursor.execute("""
#                           SELECT * FROM public."POSTS"
#                           """)
#     post = cursor.fetchall()    
#     return post


# My Experiment - Multiple Posts
# @app.post("/posts", status_code=status.HTTP_201_CREATED)
# def create_post(new_post: Post):
#     query = """ INSERT INTO public."POSTS" ("TITLE", "CONTENT") 
#                 VALUES (%s, %s) """
#     data = [
#         ("458", 'Posting from Java-58'),
#         ('py_post_258', 'Posting from JavaScript_908'),                        
#     ]
#     cursor.executemany(query, data) # Doesn't work with "RETURNING *"
#     # conn.commit()
#     select_query = """
#                 SELECT * FROM public."POSTS"
#                                 """
#     cursor.execute(select_query)

#     post = cursor.fetchall()   
#     conn.close()     
#     return post


# Single Post
@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_post(new_post: Post):
    cursor.execute (""" INSERT INTO public."POSTS" ("TITLE", "CONTENT", "published") VALUES (%s, %s, %s) RETURNING * """, (new_post.title, new_post.content, new_post.published))
    # query =  (""" INSERT INTO public."POSTS" ("TITLE", "CONTENT", "published") VALUES (%s, %s, %s) RETURNING * """, (new_post.title, new_post.content, new_post.published))    
    # data = [
    #     (new_post.title, new_post.content, new_post.published),
    #     # ('py_post_25', 'Posting from JavaScript_90'),                        
    # ]
    # cursor.executemany(query, data) -- Doesn't work either
    # cursor.execute(query, data) -- Doesn't work either    
    # cursor.execute(query) -- Doesn't Work
    # conn.commit()
    # select_query = """
    #             SELECT * FROM public."POSTS"
    #                             """
    # cursor.execute(select_query)

    post = cursor.fetchone()   
    # conn.commit()    
    # conn.close()     
    return post        