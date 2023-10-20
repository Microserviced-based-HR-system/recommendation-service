import json
import os
import requests
import boto3
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def recommend_candidates_to_recruiter(event, context):
    # Extract input arguments
    try:
        search_criteria = event["queryStringParameters"].get("SearchCriteria")
    except (AttributeError, KeyError):
        pass
    try:
        job_id = event["queryStringParameters"].get("jobid")
    except (AttributeError, KeyError):
        pass
    try:
        num_candidates = event["queryStringParameters"].get('NumCandidates')
        if num_candidates is not None:
            num_candidates = int(num_candidates)
    except (AttributeError, ValueError):
        pass

    if search_criteria is None and job_id is None:
        return {
            "statusCode": 404,
            "body": json.dumps("Missing or invalid 'SearchCriteria/JobId' parameter in the request")
        }

# If you reached this point, all required parameters are successfully retrieved and validated.

    # Define JobService API endpoints
    #job_db_dev_api = os.environ['JobDbDevApi']
    #job_db_dev_api = "https://1a2b23ed8007415aa10a43bb67d84e50.vfs.cloud9.ap-southeast-1.amazonaws.com/jobDbDev"

    # Call the function with desired stack_name and api resource name to get api url of job and candidate services
    stack_name = 'dev-app'
    api_res_name = 'JobDbDevApi'
    job_db_dev_api = get_apiurl_frmcfn(stack_name, api_res_name)

    # Define CandidateService API endpoints
    #candi_db_dev_api = os.environ['CandiDbDevApi']
    #candi_db_dev_api = "https://1a2b23ed8007415aa10a43bb67d84e50.vfs.cloud9.ap-southeast-1.amazonaws.com/candiDbDev"

    # Call the function with desired stack_name and api resource name to get api url of job and candidate services
    stack_name = 'dev-app'
    api_res_name = 'CandiDbDevApi'
    candi_db_dev_api = get_apiurl_frmcfn(stack_name, api_res_name)

    # Retrieve job data if JobId is provided
    if job_id:
        job_data = fetch_job_data(job_db_dev_api, job_id)
    else:
        job_data = {'job': {'description': search_criteria}}

    # Retrieve candidate data
    candidate_data = fetch_candidate_data(candi_db_dev_api)

    # Compute recommendations
    recommendations = generate_recommendations(job_data, candidate_data, num_candidates)

    # Prepare the response
    response = {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        #"body": json.dumps(recommendations)
        "body": json.dumps({
            "recommendations": recommendations,
            "job_data": job_data,
            "candidate_data": candidate_data
        })

    }

    return response

'''
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
^^^ THIS IS END OF THE MAIN LAMBDA FUNCTION ^^^
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
###############################################
## Other Function Declaration Section Start ###
###############################################
'''

def fetch_job_data(api_url, job_id):
    try:
        response = requests.get(api_url, params={'id': job_id})
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"An error occured during the request: {e}")
        return None

def fetch_candidate_data(api_url):
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"An error occured during the request: {e}")
        return None

def generate_recommendations(job_data, candidate_data, num_candidates):
    if job_data is None or not candidate_data:
        return []

    # Implement TF-IDF features matrix for job and candidate matching and ranking
    #documents = [job_data['job']['description']] + [candidate['Candidate']['skills'] for candidate in candidate_data]
    documents = [job_data.get('job', {}).get('description')] + [candidate.get('Candidate', {}).get('skills', '') for candidate in candidate_data]
    tfidf_vectorizer = TfidfVectorizer()
    tfidf_matrix = tfidf_vectorizer.fit_transform(documents)

    # Compute similarity scores
    similarity_scores = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix)

    # Sort candidates by similarity score and select the top candidates
    sorted_candidates = sorted(list(enumerate(similarity_scores[0])), key=lambda x: x[1], reverse=True)
    top_candidates = sorted_candidates[1:num_candidates + 1]

    # Prepare the response
    response_body = []
    for rank, (index, score) in enumerate(top_candidates):
        response_body.append({
            #"RecommendationId": f"Rec-{index}-{job_data['job']['job_type_id']}",
            "RecommendationId": f"Rec-{index}-{job_data['job']}",
            #"JobId": job_data['job']['job_type_id'],
            "JobId": job_data['job'],
            "RecommendedCandidateId": candidate_data[index - 1]['Candidate']['id'],
            "Rank": rank + 1,
            "SimilarityScore": score
        })

    return response_body

def get_apiurl_frmcfn(stack_name, output_key):
    # Create a CloudFormation client
    cfn_client = boto3.client('cloudformation')

    try:
        # Describe the stack to retrieve its outputs
        response = cfn_client.describe_stacks(StackName=stack_name)
        stack = response['Stacks'][0]

        # Extract the outputs as a dictionary
        outputs = {output['OutputKey']: output['OutputValue'] for output in stack['Outputs']}

        # Check if the specified output key exists
        if output_key in outputs:
            return outputs[output_key]
        else:
            return f"Output key '{output_key}' not found in the stack outputs."

    except Exception as e:
        return str(e)


