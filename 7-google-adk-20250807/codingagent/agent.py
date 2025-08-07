from google.adk.agents import Agent
from google.adk.agents import SequentialAgent, ParallelAgent
from google.adk.models.lite_llm import LiteLlm

#model_ollama = LiteLlm("ollama/qwen3:8b")
model_openrouter = LiteLlm(
    baseurl ="https://openrouter.ai/api/v1", 
    model = "openai/gpt-oss-20b:free", 
    api_key = "")


model_gemini = "gemini-2.5-pro"
model_gemini_reviwer = "gemini-2.5-flash-lite"

code_writer_agent= Agent(
        name ="codewriteragent",
        description="writes a python code based on specification",
        model=model_gemini,
        instruction=""""You are a Python Code Generator.
        Based *only* on the user's request, write Python code that fulfills the requirement.
        Output *only* the complete Python code block, enclosed in triple backticks (```python ... ```). 
        Do not add any other text before or after the code block.
        """,
        output_key="generated_code" # state["generated_code" = "python code"]
)

code_reviewer_agent= Agent(
    name ="codereviweragent",
    model = model_gemini_reviwer,
    description="review code and provide feedback",
    instruction="""You are an expert Python Code Reviewer. 
    Your task is to provide constructive feedback on the provided code.

    **Code to Review:**
    ```python
    {generated_code}
    ```

**Review Criteria:**
1.  **Correctness:** Does the code work as intended? Are there logic errors?
2.  **Readability:** Is the code clear and easy to understand? Follows PEP 8 style guidelines?
3.  **Efficiency:** Is the code reasonably efficient? Any obvious performance bottlenecks?
4.  **Edge Cases:** Does the code handle potential edge cases or invalid inputs gracefully?
5.  **Best Practices:** Does the code follow common Python best practices?

**Output:**
Provide your feedback as a concise, bulleted list. Focus on the most important points for improvement.
If the code is excellent and requires no changes, simply state: "No major issues found."
Output *only* the review comments or the "No major issues" statement.
""",
output_key="review_comments"

)

code_refactorer_agent = Agent(
    name = "refactoreragent",
    model = model_gemini_reviwer,
    description= "Refactors the code based on the review",
    instruction="""You are a Python Code Refactoring AI.
Your goal is to improve the given Python code based on the provided review comments.

  **Original Code:**
  ```python
  {generated_code}
  ```

  **Review Comments:**
  {review_comments}

**Task:**
Carefully apply the suggestions from the review comments to refactor the original code.
If the review comments state "No major issues found," return the original code unchanged.
Ensure the final code is complete, functional, and includes necessary imports and docstrings.

**Output:**
Output *only* the final, refactored Python code block, enclosed in triple backticks (```python ... ```). 
Do not add any other text before or after the code block.
""",
output_key="refactored_code"

)


root_agent = SequentialAgent(
    name = "codepipelineagent",
    description= " Exceutes a sequence of agents like coding , reviewer and refactor",
    sub_agents=[code_writer_agent,code_reviewer_agent,code_refactorer_agent]
)