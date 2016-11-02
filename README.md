#Capstone Project: Analyzing Employer Trends
___
## Overview:
The goal of this project is to analyze topics in Glassdoor's employee reviews, in order to understand what employees like and dislike about their employers. To answer this question, I will need to accomplish a few things:
- Identify employers that have significantly high and low scores, and that have enough reviews to collect a large corpus.
- Collect employee review data for each of the employers that I have identified as a target for analysis.
- Analyze a corpus of positive feedback and a corpus of negative feedback using NLP techniques. Identify topics and their relative importances or frequency.

___
#### Gathering Data
In order to choose which employers to focus on for this analysis, I utilized Glassdoor's Employers API to pull all the employers in their database. In order to gather a large enough corpus of reviews, I chose to focus on companies with at least 100 reviews.

<p align="center">
  <img src="images/employers_with_at_least_100_reviews.png">
</p>

Since the goal of this project is to identify trends in what makes an employer especially great (or not so great), I chose to focus even further on companies with a score either below the 5th percentile or above the 95th percentile.

<p align="center">
  <img src="images/sig_scores.png">
</p>

___
#### Creating a Corpus
Once I identified which employers were good candidates for analysis, I needed to gather all the reviews for each company. Specifically, the "Pros" for each highly rated company as well as the "Cons" for each poorly rated company. Since Glassdoor does not have an API through which I could download reviews, it became a web scraping problem.

#### Challenges
The biggest overall challenge in this project was by far the data collection. Glassdoor is quite sophisticated in their bot detection, which makes it difficult to do any sort of scraping on their site. I ran into roadblocks in both phases of my data collection.

###### *API for Employer Data*
While utilizing the Glassdoor API in the first phase, I ran into 2 main problems while downloading employer data.
- The first was being immediately blocked for having no user-agent in the header associated with my url requests. After I gave my requests a header with a Mozilla user-agent, I was able to begin downloading employer data.
- After fixing the header issue, I ran into a few more HTTP 403 errors, but I was able to bypass these by sending another request for the same page after a short timeout.

###### *Scraping Review Text*
Building a scraper to parse through each page for each employer and grab the relevant information was relatively straightforward; however, I did run into one major roadblock:
<p align="center">
  <img src="images/captcha_example.png"><br />
  <b>THE DREADED CAPTCHA</b>
</p>
- I attempted many workarounds to allow me to automatically solve CAPTCHA images, but to no avail. The most promising package out there is [tesseract](https://github.com/tesseract-ocr/tesseract) and its python integration `pytesseract`. Given more time to work on this project, I would spend more time training tesseract to solve this problem.

- The solution I implemented was a pause in my scraper that would wait for me to manually solve the captcha in the Selenium browsers, and once I had done that, resume the scrape. Since I only encountered these challenge images every 10 minutes or so, it made sense just to babysit the process until I had collected all the data I needed.

###### *Volume of Data*
The final challenge to gathering as many reviews as I wanted was the sheer volume of data that I collected. In order to get all the reviews for all the employers that I wanted to analyze, I had to distribute the workload between five computers. After splitting the data into manageable chunks, each machine ran the threaded scraper for about 10 hours.
