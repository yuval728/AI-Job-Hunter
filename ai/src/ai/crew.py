from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import SerperDevTool, ScrapeWebsiteTool, FileReadTool, PDFSearchTool


@CrewBase
class Ai():
	"""Ai crew"""

	agents_config = 'config/agents.yaml'
	tasks_config = 'config/tasks.yaml'


	llm = LLM(
		model='groq/llama-3.3-70b-versatile',
		temperature=0.2,
	)
	
	manager_llm = LLM(
		model='groq/qwen-2.5-32b',
		temperature=0.2,
	)
 
	def set_tools(self, file_path):
		self.search_tool = SerperDevTool()
		self.scrape_tool = ScrapeWebsiteTool()
		self.read_resume = FileReadTool(file_path)
		self.semantic_search_job = PDFSearchTool(
			pdf=file_path,
			config=dict(
				llm=dict(
					provider="groq",
					config=dict(
						model="mixtral-8x7b-32768",
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
			config=self.agents_config['researcher'],
			verbose=True,
			llm=self.llm,
			tools=[self.search_tool, self.scrape_tool],
		)

	@agent
	def profiler(self) -> Agent:
		return Agent(
			config=self.agents_config['profiler'],
			verbose=True,
			llm=self.llm,
			tools=[self.search_tool, self.scrape_tool, self.read_resume, self.semantic_search_job], 
		)

	@agent
	def resume_strategist(self) -> Agent:
		return Agent(
			config=self.agents_config['resume_strategist'],
			verbose=True,
			llm=self.llm,
			tools=[self.search_tool, self.scrape_tool, self.read_resume, self.semantic_search_job],
		)
  
	@agent
	def interview_preparer(self) -> Agent:
		return Agent(
			config=self.agents_config['interview_preparer'],
			verbose=True,
			llm=self.llm,
			tools=[self.search_tool, self.scrape_tool, self.read_resume, self.semantic_search_job],
		)
  

	@task
	def research_task(self) -> Task:
		return Task(
			config=self.tasks_config['research_task'],
			agent=self.researcher,
			async_execution=True,
		)

	@task
	def profile_task(self) -> Task:
		return Task(
			config=self.tasks_config['profile_task'],
			agent=self.profiler,
			async_execution=True,
		)
  
	@task
	def resume_strategy_task(self) -> Task:
		return Task(
			config=self.tasks_config['resume_strategy_task'],
			agent=self.resume_strategist,
			context=[self.profile_task, self.research_task],
			# async_execution=True,
		)
	
	@task
	def interview_preparation_task(self) -> Task:
		return Task(
			config=self.tasks_config['interview_preparation_task'],
			agent=self.interview_preparer,
			context=[self.resume_strategy_task, self.profile_task, self.research_task],
			# async_execution=True,
		)

	@crew
	def crew(self) -> Crew:
		"""Creates the Ai crew"""
	

		return Crew(
			agents=self.agents, # Automatically created by the @agent decorator
			tasks=self.tasks, # Automatically created by the @task decorator
			# process=Process.sequential,
			verbose=True,
			manager_llm=self.manager_llm
			# process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
		)
