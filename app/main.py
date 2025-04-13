from fastapi import FastAPI
from fastapi.responses import FileResponse

app = FastAPI()
page_root = '/'
page_calc = '/calculate'

@app.get(page_root)
async def root():
    return {"message": "Main page"}

@app.get(page_calc)
async def root():
    return FileResponse("../template/calculate.html")

@app.get('/fuckyou')
async def blabla():
    return {"message1": "fuck you"}

@app.post('/calculate')
async def calculate(num1: int, num2: int):
    return {f'{num1+num2}'}