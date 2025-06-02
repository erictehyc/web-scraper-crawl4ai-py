
import json
import requests
import pandas as pd
import asyncio
from crawl4ai import (
    AsyncWebCrawler,
    BrowserConfig,
    ProxyConfig,
    CrawlerRunConfig,
    DefaultMarkdownGenerator,
    PruningContentFilter,
    CrawlResult,
    LLMExtractionStrategy,
    LLMConfig,
    RateLimiter,
)
import os
from dotenv import load_dotenv
from models.JobModel import JobModel
load_dotenv()


async def main():

    OCCUPATION = 'developer'
    LOCATION = 'kuala-lumpur'
    SALARY_RANGE = '9000-15000'
    SALARY_TYPE = 'monthly'  # monthly or annually
    DATE_RANGE = '5'  # last posted x days ago

    # # Set up proxy configuration
    proxy = f"http://{os.getenv('PROXY_USERNAME')}:{os.getenv('PROXY_PASSWORD')}@{os.getenv('PROXY_SERVER')}"
    print(proxy)

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

    proxy_info = {
        "server": 'https://gate.decodo.com:10001',
        "username": os.getenv("PROXY_USERNAME"),
        "password": os.getenv("PROXY_PASSWORD")
    }

    # https://github.com/unclecode/crawl4ai/issues/993

    proxy_config = ProxyConfig(
        server=proxy_info["server"], username=proxy_info["username"], password=proxy_info["password"])

    browser_config = BrowserConfig(
        headless=False,
        verbose=True,
        # proxy=proxy,
        proxy_config=proxy_config,
    )

    # Create a RateLimiter with custom settings
    rate_limiter = RateLimiter(
        base_delay=(30.0, 60.0),  # Random delay between 30-60 seconds
        max_delay=60.0,         # Cap delay at 30 seconds
        max_retries=2,          # Retry up to 5 times on rate-limiting errors
        rate_limit_codes=[429, 503]  # Handle these HTTP status codes
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
            overlap_rate=0.1,
            chunk_token_threshold=5000,
            apply_chunking=True,

            extraction_type="schema",
            schema=JobModel.model_json_schema(),
            instruction="Extract objects with 'job_id', 'job_title', 'company', 'expected_salary', 'location', 'short_description', 'listed_on' and 'link' from the job posting. 'listed_on' should be transformed from 'X days from' to a date string in the format 'DD-MM-YYYY', calculated based from today's date.",
            # html / markdown / fit_markdown (from PruningContentFilter)
            input_format="fit_markdown",
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

        rate_limiter = RateLimiter(
            base_delay=(30.0, 60.0),  # Random delay between 30-60 seconds
            max_delay=60.0,         # Cap delay at 60 seconds
            max_retries=2,          # Retry up to 2 times on rate-limiting errors
            rate_limit_codes=[429, 503]  # Handle these HTTP status codes
        )

        print(f"Using LLM Model: {os.getenv('LLM_MODEL')}")

        all_items = []
        page = 1
        while True:

            paged_url = f"https://my.jobstreet.com/{OCCUPATION}-jobs/in-{LOCATION}?salaryrange={SALARY_RANGE}&salarytype={SALARY_TYPE}&daterange={DATE_RANGE}&page={page}"

            try:
                # return json content from the crawler
                result: CrawlResult = await crawler.arun(
                    url=paged_url,
                    config=crawler_config,
                    # dispatcher=rate_limiter,  # Use the rate limiter
                )  # type: ignore

                print(f"Crawled page {page} with result: {result}")
                if result.success is False:
                    print(
                        f"Failed to crawl page {page}: {result.error_message}")
                    break
                elif result.extracted_content is None:
                    print(f"No extracted content on page {page}. Stopping.")
                    break
                else:
                    print(f"Successfully crawled page {page}.")
                    # The extracted content is = JSON
                    data = json.loads(result.extracted_content or "[]")
                    print("Extracted items:", data)
                    if not data:
                        print(f"No more data found on page {page}. Stopping.")
                        break

                    all_items.extend(data)
                    print(f"Page {page} extracted {len(data)} items.")
                    page += 1

            # Example of errors - rate limit exceeded, no more data, etc.
            except Exception as e:
                print(f"Error on page {page}: {e}")
                break

        # Save to JSON once completed
        if all_items:
            with open("output.json", "w", encoding="utf-8") as f:
                json.dump(all_items, f, indent=4, ensure_ascii=False)
            print(f"Saved {len(all_items)} items to output.json")

            # convert to csv
            df = pd.DataFrame(all_items)
            df.to_csv("output.csv", index=False)
            print(f"Saved {len(all_items)} items to output.csv")

            # 6. Show LLM usage stats
            print("LLM Usage Stats:")
            extraction_strategy.show_usage()  # prints token usage
        else:
            print("No items extracted.")

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
