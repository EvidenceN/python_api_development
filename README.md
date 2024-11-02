# A Python API Application

Running fast api options
* uvicorn main:app --reload
* uvicorn app.main:app --reload # when application is located inside a folder called app. 
* fastapi run main:app --reload 
* fastapi dev main.py (Auto reloads)
    * (Doesn't work with `fastapi run app.main:app`). Returns with this error
    ```INFO     Using path app.main:app
    INFO     Resolved absolute path app.main:app
    ERROR    Path does not exist app.main:app```

