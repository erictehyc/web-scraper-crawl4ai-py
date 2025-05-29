from crawl4ai.extraction_strategy import LLMExtractionStrategy, LLMConfig
from pydantic import BaseModel
import os
from crawl4ai import CrawlerRunConfig, CacheMode, DefaultMarkdownGenerator, PruningContentFilter


class JobCrawlerModel(BaseModel):
    """
    Represents the data extracted from a job posting.
    This model is used to define the structure of the data that will be extracted
    from the job postings using AI-powered extraction strategies.
    It includes fields for the job title, description, salary, location, and other relevant details.
    This model is used in conjunction with the CrawlerRunConfig to configure the web crawler
    for extracting structured data from job postings.

    Args:
        BaseModel (_type_): _description_
    """

    job_id: str
    job_title: str
    company: str
    expected_salary: str
    location: str
    short_description: str
    link: str

    extraction_strategy: LLMExtractionStrategy
    crawler_config: CrawlerRunConfig

    # Use DeepSeek for AI Parsing
    # Modify scraper.py to include AI-powered extraction:

    # newLLMConfig = LLMConfig(
    #     provider=os.getenv(
    #         "LLM_MODEL") or "meta-llama/llama-4-scout-17b-16e-instruct",  # type: ignore
    #     api_token=os.getenv("LLM_API_TOKEN")
    # )
    # extraction_strategy = LLMExtractionStrategy(
    #     llm_config=newLLMConfig,
    #     extraction_type="schema",
    #     instruction="Extract all job objects with 'job_id', 'job_title', 'company', 'expected_salary', 'location', 'short_description' and 'link' from the job posting.",
    #     input_format="markdown",
    #     verbose=True
    # )

    # crawler_config = CrawlerRunConfig(
    #     cache_mode=CacheMode.BYPASS,
    #     markdown_generator=DefaultMarkdownGenerator(
    #         content_filter=PruningContentFilter()
    #     ),
    #     css_selector="article[data-testid='job-card']"
    #     # extraction_strategy=extraction_strategy,
    # )
