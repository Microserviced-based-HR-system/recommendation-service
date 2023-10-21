import requests
import random
import boto3
import json
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

# Define the function name and parameters
def recommend_jobs_to_candidate(event, context):
  # Validate input API arguments
  search_criteria = event.get("SearchCriteria", None) # Search Criteria as string
  candidate_id = event.get("CandidateId", None) # candidate id as string
  num_recommended = event.get("NumOfJobs", 5) # Number of recommended jobs as integer, default to 5
  
  # If Search Criteria argument is provided, use it as candidate info and generate random search serial number
  if search_criteria:
    candidate_info = search_criteria
    candidate_id = "jobSrchId-" + str(random.randint(10**11, 10**12 - 1)) # Generate random 12-digit number and prefix with srchId-
  
  # If Candidateid argument is provided, retrieve the candidate data from Candidate Service API and use the skills and education fields
  elif candidate_id:
    # Define Stack Name of Candidate Service API Resource
    stack_name = 'dev-app'
    api_res_name = 'CandiDbDevApi'
    api_url = get_apiurl_frmcfn(stack_name, api_res_name)
    # Retrieve the Candidate data from Job Service API
    candidate_service_url = api_url + '/' + candidate_id # Construct the API URL with the candidate_id
    api_response = requests.get(candidate_service_url) # Get the JSON response and access the data field
    if api_response.status_code == 200:
      api_output = api_response.json()
      candidate_data = {}
      candidate_data['data'] = json.loads(api_output['data'])
      # error due to list data type in skills 
      # candidate_info = candidate_data['data']['skills'] + ' ' + job_data['data']['education']# Get the description field
      candidate_info = ' '.join(candidate_data['data']['skills']) + ' ' + candidate_data['data']['education']
      #job_requirements = job_data['data']['requirements'] # Get the candidate_id field
    else:
      return { "message": f"CandidateServiceApi Request failed with status code {api_response.status_code}.", "api_response": api_response.json() }
    #return job_data, job_description, job_requirements #For Debugging
    #return { "api_output": api_output, "job_service_url": job_service_url } #For Debugging
  
  # If neither argument is provided, return an error message
  else:
    return {"error": "Please provide either Search Criteria or CandidateId as input arguments"}
    #return {"error": "Please provide either Search Criteria or bid as input arguments", **event, "search_criteria": search_criteria, "job_id": job_id} #For Debugging
  
  # Define Stack Name of Job Service API Resource
  stack_name = 'dev-app'
  api_res_name = 'JobDbDevApi'
  api_url = get_apiurl_frmcfn(stack_name, api_res_name)
  #return api_url #For Debugging
  
  # Retrieve the list of candidate data from Candidate Service API
  job_service_url = api_url # The API URL for candidate service. Optional to Construct with API parameters
  #return candidate_service_url #For Debugging

  api_response = requests.get(job_service_url) # Get the JSON response as a list of candidates
  if api_response.status_code == 200:
    api_output = api_response.json()
    job_list = {}
    job_list['data'] = json.loads(api_output['data']) # Get the JSON response as a list of candidates
  else:
    return { "message": f"JobServiceApi Request failed with status code {api_response.status_code}.", "api_response": api_response.json() }
  #return candidate_list #For Debugging

  # Extract the candidate ids, skills and resumes from the candidate list
  # Ref-code1: candidate_ids = [candidate["data"]["id"] for candidate in candidate_list] # A list of candidate ids | id is in type 'integer'
  # Ref-code2: candidate_ids = [json.loads(candidate)["data"]["id"] for candidate in candidate_list] # A list of candidate ids | converted candidate in to dic
  job_ids = [job['id'] for job in job_list['data']]
  #return #For Debugging

  # Ref-code1: candidate_skills = [", ".join(candidate["data"]["skills"]) for candidate in candidate_list] # A list of candidate skills as comma-separated strings 
  # Ref-code2: candidate_skills = [", ".join(candidate['skills']) for candidate in candidate_list['data']]
  # Ref-code3: candidate_skills = [", ".join(candidate['skills']).replace(',', ' ') for candidate in candidate_list['data']]
  job_info = [" ".join([job['title'], ' ', job['description'], ' ', job['requirements']]).replace(',', ' ') for job in job_list['data']]

  #return candidate_skills #For Debugging

  #candidate_resumes = [candidate["data"]["resumeUrl"] for candidate in candidate_list] # A list of candidate resume URLs
  #return { "candidate_ids": candidate_ids, "candidate_skills": candidate_skills } #For Debugging
  
  # Create a TF-IDF vectorizer to transform the text data into numerical features
  vectorizer = TfidfVectorizer()
  
  # Fit the vectorizer on the job description and the candidate skills
  vectorizer.fit([candidate_info] + job_info)
  
  # Transform the job description and the candidate skills into TF-IDF vectors
  candidate_vector = vectorizer.transform([candidate_info]) # A sparse matrix with one row and n_features columns
  job_vectors = vectorizer.transform(job_info) # A sparse matrix with n_candidates rows and n_features columns
  
  # Compute the cosine similarity between the job vector and each candidate vector
  similarity_scores = np.dot(job_vectors, candidate_vector.T).toarray().flatten() # A numpy array with n_candidates elements

  # Sort the candidate ids and similarity scores by descending order of similarity scores
  sorted_indices = np.argsort(similarity_scores)[::-1] # A numpy array with n_candidates elements indicating the sorted positions
  sorted_job_ids = [job_ids[i] for i in sorted_indices] # A list of candidate ids sorted by similarity scores
  sorted_similarity_scores = [similarity_scores[i] for i in sorted_indices] # A list of similarity scores sorted by similarity scores
  #return sorted_similarity_scores #For Debugging
  
  # Generate a recommendation id as an alphanumeric serial number
  recommendation_id = "".join(random.choices("0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ", k=10)) # A random string of length 10
  
  # Create a list of dictionaries to store the output information for each recommended candidate
  output_list = []
  
  # Loop through the number of recommended candidates and append the output information to the output list
  for i in range(num_recommended):
    output_dict = {
      "Recommendation-Id": recommendation_id,
      "CandidateId/SearchId": candidate_id,
      "Recommended Job-Id": sorted_job_ids[i],
      "Rank": i + 1,
      "Similarity Score": "{:.2f}%".format(sorted_similarity_scores[i] * 100) # Format the similarity score as a percentage with two decimal places
    }
    output_list.append(output_dict)
  
  # Return the output list as the API response
  return {
    "statusCode": 200,
    "message": "List of Recommended Jobs",
    "body": output_list
  }

'''
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
^^^ THIS IS END OF THE MAIN LAMBDA FUNCTION ^^^
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
###############################################
## Other Function Declaration Section Start ###
###############################################
'''

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
