import json
import os
import requests
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def recommendCandidatesToRecruiter(event, context):
    # Extract input arguments
    search_criteria = event.get('SearchCriteria')
    job_id = event.get('JobId')
    num_candidates = int(event.get('NumCandidates', 5))  # Ensure num_candidates is an integer

    # Define API endpoints
    job_db_dev_api = os.environ['JobDbDevApi']
    candi_db_dev_api = os.environ['CandiDbDevApi']

    # Retrieve job data if JobId is provided
    job_data = None
    if job_id:
        job_data = fetch_job_data(job_db_dev_api, job_id)

    # Retrieve candidate data
    candidate_data = fetch_candidate_data(candi_db_dev_api)

    # Compute recommendations
    recommendations = generate_recommendations(job_data, candidate_data, num_candidates)

    # Prepare the response
    response = {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(recommendations)
    }

    return response

def fetch_job_data(api_url, job_id):
    url = f"https://{api_url}.execute-api.{os.environ['AWS::Region']}.amazonaws.com/Prod/jobDbDev"
    response = requests.get(url, params={'JobId': job_id})
    if response.status_code == 200:
        return response.json()
    return None

def fetch_candidate_data(api_url):
    url = f"https://{api_url}.execute-api.{os.environ['AWS::Region']}.amazonaws.com/Prod/candiDbDev"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return []

def generate_recommendations(job_data, candidate_data, num_candidates):
    if job_data is None or not candidate_data:
        return []

    # Implement TF-IDF features matrix for job and candidate matching and ranking
    documents = [job_data['job']['description']] + [candidate['Candidate']['skills'] for candidate in candidate_data]
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
            "RecommendationId": f"Rec-{index}-{job_data['job']['job_type_id']}",
            "JobId": job_data['job']['job_type_id'],
            "RecommendedCandidateId": candidate_data[index - 1]['Candidate']['id'],
            "Rank": rank + 1,
            "SimilarityScore": score
        })

    return response_body

