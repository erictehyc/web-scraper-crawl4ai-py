
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
    JsonXPathExtractionStrategy,
)
import os
from dotenv import load_dotenv
from models.JobModel import JobModel
from models.xpath_schema import job_listing_schema
from datetime import datetime, timedelta
from helper.send_email import send_email
load_dotenv()

BASE_URL = "https://my.jobstreet.com"
OCCUPATION = 'react-developer'
LOCATION = 'singapore'
SALARY_RANGE = '0-15000'
SALARY_TYPE = 'monthly'  # monthly or annually
DATE_RANGE = '3'  # last posted x days ago


def process_json_data(data, base_url):
    # Process the JSON data as needed

    for item in data:
        # prepend base URL to job URLs
        if 'jobUrl' in item and item['jobUrl']:
            item['jobUrl'] = f"{base_url}{item['jobUrl']}"
        # Convert days ago (3d) to a date format
        if 'dateListed' in item and item['dateListed']:
            try:
                now = datetime.now()
                relative_str = item['dateListed'].strip().lower()
                if "d ago" in relative_str:
                    days = int(relative_str.replace("d ago", "").strip())
                    date = now - timedelta(days=days)
                elif "h ago" in relative_str:
                    hours = int(relative_str.replace("h ago", "").strip())
                    date = now - timedelta(hours=hours)
                else:
                    # fallback: return today
                    date = now
                item['dateListed'] = date.strftime("%d/%m/%Y")
            except ValueError:
                item['dateListed'] = None

    return data


async def main():

    # # Set up proxy configuration
    proxy = f"http://{os.getenv('PROXY_USERNAME')}:{os.getenv('PROXY_PASSWORD')}@{os.getenv('PROXY_SERVER')}"
    print(f'Using proxy: {proxy}')

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

    # Solve Proxy issue - https://github.com/unclecode/crawl4ai/issues/993
    proxy_config = ProxyConfig(
        server=proxy_info["server"], username=proxy_info["username"], password=proxy_info["password"])

    browser_config = BrowserConfig(
        headless=False,
        verbose=True,
        # proxy=proxy,
        proxy_config=proxy_config,
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

        # refer to https://docs.crawl4ai.com/extraction/no-llm-strategies/
        extraction_strategy = JsonXPathExtractionStrategy(
            job_listing_schema, verbose=True)

        crawler_config = CrawlerRunConfig(
            # cache_mode=CacheMod.BYPASS,

            markdown_generator=DefaultMarkdownGenerator(
                content_filter=PruningContentFilter()
            ),
            css_selector="article[data-testid='job-card']",
            extraction_strategy=extraction_strategy,
        )

        all_items = []
        all_results = []
        page = 1
        while True:

            paged_url = f"{BASE_URL}/{OCCUPATION}-jobs/in-{LOCATION}?salaryrange={SALARY_RANGE}&salarytype={SALARY_TYPE}&daterange={DATE_RANGE}&page={page}"

            try:
                # return json content from the crawler
                result: CrawlResult = await crawler.arun(
                    url=paged_url,
                    config=crawler_config,
                    # dispatcher=rate_limiter,  # Use the rate limiter
                )  # type: ignore

                # remove html from result
                result_dict = result.model_dump()
                # for key in ["html", "cleaned_html", "fit_html"]:
                #     result_dict.pop(key, None)

                print(
                    f"Crawled page {page} with status code {result.status_code}")
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
                    # print("Extracted items:", data)
                    if not data:
                        print(f"No more data found on page {page}. Stopping.")
                        break

                    all_items.extend(data)
                    all_results.append(result_dict)
                    print(f"Page {page} extracted {len(data)} items.")
                    page += 1

            # Example of errors - rate limit exceeded, no more data, etc.
            except Exception as e:
                print(f"Error on page {page}: {e}")
                break

        # Save to JSON once completed
        if all_items:

            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"Processing completed at {now}. Saving results...")
            # Save results to JSON (include status_code, error_message, etc.)
            with open(f"result-{now}.json", "w", encoding="utf-8") as f:
                json.dump(all_results, f, indent=4, ensure_ascii=False)
            print(f"Saved {len(all_results)} results to results.json")

            # Save data to JSON
            processed_json = process_json_data(all_items, BASE_URL)
            with open(f"output-{now}.json", "w", encoding="utf-8") as f:
                json.dump(processed_json, f, indent=4, ensure_ascii=False)
            print(f"Saved {len(processed_json)} items to output.json")

            # convert to csv
            df = pd.DataFrame(processed_json)
            df.to_csv(
                f"output-{now}.csv", index=False)
            print(f"Saved {len(processed_json)} items to output.csv")

            # send email (csv file)
            if os.getenv("SEND_EMAIL") == "True":
                print("Sending email with results...")
                send_email(filename=f"output-{now}.csv")

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
