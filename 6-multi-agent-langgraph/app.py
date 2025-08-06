import os
from dotenv import load_dotenv
from typing import TypedDict, List
from langgraph.graph import StateGraph, END
from agents.research_agent import research_agent
from agents.writing_agent import writing_agent
from agents.proofreading_agent import proofreading_agent
from agents.publishing_agent import publishing_agent
from config import ORGANIZATION_NAME, ORGANIZATION_DESCRIPTION

load_dotenv()

class GraphState(TypedDict):
    organization_name: str
    organization_description: str
    urls: List[str]
    research_results: str
    blog_post: str
    final_blog_post: str
    published: bool