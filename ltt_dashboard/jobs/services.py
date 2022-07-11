import json

from PyPDF2 import PdfReader
import environ
import requests

from ltt_dashboard.jobs.models import JobApplication
from ltt_dashboard.jobs.serializers import JobApplicationESSerializer

env = environ.Env()


def read_pdf(obj):
    reader = PdfReader(obj)
    number_of_pages = len(reader.pages)
    pdf_text = ""
    for i in range(0, number_of_pages, 1):
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
    elastic_search_index = env.str("ELASTICSEARCH_APPLICATION_INDEX", default=None)
    if elastic_search_url is None or elastic_search_index is None:
        raise ValueError("Invalid Elasticsearch Configuration")
    hit_url = f"{elastic_search_url}/{elastic_search_index}/_doc/{application_data['id']}"
    headers = {"Content-Type": "application/json"}
    response = requests.request("POST", hit_url, headers=headers, data=json.dumps(application_data))


def get_payload_for_application_es_search(data):
    bool_query = {}
    if data.get('query_text'):
        should_query = [
            {
                "multi_match": {
                    "query": data.get('query_text'),
                    "fields": ["user.email", "user.full_name", "user.user_name", "email", "applicant_message",
                               "last_staff_note", "resume"]
                }
            }
        ]
        bool_query.update({"should": should_query})
    must_filters = []
    filter_key_list = ['job', 'country', 'application_status']
    for filter_key in filter_key_list:
        if data.get(filter_key):
            if filter_key == 'job':
                match_query_tmp = {"terms": {"job.id": data.get(filter_key)}}
            else:
                match_query_tmp = {"terms": {filter_key: data.get(filter_key)}}
            must_filters.append(match_query_tmp)
    if len(must_filters) > 0:
        bool_query.update({"filter": must_filters})
    payload = {
        "_source": ["id"],
        "query": {
            "bool": bool_query
        }
    }
    return payload


def get_filtered_application_id_list_from_es(data):
    payload = get_payload_for_application_es_search(data)
    elastic_search_url = env.str("ELASTICSEARCH_APPLICATION_URL", default=None)
    elastic_search_index = env.str("ELASTICSEARCH_APPLICATION_INDEX", default=None)
    if elastic_search_url is None or elastic_search_index is None:
        raise ValueError("Invalid Elasticsearch Configuration")
    hit_url = f"{elastic_search_url}/{elastic_search_index}/_search"
    headers = {"Content-Type": "application/json"}
    response = requests.request("POST", hit_url, headers=headers, data=json.dumps(payload))
    data = json.loads(response.text)
    application_id_list = []
    for source_id in data['hits']['hits']:
        application_id_list.append(source_id["_source"]["id"])
    return application_id_list
