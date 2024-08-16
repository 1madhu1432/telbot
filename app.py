
from pathlib import Path
import os 
from langchain_community.vectorstores import FAISS 
from pprint import pprint
import google.generativeai as genai 
from langchain.chains.question_answering import load_qa_chain
from dotenv import load_dotenv



import base64 
import io 
from PIL import Image
import pdf2image # type: ignore


from flask import Flask, request, jsonify
from flask import jsonify
from flask_cors import CORS # type: ignore
import numpy as np




load_dotenv()
genai.configure(api_key="AIzaSyC34WIDJl_0_qHrpItozITRQCphGVEwYBI")


flask_app=Flask(__name__)
CORS(flask_app)

######################################################## PDF CONTENT EXTRACTION ################################################
# Define a function to extract content from a PDF file
def extract_pdf_content():
    try:
        # Open the PDF file in binary read mode
        pdf_path = open("resume.pdf", "rb")
        
        # Check if the PDF file was successfully opened
        if pdf_path is not None :
            # Convert the PDF file to a list of images, one image per page
            images = pdf2image.convert_from_bytes(pdf_path.read())
            
            # Extract the first page of the PDF as an image
            first_page = images[0]

            # Convert the PIL image of the first page to a byte array in JPEG format
            img_byte_arr = io.BytesIO()
            first_page.save(img_byte_arr, format='JPEG')
            img_byte_arr = img_byte_arr.getvalue()

            # Encode the byte array to base64 and prepare it as part of the input for the model
            pdf_parts = [
                {
                    "mime_type": "image/jpeg",
                    "data": base64.b64encode(img_byte_arr).decode('utf-8')
                }
            ]
        else:
            # Return None if the PDF file could not be opened
            return None
        
        # Define a prompt for the model to extract and format data from the PDF
        prompt = "This is a resume. Extract all the data in this pdf in sequential format and then create a json as output which has all the data of the pdf. Extract all the information in the pdf such as skills, contact number, projects, work experience and all the relevant data that companies require in Resume. Make sure to give out in json format. If you are not able to extract the data, just say, 'I am not able to extract the data'"

        # Initialize the model with a specific version
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Generate content based on the image of the first page and the prompt
        response = model.generate_content([pdf_parts[0], prompt])
        
        # Return the text response from the model
        # print(response.text)
        return response.text
    except FileNotFoundError:
        # Return None if the PDF file was not found
        return None

# extract_pdf_content()


#########USE OF JSONLOADER #########


# Define a function to load JSON data from a specified file path
def load_json_data(file_path):
    try:
        # Open the file in read mode
        with open(file_path, 'r') as f:
            # Read the entire content of the file
            data = f.read()
            # Print the data to the console (for debugging or verification purposes)
            print(data)
            # Return the data read from the file
            return data
    except Exception as e:
        # If an exception occurs, print the error message
        print(f"Error loading JSON data: {e}")
        # Return None to indicate failure in loading data
        return None



###########################Taking Job description as ####################################

# Define a function to process a resume and match it against a job description
def process_resume(job_description,resume_text):
    # Extract content from a PDF resume
    # resume_text = extract_pdf_content()
    # print(resume_text)
    # Load resume data from a JSON file
    resume_data = load_json_data('resume.json')
    # Open and read the job description from a text file
    job_description = open("job_description.txt", "r")
    job_description = job_description.read()
    # Define a prompt for the model to format the resume according to the job description
    # prompt="You are provided with a job description and a resume. Process all the information and generate a JSON object containing a newly formatted resume. This new resume should retain all the existing information but be modified to closely match the job description. Additionally, add a couple of relevant skills to enhance the ATS score and improve the chances of selection. Ensure there are no significant changes in the skill set; add only related skills to avoid any suspicion. Modify the summary and project descriptions in the same way. Ensure the output is in JSON format and also share the changes made in this new resume. If you are unable to extract the necessary data, respond with 'I am not able to extract the data.'"

    prompt="Your task is to create a resume that matches the provides job_description. Data of the applicant is provided. Use this data to increase the ATS( Applicant Tracking System) score of the resume. In the skills sections don't make any major changes only add those skills that is highly associated with existing skills. Make changes in the summary sections and Project Description to match the requiremnts of the job decsription. Project description must be in bullet points instead of a paragraph. Avoid any suspicion and maintain the overall integrity of the Resume.Ensure the output is in JSON format and also share the changes made in this new resume. Extract the technical technical words from job_description and include that into the resume to uplift the score.Always include basic technical terms from the job skills that does not signify and particular skillset. Eg: HTML, CSS, Version Control, Rest API if web developer(Extract words like these from the Job Description).  If you are unable to extract the necessary data, respond with 'I am not able to extract the data.'"

    # Initialize the model with a specific version
    np.random.seed(42)
    model = genai.GenerativeModel('gemini-1.5-flash')
    

    # If PDF data extraction failed, use the JSON resume data to generate content
    if resume_text is None :
        response = model.generate_content([job_description, prompt, resume_data],seed=42)
        # print(response._result[""])
        

    # If loading JSON resume data failed, use the PDF data to generate content
    if resume_text is not None:
        response = model.generate_content([job_description,  resume_text,prompt])
        # print(response)
    return response
# Call the process_resume function to execute the processing
# process_resume()



if __name__ == '__main__':
    flask_app.run(debug=True, host='0.0.0.0', port=5123)