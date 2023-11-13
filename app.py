# Import necessary libraries
import os
import pandas as pd
import streamlit as st
import pyresparser
import nltk
import spacy

# Download NLTK resources
nltk.download('words')
nltk.download('stopwords')

# Download SpaCy English model
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("Downloading language model for the spaCy POS tagger")
    from spacy.cli import download
    download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")


# Function to parse resumes
def parse_resumes(resume_directory):
    resume_data_list = []
    for root, dirs, files in os.walk(resume_directory):
        for file in files:
            if file.endswith('.pdf') or file.endswith('.docx'):
                resume_file_path = os.path.join(root, file)
                data = pyresparser.ResumeParser(resume_file_path).get_extracted_data()
                resume_data_list.append(data)
    return resume_data_list

# Function to filter candidates based on skills
def search_candidates(skills, resume_data_list):
    df = pd.DataFrame(resume_data_list)
    columns_to_drop = ['college_name', 'experience', 'no_of_pages', 'total_experience']
    df = df.drop(columns=columns_to_drop)

    skills_list = [skill.strip().lower() for skill in skills.split(',')]
    df['skills'] = df['skills'].apply(lambda x: ', '.join(x) if isinstance(x, list) else x)
    df['skills'] = df['skills'].astype(str)

    filtered_df = pd.DataFrame()
    for skill in skills_list:
        filtered_df = pd.concat([filtered_df, df[df['skills'].str.lower().str.contains(skill, case=False, na=False)]])

    return filtered_df[['name', 'email', 'mobile_number', 'skills']].drop_duplicates()

# Streamlit App for Recruiter
def main():
    st.title("Recruiter Candidate Search")

    # User input for directory path
    resume_directory = st.text_input("Enter the path to the resume directory:")

    skill_input = st.text_input("Enter skills (comma-separated):")

    if st.button("Search"):
        if resume_directory and skill_input:
            resume_data_list = parse_resumes(resume_directory)
            filtered_candidates = search_candidates(skill_input, resume_data_list)
            if not filtered_candidates.empty:
                st.write(filtered_candidates)
            else:
                st.write("No candidates found with the specified skills.")

if __name__ == '__main__':
    main()
