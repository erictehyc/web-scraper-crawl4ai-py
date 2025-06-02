# Used for scraper_without_llm.py
job_listing_schema = {
    "name": "Job Listing via XPath",
    "baseSelector": ".//article[@data-card-type='JobCard']",
    "baseFields": [
        {
            "name": "jobId",
            "type": "attribute",
            "attribute": "data-job-id",
        }
    ],
    "fields": [
        {
            "name": "jobTitle",
            "selector": ".//a[@data-automation='jobTitle']",
            "type": "text"
        },
        {
            "name": "jobCompany",
            "selector": ".//a[@data-automation='jobCompany']",
            "type": "text"
        },
        {
            "name": "salary",
            "selector": ".//span[@data-automation='jobSalary']",
            "type": "text",
            "default": ""
        },
        {
            "name": "location",
            "selector": ".//span[@data-automation='jobCardLocation']",
            "type": "text",
            "default": ""
        },
        {
            "name": "classification",
            "selector": ".//span[@data-automation='jobClassification']",
            "type": "text"
        },
        {
            "name": "subClassification",
            "selector": ".//span[@data-automation='jobSubClassification']",
            "type": "text"
        },
        {
            "name": "jobShortDescription",
            "selector": ".//span[@data-automation='jobShortDescription']",
            "type": "text",
            "default": ""
        },
        {
            "name": "jobUrl",
            "selector": ".//a[@data-automation='job-list-view-job-link']",
            "attribute": "href",
            "type": "attribute"
        },
        {
            "name": "dateListed",
            "selector": ".//span[@data-automation='jobListingDate']",
            "type": "text",
            "default": ""
        }
    ]
}
