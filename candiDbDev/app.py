import json

# Sample candidate data
candidates = [
    {
        "id": "1",
        "userid": "user1",
        "fullName": "John Doe",
        "dateOfBirth": "1990-01-15",
        "address": "123 Main St, City",
        "contactNumber": "555-123-4567",
        "skills": ["Python", "JavaScript", "SQL"],
        "education": "Bachelor's in Computer Science",
        "yearOfExperience": "5",
        "resumeUrl": "https://example.com/resume/user1"
    },
    {
        "id": "2",
        "userid": "user2",
        "fullName": "Alice Smith",
        "dateOfBirth": "1988-04-20",
        "address": "456 Elm St, Town",
        "contactNumber": "555-987-6543",
        "skills": ["Java", "C++", "Angular"],
        "education": "Master's in Information Technology",
        "yearOfExperience": "8",
        "resumeUrl": "https://example.com/resume/user2"
    },
    {
        "id": "3",
        "userid": "user3",
        "fullName": "Emily Johnson",
        "dateOfBirth": "1995-09-10",
        "address": "789 Oak St, Village",
        "contactNumber": "555-456-7890",
        "skills": ["Ruby", "React", "MongoDB"],
        "education": "Bachelor's in Computer Engineering",
        "yearOfExperience": "4",
        "resumeUrl": "https://example.com/resume/user3"
    },
    {
        "id": "4",
        "userid": "user4",
        "fullName": "Michael Brown",
        "dateOfBirth": "1987-02-05",
        "address": "101 Pine St, Suburb",
        "contactNumber": "555-234-5678",
        "skills": ["Node.js", "AWS", "MySQL"],
        "education": "Ph.D. in Computer Science",
        "yearOfExperience": "12",
        "resumeUrl": "https://example.com/resume/user4"
    },
    {
        "id": "5",
        "userid": "user5",
        "fullName": "Sarah Wilson",
        "dateOfBirth": "1992-11-25",
        "address": "222 Cedar St, County",
        "contactNumber": "555-345-6789",
        "skills": ["Python", "Django", "PostgreSQL"],
        "education": "Bachelor's in Information Systems",
        "yearOfExperience": "7",
        "resumeUrl": "https://example.com/resume/user5"
    },
    {
        "id": "6",
        "userid": "user6",
        "fullName": "David Lee",
        "dateOfBirth": "1991-08-12",
        "address": "333 Birch St, State",
        "contactNumber": "555-876-5432",
        "skills": ["Java", "Spring Boot", "Oracle"],
        "education": "Master's in Software Engineering",
        "yearOfExperience": "9",
        "resumeUrl": "https://example.com/resume/user6"
    },
    {
        "id": "7",
        "userid": "user7",
        "fullName": "Linda Hall",
        "dateOfBirth": "1989-03-30",
        "address": "444 Maple St, Capital",
        "contactNumber": "555-765-4321",
        "skills": ["JavaScript", "React", "MySQL"],
        "education": "Bachelor's in Computer Science",
        "yearOfExperience": "6",
        "resumeUrl": "https://example.com/resume/user7"
    },
    {
        "id": "8",
        "userid": "user8",
        "fullName": "Robert Taylor",
        "dateOfBirth": "1993-06-18",
        "address": "555 Pine St, Metro",
        "contactNumber": "555-987-6543",
        "skills": ["Python", "Flask", "MongoDB"],
        "education": "Master's in Computer Engineering",
        "yearOfExperience": "5",
        "resumeUrl": "https://example.com/resume/user8"
    },
    {
        "id": "9",
        "userid": "user9",
        "fullName": "Karen White",
        "dateOfBirth": "1986-12-07",
        "address": "666 Elm St, Town",
        "contactNumber": "555-234-5678",
        "skills": ["Node.js", "Express.js", "PostgreSQL"],
        "education": "Bachelor's in Information Systems",
        "yearOfExperience": "8",
        "resumeUrl": "https://example.com/resume/user9"
    },
    {
        "id": "10",
        "userid": "user10",
        "fullName": "James Brown",
        "dateOfBirth": "1994-04-03",
        "address": "777 Oak St, City",
        "contactNumber": "555-765-4321",
        "skills": ["Java", "Spring Boot", "Oracle"],
        "education": "Ph.D. in Computer Science",
        "yearOfExperience": "10",
        "resumeUrl": "https://example.com/resume/user10"
    }
]

def lambda_handler(event, context):
    http_method = event["httpMethod"]
    path_parameters = event.get("pathParameters")

    if http_method == "GET":
        if path_parameters and "id" in path_parameters:
            # Retrieve a candidate by id
            candidate_id = path_parameters["id"]
            candidate = next((c for c in candidates if c["id"] == candidate_id), None)
            if candidate:
                response = {"Candidate": candidate}
            else:
                response = {"message": "Candidate not found"}
        else:
            # Retrieve the list of all candidates
            response = {"Candidate": candidates}
    else:
        response = {"message": "Unsupported HTTP method"}

    return {
        "statusCode": 200,
        "body": json.dumps(response),
        "headers": {
            "Content-Type": "application/json"
        }
    }









