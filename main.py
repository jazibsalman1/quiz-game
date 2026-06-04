from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn
import random
import requests

app = FastAPI()

# Static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

# Store last quiz temporarily (per user/session you can improve later)
last_quiz = []

# Home page
@app.get("/", response_class=HTMLResponse)
def index_page(request: Request):
    return templates.TemplateResponse(request,"index.html", {"request": request})

# Quiz page
@app.get("/quiz", response_class=HTMLResponse)
def quiz_page(request: Request):
    global last_quiz
    url = "https://opentdb.com/api.php?amount=10&type=multiple"
    response = requests.get(url)
    data = response.json()

    questions = []
    for idx, item in enumerate(data["results"]):
        options = item["incorrect_answers"] + [item["correct_answer"]]
        random.shuffle(options)
        questions.append({
            "id": idx,
            "question": item["question"],
            "options": options,
            "answer": item["correct_answer"]
        })

    last_quiz = questions  # save for scoring

    return templates.TemplateResponse(request,"quiz.html", {
        "request": request,
        "questions": questions
    })

@app.post("/submit", response_class=HTMLResponse)
async def submit_quiz(request: Request):
    form = await request.form()

    score = 0
    results = []

    for q in last_quiz:
        user_answer = form.get(f"answer_{q['id']}")

        is_correct = user_answer == q["answer"]

        if is_correct:
            score += 1

        results.append({
            "question": q["question"],
            "user_answer": user_answer,
            "correct_answer": q["answer"],
            "is_correct": is_correct
        })

    return templates.TemplateResponse(request,"result.html", {
        "request": request,
        "score": score,
        "total": len(last_quiz),
        "results": results
    })

# Run app
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)