import re
def find_key_by_value(data, search_key):
    """
    Recursively searches for a key in a nested dictionary and returns the corresponding value.
    """
    for key, value in data.items():
        if key == search_key:
            return value
        if isinstance(value, dict):  # If the value is a dictionary, recurse
            found_value = find_key_by_value(value, search_key)
            if found_value:
                return found_value
    return None
def clean_text(text):
    text = re.sub(r'\s*,\s*', '', text)  # Remove commas surrounded by whitespace
    text = re.sub(r'[\t\n]', ' ', text)  # Replace tabs and newlines with spaces
    text = re.sub(r'\s+', ' ', text)  # Collapse multiple spaces into one
    return text.strip()
def standardize_format(data):
    # data = clean_text(data)
    """
    Standardizes the input dictionary to a common format.
    """
    standard_format = {
        "name": "",
        "email": "",
        "phone": "",
        "linkedin": "",
        "summary": "",
        "education": [],
        "experience": [],
        "projects": [],
        "skills": [],
        "awards": [],
        "interests": [],
        "languages": [],
        "certificates": [],
        "changes": []
    }

    # Fill the fields that might have different nesting
    for search_key in ["name", "email", "phone", "linkedin"]:
        standard_format[search_key] = find_key_by_value(data, search_key)
    
    # Directly fill the other fields that match the standard keys
    for key in standard_format.keys():
        if key in data:
            standard_format[key] = data[key]
        elif key in data.get("resume", {}):
            standard_format[key] = data["resume"][key]
    
    return standard_format


# Example usage with your provided JSON data
json1 = {
    "resume": {
        "header": {
            "name": "Nithin Sai Charugundla",
            "email": "nithincns2701@gmail.com",
            "phone": "+918185004930",
            "linkedin": "linkedin.com/in/nithin-sai-charugundla",
            "github": "github.com/Nithin2701s"
        },
        "summary": "Highly motivated and enthusiastic MERN stack developer intern...",
        "education": [{"institution": "Indian Institute of Information Technology, Sricity (IIITS)", "degree": "B.Tech. in Computer Science and Technology", "graduationDate": "May. 2025", "gpa": "7.89/10"}],
        "experience": [],
        "projects": [{"title": "VIHARI", "dates": "Sep. 2023 - Dec 2023", "description": ["Developed a full-stack MERN stack web application using React.js..."]}],
        "skills": ["JavaScript", "React.js", "Node.js", "Express.js", "MongoDB", "HTML", "CSS", "Bootstrap"],
        "changes": ["Updated the summary section to highlight skills and experience relevant to the job description."]
    }
}

json2 = {
    "name": "Bhavana Dupaguntla",
    "email": "bhavanadupaguntla5566@gmail.com",
    "phone": "6281156227",
    "linkedin": "Bhavana Dupaguntla",
    "summary": "MERN Stack Developer with a strong foundation in JavaScript...",
    "education": [
        {"degree": "BTech in Computer Science", "institution": "Sree Vahini Institute of Science and Technology", "years": "2019-2023", "gpa": "6.74"},
        {"degree": "Intermediate in Computer Science", "institution": "Sri Sri Junior College", "years": "2017-2019", "gpa": "6.84"}
    ],
    "skills": ["JavaScript", "MERN Stack", "MongoDB", "Express.js", "React.js", "Node.js", "HTML5", "CSS3"],
    "experience": [{"title": "Sweets Shop Website", "company": "Personal Project", "years": "2022", "description": ["Developed a website using Python Django..."]}],
    "awards": ["First prize in quiz competition in college fest"],
    "interests": ["Emerging Technologies", "Music"],
    "languages": ["Telugu", "English"],
    "certificates": ["Python Full Stack Course"]
}

# Convert both JSON objects to the standard format
# standard_json1 = standardize_format(json1['resume'])
# standard_json2 = standardize_format(json2)

# print(standard_json1)
# print("\n\n")
# print(standard_json2)
