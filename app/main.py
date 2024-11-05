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
    cursor = conn.cursor()
    print("Database connection was successful")
except Exception as error:
    raise SystemExit(f"Connecting to database failed \nError: {error}")

app = FastAPI()

# Schema. Title str, content str,
class Post(BaseModel):
    title: str
    content: str
    published: bool = True


@app.get("/")
async def root():
    return {"message": "Hello World"}

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


# My Experiment - Multi Post Example
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


# Single Post Example
@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_post(new_post: Post):
    cursor.execute (""" INSERT INTO public."POSTS" ("TITLE", "CONTENT", "published") VALUES (%s, %s, %s) RETURNING * """, (new_post.title, new_post.content, new_post.published))
    post = cursor.fetchone()   
    # conn.commit()    
    # conn.close()     
    return post


# @app.post("/posts/{id}")
# def send_post(id, new_post: Post):
#     print(id)
#     new_post_dict = new_post.model_dump()
#     print(new_post_dict)
#     # manually adding new id to posts in th absence of dictionaries
#     # new_post_dict['id'] = id # no longer needed since it has been added to the pydantic schema model.
#     print(new_post_dict)
#     my_posts.append(new_post_dict)
#     print(my_posts)
#     return {"data": f'Your post has been sent'}


# def find_post(id):
#     for p in my_posts:
#         if p["id"] == id:
#             return p


@app.get("/posts/{id}")
def get_post(id: int):
    cursor.execute(""" SELECT * FROM public."POSTS" 
                   where "ID" = %s """, (str(id),))
    post = cursor.fetchall()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Post {id} not found")
    return {"data": post}

# with HTTP_204_NO_CONTENT ;  Any output in return is not shown.
@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int):   
    cursor.execute(""" DELETE FROM public."POSTS" where "ID" = %s returning *""", (str(id),))
    deleted_post = cursor.fetchall()
    if not deleted_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"This post Id '{id}' doesn't exist")
    return Response(status_code=status.HTTP_204_NO_CONTENT)

# without post
@app.patch("/posts/{id}", status_code=status.HTTP_201_CREATED)
def update_post(id: int):
    cursor.execute("""UPDATE public."POSTS" SET "CONTENT" = %s 
        WHERE "ID" = %s returning *""", ("posting from Nueva York", str(id),))
    updated_post = cursor.fetchall()
    if not updated_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"This post Id '{id}' doesn't exist")
    return {"data": updated_post}


@app.patch("/posts/{id}", status_code=status.HTTP_201_CREATED)
def update_post(id: int, post: Post):
    post.content  = "posting from Nueva York"
    cursor.execute("""UPDATE public."POSTS" SET "CONTENT" = %s 
        WHERE "ID" = %s returning *""", (post.content, str(id),))
    updated_post = cursor.fetchall()
    if not updated_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"This post Id '{id}' doesn't exist")
    return {"data": updated_post}


# Patch while using post.content but not providing a value for post.title. 

# 2 Options. 

# A new basemodel for post.patch or use OPTIONAL for post(basemodel)

# OPTION 1 

# Original Post model
class Post(BaseModel):
    title: str
    content: str
    published: bool = True

# New model specifically for content updates
class PostContentUpdate(BaseModel):
    content: str

# Option 2 

class Post(BaseModel):
    title: Optional[str] = None  # Set title as optional
    content: str
    published: bool = True