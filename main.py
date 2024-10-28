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


@app.get("/posts")
def get_posts():
    return {"data": "This is your posts"}

# Posts -V1 ; No Base Model
# @app.post("/createposts")
# def create_post(payload: dict = Body(...)):
#     print(payload)
#     result = {"Message": "successfully created a post"}
#     #result  = {"new_post": f"Title {payload['title']}. Content: {payload['content']}"}
#     return result


@app.post("/createposts")
def create_post(new_post: Post):
    # print(new_post)
    # print(new_post.title)
    # print(new_post.publish)
    #result  = {"new_post": f"Title {payload['title']}. Content: {payload['content']}"}
    new_dictionary = new_post.model_dump()
    print(new_dictionary)
    result  = {"new_post": "New data for the post"}
    result  = {"new_post": new_dictionary}    
    return result