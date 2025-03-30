#!/usr/bin/env python
import sys
import warnings

from datetime import datetime

from aijobhunter.crew import AIjobhunter

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# This main file is intended to be a way for you to run your
# crew locally, so refrain from adding unnecessary logic into this file.
# Replace with inputs you want to test with, it will automatically
# interpolate any tasks and agents information

def run():
    """
    Run the crew.
    """
    job_application_inputs = {
        # 'job_posting_url': 'https://amazon.jobs/en/jobs/2821385/worldwide-specialist-solutions-architect-genai',
        # "job_posting_url": "https://jobs.lever.co/Federato/ca664080-ae5b-4cac-88f9-137d3d9f0c78",
        "job_posting_url": "https://www.glassdoor.co.in/job-listing/ai-applications-engineer-prolegion-private-limited-JV_IC2851180_KO0,24_KE25,50.htm?jl=1009653091477&utm_campaign=google_jobs_apply&utm_source=google_jobs_apply&utm_medium=organic",
        "github_url": "https://github.com/Yuval728",
        # 'personal_website': 'your_personal_website_url' # Replace with your personal website UR,
    }
    
    try:
        
        ai_job_hunter = AIjobhunter(file_path="./knowledge/CV_YuvalMehta.pdf")
        # ai_job_hunter.set_tools(file_path="../knowledge/CV_YuvalMehta.pdf")
        output = ai_job_hunter.crew().kickoff(inputs=job_application_inputs)
        # Ai().crew().kickoff(inputs=job_application_inputs)
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")


def train():
    """
    Train the crew for a given number of iterations.
    """
    inputs = {
        "topic": "AI LLMs"
    }
    try:
        AIjobhunter().crew().train(n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")

def replay():
    """
    Replay the crew execution from a specific task.
    """
    try:
        AIjobhunter().crew().replay(task_id=sys.argv[1])

    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")

def test():
    """
    Test the crew execution and returns the results.
    """
    inputs = {
        "topic": "AI LLMs"
    }
    try:
        AIjobhunter().crew().test(n_iterations=int(sys.argv[1]), openai_model_name=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while testing the crew: {e}")
