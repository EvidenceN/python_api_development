from fastapi import FastAPI
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

@app.get("/")
async def root():
    return {"message": "Hello World"}


my_posts = [{"title": "title of post 1", "content": "content of post 1", "id": 1}, 
            {"title": "favorite foods", "content": "I like pizza", "id": 2}]


@app.get("/posts")
def get_posts():
    return {"data": my_posts}

@app.post("/posts")
def create_post(new_post: Post): 
    new_post_dict = new_post.model_dump()
    print(new_post_dict)
    new_post_dict['id'] = randrange(0, 100000) # manually adding new id to posts in th absence of dictionaries
    print(new_post_dict)    
    my_posts.append(new_post_dict)
    print(my_posts)
    return {"data": new_post_dict}


@app.get("/posts/{id}")
def get_post(id):
    print(id)
    return {"data": f"this is your post {id}"}

# My Experiment
@app.post("/posts/{id}")
def send_post(id, new_post: Post):
    print(id)
    new_post_dict = new_post.model_dump()
    print(new_post_dict)
    new_post_dict['id'] = id # manually adding new id to posts in th absence of dictionaries
    print(new_post_dict)    
    my_posts.append(new_post_dict)
    print(my_posts)    
    return {"data": f'Your post has been sent'}