import json

# Sample job data (you can fetch this data from a database or another source)
jobs = [
    {
        "job_type_id": "45",
        "company_id": "p6g3sDq4Rl",
        "title": "Job 45",
        "description": "Description for Job 45",
        "requirements": "Requirements for Job 45",
        "expired_date": "2023-12-14",
        "status": 0,
        "location": "Location RZjsF",
        "no_of_vacancies": "10"
    },
    {
        "job_type_id": "77",
        "company_id": "cB5jfA9oLt",
        "title": "Job 77",
        "description": "Description for Job 77",
        "requirements": "Requirements for Job 77",
        "expired_date": "2023-12-24",
        "status": 0,
        "location": "Location QxCu2",
        "no_of_vacancies": "2"
    },
    {
        "job_type_id": "64",
        "company_id": "YJzhW1B4rV",
        "title": "Job 64",
        "description": "Description for Job 64",
        "requirements": "Requirements for Job 64",
        "expired_date": "2023-12-10",
        "status": 1,
        "location": "Location FUBrt",
        "no_of_vacancies": "1"
    },
    {
        "job_type_id": "68",
        "company_id": "kx9p2LsoEa",
        "title": "Job 68",
        "description": "Description for Job 68",
        "requirements": "Requirements for Job 68",
        "expired_date": "2023-12-16",
        "status": 0,
        "location": "Location jn5D7",
        "no_of_vacancies": "9"
    },
    {
        "job_type_id": "32",
        "company_id": "3KXutlRdbG",
        "title": "Job 32",
        "description": "Description for Job 32",
        "requirements": "Requirements for Job 32",
        "expired_date": "2023-12-11",
        "status": 0,
        "location": "Location CRbQe",
        "no_of_vacancies": "5"
    },
    {
        "job_type_id": "61",
        "company_id": "YdCvoIjVnL",
        "title": "Job 61",
        "description": "Description for Job 61",
        "requirements": "Requirements for Job 61",
        "expired_date": "2023-12-26",
        "status": 1,
        "location": "Location Z7M1s",
        "no_of_vacancies": "8"
    },
    {
        "job_type_id": "89",
        "company_id": "bgJsW5nCZd",
        "title": "Job 89",
        "description": "Description for Job 89",
        "requirements": "Requirements for Job 89",
        "expired_date": "2023-12-3",
        "status": 0,
        "location": "Location fA6Hv",
        "no_of_vacancies": "10"
    },
    {
        "job_type_id": "1",
        "company_id": "Tio6VmUjbX",
        "title": "Job 1",
        "description": "Description for Job 1",
        "requirements": "Requirements for Job 1",
        "expired_date": "2023-12-25",
        "status": 1,
        "location": "Location XYz2K",
        "no_of_vacancies": "4"
    },
    {
        "job_type_id": "16",
        "company_id": "HZmaY6x8dp",
        "title": "Job 16",
        "description": "Description for Job 16",
        "requirements": "Requirements for Job 16",
        "expired_date": "2023-12-27",
        "status": 0,
        "location": "Location uApk4",
        "no_of_vacancies": "3"
    },
    {
        "job_type_id": "14",
        "company_id": "R0jgCMvPxo",
        "title": "Job 14",
        "description": "Description for Job 14",
        "requirements": "Requirements for Job 14",
        "expired_date": "2023-12-13",
        "status": 1,
        "location": "Location FdeV9",
        "no_of_vacancies": "7"
    }
    # Add more job entries as needed
]

def lambda_handler(event, context):
    http_method = event["httpMethod"]
    path_parameters = event.get("pathParameters")

    if http_method == "GET":
        if path_parameters and "jobid" in path_parameters:
            # Retrieve a job by job_type_id
            job_id = path_parameters["jobid"]
            job = next((j for j in jobs if j["job_type_id"] == job_id), None)
            if job:
                response = {"job": job}
            else:
                response = {"message": "Job not found"}
        else:
            # Retrieve the list of all jobs
            response = {"job": jobs}
    else:
        response = {"message": "Unsupported HTTP method"}

    return {
        "statusCode": 200,
        "body": json.dumps(response),
        "headers": {
            "Content-Type": "application/json"
        }
    }

