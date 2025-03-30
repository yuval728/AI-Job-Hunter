from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import SerperDevTool, ScrapeWebsiteTool, PDFSearchTool
from aijobhunter.tools.pdf_content_reader import PDFContentReader
import warnings

warnings.filterwarnings("ignore")

llm = LLM(
    # model="groq/llama-3.3-70b-versatile",
    model="ollama/qwen2.5:3b",
    temperature=0.2,
)

manager_llm = LLM(
    model="groq/llama-3.3-70b-versatile",
    temperature=0.2,
)

function_calling_llm = LLM(
    model="ollama/qwen2.5:3b",
    # model="groq/qwen-2.5-32b",
    temperature=0.0,
    seed=71,
)


@CrewBase
class AIjobhunter:
    """Aijobhunter crew"""

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    def __init__(self, file_path):
        self.search_tool = SerperDevTool()
        self.scrape_tool = ScrapeWebsiteTool()
        self.read_resume = PDFContentReader(file_path)
        self.semantic_search_job = PDFSearchTool(
            pdf=file_path,
            config=dict(
                llm=dict(
                    provider="groq",
                    config=dict(
                        model="qwen-2.5-32b",
                        # model="groq/llama-3.3-70b-versatile",
                    ),
                ),
                embedder=dict(
                    provider="huggingface",
                    config=dict(
                        model="BAAI/bge-large-en-v1.5",
                        # task_type="retrieval_document",
                    ),
                ),
            ),
        )

    @agent
    def researcher(self) -> Agent:
        return Agent(
            config=self.agents_config["researcher"],
            verbose=True,
            llm=llm,
            tools=[
                self.scrape_tool,
                self.search_tool,
            ],
            function_calling_llm=function_calling_llm,
        )

    @agent
    def profiler(self) -> Agent:
        return Agent(
            config=self.agents_config["profiler"],
            verbose=True,
            llm=llm,
            tools=[
                # self.search_tool,
                self.scrape_tool,
                self.read_resume,
                self.semantic_search_job,
            ],
            function_calling_llm=function_calling_llm,
        )

    @agent
    def resume_strategist(self) -> Agent:
        return Agent(
            config=self.agents_config["resume_strategist"],
            verbose=True,
            llm=llm,
            tools=[
                self.read_resume,
                self.search_tool,
                self.scrape_tool,
                self.semantic_search_job,
            ],
            function_calling_llm=function_calling_llm,
        )

    @agent
    def interview_preparer(self) -> Agent:
        return Agent(
            config=self.agents_config["interview_preparer"],
            verbose=True,
            llm=llm,
            tools=[
                self.search_tool,
                self.scrape_tool,
                self.read_resume,
                self.semantic_search_job,
            ],
            function_calling_llm=function_calling_llm,
        )

    @task
    def research_task(self) -> Task:
        self.research_task_instance = Task(
            config=self.tasks_config["research_task"],
            async_execution=True,
        )
        return self.research_task_instance

    @task
    def profile_task(self) -> Task:
        self.profile_task_instance = Task(
            config=self.tasks_config["profile_task"],
            async_execution=True,
        )
        return self.profile_task_instance

    @task
    def resume_strategy_task(self) -> Task:
        self.resume_strategy_task_instance = Task(
            config=self.tasks_config["resume_strategy_task"],
            context=[self.profile_task_instance, self.research_task_instance],
            # async_execution=True,
        )
        return self.resume_strategy_task_instance

    @task
    def interview_preparation_task(self) -> Task:
        self.interview_preparation_task_instance = Task(
            config=self.tasks_config["interview_preparation_task"],
            context=[
                self.resume_strategy_task_instance,
                self.profile_task_instance,
                self.research_task_instance,
            ],
            # async_execution=True,
        )
        return self.interview_preparation_task_instance

    @crew
    def crew(self) -> Crew:
        """Creates the Aijobhunter crew"""

        return Crew(
            agents=self.agents,  # Automatically created by the @agent decorator
            tasks=self.tasks,  # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
            manager_llm=manager_llm,
            # process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
        )
