import argparse
from collections import namedtuple

import markdownify
import requests
from bs4 import BeautifulSoup
from pathlib import Path
from uuid import uuid4

Job = namedtuple("Job", "company, jd, job_title")


def fetch_data(url):
    return requests.get(url).text


def company_name_cleaner(raw_company_name):
    return raw_company_name.strip().replace(" ", "-")


def get_job_description(text):
    soup = BeautifulSoup(text, "html.parser")
    body = soup.findAll("div", "description__text description__text--rich")
    company = soup.findAll("a", "topcard__org-name-link topcard__flavor--black-link")
    title = soup.findAll("h1",
                         "top-card-layout__title font-sans text-lg papabear:text-xl font-bold leading-open text-color-text mb-0 topcard__title")
    if body:
        return Job(jd=str(body[0]), company=company_name_cleaner(company[0].text), job_title=title[0])
    else:
        raise Exception("Body not found")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("url")
    args = parser.parse_args()
    _text = fetch_data(args.url)
    job = get_job_description(_text)
    markdown_text = markdownify.markdownify(job.jd)
    with open(Path(__file__).parent / "before" / f"{job.company}-{uuid4()}.md", "w") as md:
        enriched_text = f"# {job.job_title}\n\n## Company\n*{job.company}*\n\n## Job Description\n{markdown_text}"
        enriched_text = enriched_text.replace("Show more", "").replace("Show less", "")
        md.write(enriched_text)


if __name__ == "__main__":
    main()
