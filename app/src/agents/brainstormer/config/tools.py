from langchain_core.tools import tool
from langchain_cerebras import ChatCerebras
from dotenv import load_dotenv
from pathlib import Path
import os
import textwrap


ROOT_DIR = Path(__file__).resolve().parents[5]
ENV_PATH = ROOT_DIR / ".env"
load_dotenv(dotenv_path=ENV_PATH)


def get_config():

    llm_api_key = os.getenv("CEREBRAS_API_KEY")
    ggl_api_key = os.getenv("GOOGLE_SEARCH_API_KEY")
    cx_id = os.getenv("SEARCH_ENGINE_ID")
    return llm_api_key, ggl_api_key, cx_id


def extract_main_idea(prompt: str) -> str:
    """
    Extract the main idea of the project from the given prompt.
    This function will provide a string contraining the core concept of the project
    without any technical details or implementation specifics that might be present in the prompt.
    """

    llm_api_key, _, _ = get_config()
    summarizer = ChatCerebras(
        model="llama3.1-8b",
        temperature=0,
        timeout=None,
        max_retries=5,
        api_key=llm_api_key,
    )

    main_idea = summarizer.invoke(
        f"Extract the main idea from the following text: {prompt}"
    )

    return main_idea.content


def extract_tech_details(prompt: str) -> str:
    """
    Extract the technical details of the project from the given prompt.
    This function will provide a string containing the technical aspects, tools, and technologies
    that are relevant to the project.
    """

    llm_api_key, _, _ = get_config()
    summarizer = ChatCerebras(
        model="llama3.1-8b",
        temperature=0,
        timeout=None,
        max_retries=5,
        api_key=llm_api_key,
    )

    prompt = r"""
    Extract the technical details from the following text: {prompt}
    Structure the output in the following format:
    - target platforms (e.g., web, mobile, desktop): {target_platforms}
    - programming languages: {programming_languages}
    - frameworks: {frameworks}
    - libraries: {libraries}
    - techstack: {techstack}
    - other relevant details: {other_technologies}
    """
    prompt = textwrap.dedent(prompt)

    tech_details = summarizer.invoke(prompt)

    return tech_details.content


@tool
def get_features_ideas(prompt: str) -> str:
    """
    Generate a list of features and ideas based on the main idea and technical details.
    This function will provide a string containing a list of potential features or ideas
    that can be derived from the main idea and technical details.
    """

    llm_api_key, _, _ = get_config()
    summarizer = ChatCerebras(
        model="llama3.1-8b",
        temperature=0,
        timeout=None,
        max_retries=5,
        api_key=llm_api_key,
    )

    prompt = f"""
    Generate a list of features and ideas based on the main idea
    while respecting the limitations of the provided technical details.
    Main Idea: {extract_main_idea(prompt)}
    Technical details: {extract_tech_details(prompt)}
    """
    prompt = textwrap.dedent(prompt)

    features_ideas = summarizer.invoke(prompt)

    return features_ideas.content
