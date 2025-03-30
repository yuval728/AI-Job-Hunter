from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from aijobhunter.crew import AIjobhunter

app = FastAPI()

class JobApplicationInputs(BaseModel):
    job_posting_url: str
    github_url: str
    personal_website: str = None  # Optional field

@app.post("/apply")
async def apply_for_job(inputs: JobApplicationInputs):
    try:
        ai_job_hunter = AIjobhunter(file_path="./knowledge/CV_YuvalMehta.pdf")
        output = ai_job_hunter.crew().kickoff(inputs=inputs.model_dump())
        return {"status": "success", "output": output}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")

@app.get("/")
async def root():
    return {"message": "AIJobHunter Agent API"}