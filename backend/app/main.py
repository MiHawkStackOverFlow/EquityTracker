from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"message": "EquityTracker backend running on EC2!"}
