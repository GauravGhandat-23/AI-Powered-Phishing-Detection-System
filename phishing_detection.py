import pandas as pd
import numpy as np
import re
import streamlit as st
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import make_pipeline
import joblib
from nltk.corpus import stopwords
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup

# Download NLTK data
import nltk
nltk.download('stopwords')

# Load stopwords
STOPWORDS = set(stopwords.words("english"))

# Function to clean and process the email body
def clean_email_body(email_body):
    # Removing non-alphabetic characters
    email_body = re.sub(r'[^a-zA-Z\s]', '', email_body)
    # Lowercasing and removing stopwords
    email_body = ' '.join([word.lower() for word in email_body.split() if word.lower() not in STOPWORDS])
    return email_body

def extract_url_features(email_body):
    urls = re.findall(r'(https?://[^\s]+)', email_body)
    features = []
    
    for url in urls:
        parsed_url = urlparse(url)
        
        # Ensure numeric values are appended to the features list
        domain_length = len(parsed_url.netloc)  # Length of the domain
        path_length = len(parsed_url.path)  # Length of the path
        protocol = parsed_url.scheme  # Protocol (http/https)
        
        features.append(domain_length)
        features.append(path_length)
        
        # Check if the protocol is valid and append to features
        if protocol in ['http', 'https']:
            features.append(1)
        else:
            features.append(0)
        
        # Try to fetch the URL to check its status code
        try:
            response = requests.get(url, timeout=3)
            status_code = response.status_code
            features.append(status_code)
        except:
            features.append(0)  # If URL is not reachable, append 0
    
    # Return the mean of numeric values in the features list or 0 if empty
    return np.mean([f for f in features if isinstance(f, (int, float))]) if features else 0

# Function to load and train the model
def train_model(data):
    # Clean and process email bodies
    data['cleaned_body'] = data['email_body'].apply(clean_email_body)
    data['url_features'] = data['email_body'].apply(extract_url_features)

    X = pd.concat([data['cleaned_body'], data['url_features']], axis=1)
    X.columns = ['email_body', 'url_features']
    y = data['label']

    # Use CountVectorizer for email body and concatenate URL features
    body_vectorizer = CountVectorizer()
    model = make_pipeline(body_vectorizer, MultinomialNB())

    # Train the model
    model.fit(X['email_body'], y)
    
    # Save the trained model
    joblib.dump(model, 'phishing_model.pkl')

# Function to predict phishing
def predict_phishing(model, email_body):
    # Clean and process the email body and extract URL features
    cleaned_body = clean_email_body(email_body)
    url_features = extract_url_features(email_body)
    X = pd.DataFrame([[cleaned_body, url_features]], columns=['email_body', 'url_features'])
    
    # Predict using the trained model
    prediction = model.predict(X['email_body'])
    return 'Phishing' if prediction[0] == 1 else 'Safe'

# Streamlit interface
def main():
    # Display the logo
    st.image("logo.JPEG", width=700)  # Adjust the width as needed
    st.title("AI-Powered Phishing Detection System")
    
    # Load trained model if available
    try:
        model = joblib.load('phishing_model.pkl')
        st.write("Model loaded successfully!")
    except:
        st.write("No trained model found. Please train the model first.")
    
    # Email Input
    email_input = st.text_area("Enter the Email Body to Check:", height=200)
    
    if st.button("Check Phishing"):
        if email_input:
            result = predict_phishing(model, email_input)
            st.write(f"Prediction: {result}")
        else:
            st.write("Please enter an email body for analysis.")
            
    # Upload email dataset for training the model
    st.subheader("Train the Model (Optional)")
    uploaded_file = st.file_uploader("Choose a CSV file with email data", type="csv")
    
    if uploaded_file is not None:
        data = pd.read_csv(uploaded_file)
        if 'email_body' in data.columns and 'label' in data.columns:
            st.write("Training the model with the uploaded data...")
            train_model(data)
            st.write("Model trained and saved successfully!")

if __name__ == '__main__':
    main()
