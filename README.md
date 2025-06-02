## Set up Crawl4AI with Groq

Go to [Groq](https://groq.com/) and sign up for an account.
Then, follow these steps to set up Crawl4AI with Groq:

1. **Create a Groq API Key**:
   - Go to the Groq dashboard and create an API key.
   - Save the key in a secure place.
2. **Install Crawl4AI**:
   - Open your terminal and run the following command:
     ```bash
     pip install crawl4ai
     ```
3. **Set up the Groq API Key**:
   - Create a file named `.env` in your project directory.
   - Add the following line to the `.env` file:
     ```
     LLM_API_TOKEN=your_groq_api_key_here
     ```
   - Replace `your_groq_api_key_here` with the API key you created in step 1.

## Set up Proxies with Decodo

To set up proxies with Decodo, follow these steps:

1. **Create a Decodo Account**:
   - Go to [Decodo](https://decodo.com/) and sign up for an account.
2. **Get Proxy Credentials**:
   - After logging in, navigate to the "Proxies" section.
   - Create a new proxy and note down the credentials (username and password).
3. **Set up the Proxy in Crawl4AI**:
   - In your `.env` file, add the following lines:
     ```
     PROXY_URL=http://your_proxy_url_here
     PROXY_USERNAME=your_proxy_username_here
     PROXY_PASSWORD=your_proxy_password_here
     ```
   - Replace `your_proxy_url_here`, `your_proxy_username_here`, and `your_proxy_password_here` with the credentials you obtained from Decodo.
4. **Test the Proxy**:
   - You can test the proxy setup by running a simple Python script to ensure it connects through the proxy as detailed in Decodo's documentation.

## Running Jobstreet Web Scraper

To run the Jobstreet web scraper using Crawl4AI, follow these steps:

1. Run the following command in your terminal for LLM-based scraping:

   ```bash
   python scraper.py
   ```

   However, this method is slower and may not be as efficient as using non-LLM-based scraping.
   It will also be limited by the Groq API rate limits.

2. If you want to use non LLM-based scraping (recommended for faster results) which uses XPath selector, run:
   ```bash
    python scraper_without_llm.py
   ```
3. **View the Results**:
   - The results will be saved in a file named `results.json` in the same directory as your script.
   - You can open this file to view the scraped job listings.
   - Parsed data will be in the file `output.json` and `output.csv` in the same directory.
   - The data is in JSON format with the following structure:
     ```json
     {
       "job_title": "Software Engineer",
       "company_name": "Tech Company",
       "location": "New York, NY",
       "salary": "$100,000 - $120,000",
       "description": "Job description goes here.",
       "url": "https://www.jobstreet.com/job/123456"
     }
     ```

## References

[Crawl4AI YT](https://www.youtube.com/watch?v=xo3qK6Hg9AA&t=1487s&ab_channel=Unclecode)  
[Crawl4AI Docs](https://docs.crawl4ai.com/blog/releases/0.6.0/#2-native-table-extraction)  
[Medium Article using Crawl4AI + Groq](https://medium.com/@datajournal/ai-scraper-with-crawl4ai-and-deepseek-94f1e66a14d0)  
[AI with Brandon Hancock - Crawl4AI + Groq](https://www.youtube.com/watch?v=Osl4NgAXvRk&ab_channel=aiwithbrandon)  
[Jan Marshal - Setting up Proxies with Decodo](https://www.youtube.com/watch?v=_rI7IDEGMvk&ab_channel=JanMarshal)
