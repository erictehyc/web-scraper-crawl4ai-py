
import json
import requests
import pandas as pd
import asyncio
from crawl4ai import (
    AsyncWebCrawler,
    BrowserConfig,
    CrawlerRunConfig,
    DefaultMarkdownGenerator,
    PruningContentFilter,
    CrawlResult,
    LLMExtractionStrategy,
    LLMConfig,
)
import os
from dotenv import load_dotenv

load_dotenv()


# async def crawl_job_postings(crawler: AsyncWebCrawler, url: str):
#     """
#     Crawl job postings from the given URL using the provided crawler.

#     Args:
#         crawler (AsyncWebCrawler): The web crawler instance.
#         url (str): The URL to crawl for job postings.

#     Returns:
#         list: A list of job postings extracted from the page.
#     """
#     # State Variables for pagination
#     page_number = 1
#     all_jobs = []
#     seen_job_ids = set()

#     # Proxy configuration
#     proxy_config = {
#         "server": os.getenv("PROXY_SERVER"),
#         "username": os.getenv("PROXY_USERNAME"),
#         "password": os.getenv("PROXY_PASSWORD")
#     }

#     browser_config = BrowserConfig(
#         browser_type="chromium",
#         headless=False,
#         verbose=True,
#         proxy_config=proxy_config
#     )

#     # Start the web crawling process
#     async with AsyncWebCrawler(config=browser_config) as crawler:
#         while True:
#             # Construct the URL for the current page
#             current_url = f"{url}&page={page_number}"
#             print(f"Crawling page {page_number}: {current_url}")

#             # Run the crawler on the current URL
#             result: CrawlResult = await crawler.arun(
#                 url=current_url,
#                 config=CrawlerRunConfig(
#                     markdown_generator=DefaultMarkdownGenerator(
#                         content_filter=PruningContentFilter()
#                     ),
#                     extraction_strategy=os.getenv("LLM_MODEL"),
#                     css_selector="article[data-testid='job-card']",
#             )  # type: ignore

#             if not result.success:
#                 print(
#                     f"Failed to crawl page {page_number}: {result.error_message}")
#                 return [], False

#             extracted_data=json.loads(result.extracted_content or "{}")
#             if not extracted_data:
#                 print(f"No data extracted from page {page_number}")
#                 return [], False

#             # Check if the result contains job postings

#             print(f"Successfully crawled page {page_number}")

#             # Extract job postings from the result
#             jobs=result.extracted_content.get("jobs", [])

#             if not jobs:
#                 print("No more jobs found, stopping.")
#                 break

#             # Filter out duplicate jobs based on job_id
#             new_jobs=[job for job in jobs if job["job_id"]
#                         not in seen_job_ids]
#             all_jobs.extend(new_jobs)

#             # Update seen job IDs
#             seen_job_ids.update(job["job_id"] for job in new_jobs)

#             # Increment page number for next iteration
#             page_number += 1

#             # Check if we have reached the end of the job postings
#             if len(new_jobs) < 10:  # Assuming less than 10 jobs means no more pages
#                 print("Less than 10 jobs found, stopping.")
#                 break
#     # Return all collected job postings

#     return all_jobs, True


async def main():

    OCCUPATION = 'farm'
    LOCATION = 'victoria'
    SALARY_RANGE = '1000-2000'

    # # Set up proxy configuration
    print(os.getenv("PROXY_SERVER"))
    proxy = f"http://{os.getenv('PROXY_USERNAME')}:{os.getenv('PROXY_PASSWORD')}@{os.getenv('PROXY_SERVER')}"
    # url = 'https://ip.decodo.com/json'
    # proxies = {
    #     'http': proxy,
    #     'https': proxy
    # }

    # # Test the proxy with a simple request
    # try:
    #     response = requests.get(url, proxies=proxies, timeout=5)
    #     response.raise_for_status()  # Raise an error for bad responses
    #     # Print the response to verify the proxy is working
    #     print(response.json())
    # except requests.RequestException as e:
    #     print(f"Proxy error: {e}")
    #     return  # Exit if the proxy is not working

    # Create an instance of AsyncWebCrawler
    # async with AsyncWebCrawler() as crawler:
    proxy_config = {
        "server": 'http://gate.decodo.com:10001',
        "username": os.getenv("PROXY_USERNAME"),
        "password": os.getenv("PROXY_PASSWORD")
    }

    browser_config = BrowserConfig(
        headless=False,
        verbose=True,
        # proxy=proxy,
        # proxy_config=proxy_config,
    )

    # # Run the crawler on a URL
    async with AsyncWebCrawler(config=browser_config) as crawler:

        # ####### -------- MARKDOWN Crawler -------- ########
        # crawler_config = CrawlerRunConfig(
        #     markdown_generator=DefaultMarkdownGenerator(
        #         content_filter=PruningContentFilter()
        #     ),
        #     css_selector="article[data-testid='job-card']",
        # )
        # # return markdown content from the crawler
        # result: CrawlResult = await crawler.arun(
        #     url="https://my.jobstreet.com/react-developer-jobs/in-Kuala-Lumpur?daterange=7&jobId=84480077&type=standard",
        #     config=crawler_config
        # )  # type: ignore

        # # SAve the raw markdown content to a file
        # with open("raw_markdown.md", "w", encoding="utf-8") as f:
        #     f.write(result.markdown and result.markdown.raw_markdown or "")

        # if not result.success:
        #     print(f"Failed to crawl: {result.error_message}")
        #     return
        # else:
        #     print(
        #         result.markdown[:1000] if result.markdown else "No markdown content extracted.")

        ######## ----------- JSON crawler ----------- ####

        # LLM Extraction Strategy refer to https://docs.crawl4ai.com/extraction/llm-strategies/
        extraction_strategy = LLMExtractionStrategy(
            llm_config=LLMConfig(
                provider=os.getenv("LLM_MODEL"),  # type: ignore
                api_token=os.getenv("LLM_API_TOKEN"),
            ),
            # overlap_rate=0.06,
            # chunk_token_threshold=2000,
            # apply_chunking=True,

            extraction_type="schema",
            # schema="{job_id: str, job_title: str, company: str, expected_salary: str, location: str, short_description: str, link: str}",
            instruction="Extract objects with 'job_id', 'job_title', 'company', 'expected_salary', 'location', 'short_description', 'listed_on' and 'link' from the job posting. 'listed_on' should be transformed from 'X days from' to a date string in the format 'DD-MM-YYYY', calculated based from today's date.",
            input_format="markdown",
            verbose=True
        )

        crawler_config = CrawlerRunConfig(
            # cache_mode=CacheMod.BYPASS,

            markdown_generator=DefaultMarkdownGenerator(
                content_filter=PruningContentFilter()
            ),
            css_selector="article[data-testid='job-card']",
            extraction_strategy=extraction_strategy,
        )

        print(f"Using LLM Model: {os.getenv('LLM_MODEL')}")

        # return json content from the crawler
        result: CrawlResult = await crawler.arun(
            url=f"https://my.jobstreet.com/{OCCUPATION}-jobs/in-{LOCATION}?salaryrange={SALARY_RANGE}&salarytype=monthly",
            # url="https://my.jobstreet.com/react-developer-jobs/in-Kuala-Lumpur?daterange=7&jobId=84480077&type=standard",
            config=crawler_config
        )  # type: ignore

        # print result

        if result.success:
            # The extracted content is = JSON
            data = json.loads(result.extracted_content or "[]")
            print("Extracted items:", data)

            # Save to JSON
            with open("output.json", "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)

            print(f"Saved {len(data)} items to output.json")

            # convert to csv
            df = pd.DataFrame(data)
            df.to_csv("output.csv", index=False)
            print(f"Saved {len(data)} items to output.csv")

            # 6. Show LLM usage stats
            print("LLM Usage Stats:")
            extraction_strategy.show_usage()  # prints token usage
        else:
            print("Error:", result.error_message)

    #     # # Print the number of results
    #     # print(f"Number of results: {len(results)}")
    #     # if not results:
    #     #     print("No results found.")
    #     #     return

    #     # # Parse AI-extracted data
    #     # extracted_data = json.loads(result.extracted_content or "{}")

    #     # # Save to JSON
    #     # with open("output.json", "w", encoding="utf-8") as f:
    #     #     json.dump(extracted_data, f, indent=4)


# Run the async main function
if __name__ == "__main__":
    asyncio.run(main())
