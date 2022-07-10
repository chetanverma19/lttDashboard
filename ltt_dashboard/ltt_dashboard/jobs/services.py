import json

from PyPDF2 import PdfReader
import environ
import requests

from ltt_dashboard.jobs.models import JobApplication
from ltt_dashboard.jobs.serializers import JobApplicationESSerializer


env = environ.Env()


def read_pdf(obj):
    # print(obj.resume.get)
    # obj = open(obj)
    # image_data = bytes(obj.read())
    reader = PdfReader(obj)
    number_of_pages = len(reader.pages)
    pdf_text = ""
    for i in range(0,number_of_pages,1):
        page = reader.pages[0]
        text = page.extract_text()
        pdf_text += text

    return pdf_text


def update_application_on_elastic_search(job_id, user_id, resume):
    job_application = JobApplication.objects.filter(job__id=job_id, user__id=user_id).first()
    if not job_application:
        raise ValueError("Invalid Application")
    application_data = JobApplicationESSerializer(job_application).data
    application_data['resume'] = read_pdf(resume)
    elastic_search_url = env.str("ELASTICSEARCH_APPLICATION_URL", default=None)
    if elastic_search_url is None:
        raise ValueError("Invalid Elasticsearch URL")
    elastic_search_index = env.str("ELASTICSEARCH_APPLICATION_INDEX", default=None)
    hit_url = f"{elastic_search_url}/{elastic_search_index}/_doc/{application_data['id']}"
    print(hit_url)
    headers = {"Content-Type": "application/json"}
    response = requests.request("POST", hit_url, headers=headers, data=json.dumps(application_data))
    print(response)

