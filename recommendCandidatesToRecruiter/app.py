import requests
from requests.auth import HTTPBasicAuth
import random
import json

def recommend_candidates_to_recruiter(event, context):
    httppostbody = json.loads(event.get("body", "{}"))
    search_criteria = httppostbody.get("SearchCriteria", None)
    job_id = httppostbody.get("JobId", None)
    num_recommended = httppostbody.get("NumOfCandidates", 5)
    
    if search_criteria:
        job_description = search_criteria
        job_requirements = None
        job_id = "candidateSrchId-" + str(random.randint(10**11, 10**12 - 1))

    elif job_id:
        job_service_url = get_job_service_url(job_id)
        job_description = get_job_description(job_service_url)
        if job_description is None:
            return {
                "statusCode": 500,
                "body": json.dumps({
                    "message": "JobId not found. Please provide a valid JobId as a input argument",
                    "jost description": job_description,
                }),
            }        

    else:
        return {
            "statusCode": 500,
            "body": json.dumps({
                "message": "Please provide either Search Criteria or Jobid as input arguments",
            }),
        }

    candidate_service_url = get_candidate_service_url()
    candidate_list = get_candidate_list(candidate_service_url)
    if candidate_list is None:
        return {
            "statusCode": 500,
            "body": json.dumps({
                "message": "Candidate List is empty. Please check Candidate Service API and API Output",
            }),
        }
    candidate_ids, candidate_name, candidate_email, candidate_mobileNo, candidate_data = get_candidate_ids_and_skills(candidate_list)
    sorted_indices, sorted_candidate_ids, sorted_similarity_scores = get_sorted_indices_scores(candidate_ids, candidate_data, job_description.replace(',', ' ').replace('"', ' ').replace('.', ' ').replace('{', ' ').replace('}', ' ').replace('[', ' ').replace(']', ' ').replace('(', ' ').replace(')', ' ').lower())
    sorted_candidate_name = [candidate_name[i] for i in sorted_indices]
    sorted_candidate_email = [candidate_email[i] for i in sorted_indices]
    sorted_candidate_mobileNo = [candidate_mobileNo[i] for i in sorted_indices]
    recommendation_id = "".join(random.choices("0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ", k=10)) 
    if num_recommended > len(sorted_indices):
        num_recommended = len(sorted_indices)
    output_list = []
    for i in range(num_recommended):
        output_dict = {
            "Recommendation-Id": recommendation_id,
            "JobId/SearchId": job_id,
            "Recommended Candidate-Id": sorted_candidate_ids[i],
            "Candidate-Name": sorted_candidate_name[i],
            "Candidate-email": sorted_candidate_email[i],
            "Candidate_mobileNo": sorted_candidate_mobileNo[i],
            "Rank": i + 1,
            "Similarity Score": "{:.2f}%".format(min(sorted_similarity_scores[i] * 100, 100))
        }
        output_list.append(output_dict)

    return {
        "statusCode": 200,
        "body": json.dumps({
                "message": "List of Recommended Candidates",
                "body": output_list,
        }),
    }

def get_job_service_url(job_id):
    #return 'http://job-service-32b5298bca7abe46.elb.ap-southeast-1.amazonaws.com/api/v1/jobs/' + job_id
    return 'http://job-service-elb-de53cd8b61f351ee.elb.ap-southeast-1.amazonaws.com/api/v1/jobs/' + job_id

def get_job_description(job_service_url):
    api_response = requests.get(job_service_url)
    if api_response.status_code == 200:
        api_output = api_response.json()
        job_data = api_output['data']
        return job_data['description'] + ' ' + job_data['requirements']
    else:
        return None

def get_candidate_service_url():
    return 'https://36528a98aae344c6a26756a47b7a8ee5.us-central1.gcp.cloud.es.io:9243/candidate/_search'

def get_candidate_list(candidate_service_url):
    username = 'elastic'
    password = 'dcAjK4RminkR6JSP3qPSLzHw'
    headers = {"Content-Type": "application/json"}
    body = {"query": { "match_all" : {} }, "_source" : [ "_id","name","email","mobileNo","workExperiences", "educationDetails","jobPreferences" ] }
    api_response = requests.post(candidate_service_url, auth=HTTPBasicAuth(username, password), headers=headers, json=body)
    if api_response.status_code == 200:
        api_output = api_response.json()['hits']['hits']
        api_data = []
        api_data = [{"_id": candidate['_id'], "_name": candidate['_source']['name'], "_email": candidate['_source']['email'], "_mobileNo": candidate['_source']['mobileNo'], "_data": json.dumps(candidate['_source']).replace(',', ' ').replace('"', ' ').replace('.', ' ').replace('{', ' ').replace('}', ' ').replace('[', ' ').replace(']', ' ').replace('(', ' ').replace(')', ' ').lower()} for candidate in api_output] 
        return api_data
    else:
        return None

def get_candidate_ids_and_skills(candidate_list):
    candidate_ids = [candidate['_id'] for candidate in candidate_list]
    candidate_name = [candidate['_name'] for candidate in candidate_list]
    candidate_email = [candidate['_email'] for candidate in candidate_list]
    candidate_mobileNo = [candidate['_mobileNo'] for candidate in candidate_list]
    candidate_data = [candidate['_data'] for candidate in candidate_list]
    return candidate_ids, candidate_name, candidate_email, candidate_mobileNo, candidate_data

def get_sorted_indices_scores(candidate_ids, candidate_data, job_description):
    if job_description:
        similarity_scores = []
        for candidate_skill in candidate_data:
            if candidate_skill:
                score = len(set(job_description.split()) & set(candidate_skill.split())) / len(set(job_description.split()))
                similarity_scores.append(score)
            else:
                # Handle the case when 'candidate_data' is None
                similarity_scores.append(0)  # or any default value
    else:
        # Handle the case when 'job_description' is None
        similarity_scores = [0 for _ in candidate_data]  # or any default value

    sorted_indices = sorted(range(len(similarity_scores)), key=lambda k: similarity_scores[k], reverse=True)
    sorted_candidate_ids = [candidate_ids[i] for i in sorted_indices]
    sorted_similarity_scores = [similarity_scores[i] for i in sorted_indices]
    return sorted_indices, sorted_candidate_ids, sorted_similarity_scores

