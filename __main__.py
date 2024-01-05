import uvicorn

if __name__ == "__main__":
    uvicorn.run("naomi:app", env_file=".env")
