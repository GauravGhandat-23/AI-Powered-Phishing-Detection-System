<h1 align="center"> 🚨 AI-Powered Phishing & Fraud Detection System 🚨 </h1>

## ⚙️ About the Project

An AI-powered threat detection console that classifies emails as **phishing** or **safe**, and layers on a rule-based **fraud risk score** for social-engineering patterns. Built using **Python**, **Streamlit**, and **scikit-learn**, the system analyzes email bodies, embedded URLs, and known fraud/scam language to flag malicious content — all wrapped in a dark, SOC-console-style interface.

[![Phishing Detection](https://img.shields.io/badge/Phishing%20Detection-Active-brightgreen)](https://ai-powered-phishing-detection-system-ples7i6bq2tzkaguiykzzt.streamlit.app/)
[![Fraud Risk Engine](https://img.shields.io/badge/Fraud%20Risk%20Engine-Active-orange)](https://ai-powered-phishing-detection-system-ples7i6bq2tzkaguiykzzt.streamlit.app/)

## 🚀 Features

- **Email Body Analysis**: Uses NLP text processing (stopword removal, cleaning) to identify phishing patterns.
- **URL Scanning**: Extracts and evaluates URLs within the email — domain length, path length, protocol, and live status code — to detect malicious links.
- **Machine Learning Classification**: Naive Bayes model trained on labeled phishing data (`CountVectorizer` + `MultinomialNB`) to predict phishing vs. safe.
- **🆕 Fraud Risk Engine**: A local, rule-based heuristic scanner that scores emails 0–100 across four social-engineering categories:
  - Advance-Fee / Inheritance Scams
  - Financial / Payment Urgency
  - Credential / Identity Harvesting
  - Pressure / Intimidation Tactics
- **🆕 Bulk CSV Scan**: Upload a CSV of many emails and run phishing + fraud scoring across the whole batch in one pass, with results downloadable as CSV.
- **🆕 Session Scan History**: Every scan performed in the session is logged with timestamp, verdict, and risk scores — exportable and clearable.
- **Model Training**: Retrain the phishing classifier anytime by uploading a new labeled dataset.
- **Interactive SOC-Console UI**: Dark, terminal-inspired Streamlit interface with live status pills, glowing risk gauges, and tabbed navigation for real-time analysis.

## 🧑‍💻 Technologies Used

- **Python** 🐍
- **Streamlit** 🌐
- **scikit-learn** 🤖
- **pandas** 📊
- **nltk** 🧠
- **Requests** 🌍
- **BeautifulSoup** 🍲

## 🎯 Installation & Setup

1. Clone the repository

   ```bash
   git clone https://github.com/yourusername/AI-Powered-Phishing-Detection-System.git
   cd AI-Powered-Phishing-Detection-System
   ```

2. Install Dependencies
   Create and activate a virtual environment, then install required packages:

   ```bash
   python -m venv venv
   source venv/bin/activate   # For macOS/Linux
   venv\Scripts\activate      # For Windows

   pip install -r requirements.txt
   ```

3. Run the App
   Start the Streamlit app to launch the console:

   ```bash
   streamlit run phishing_detector_app.py
   ```

4. Upload Dataset for Training (Optional)
   Upload a CSV file with columns `email_body` (content of the email) and `label` (1 for phishing, 0 for safe) in the **Model Training** tab to train the model. Sample datasets (`sample_emails.csv`, `training_dataset_large.csv`) are included in this repo for quick testing.

## 🔍 How to Use

The app is organized into four console tabs:

| Tab | Purpose |
|---|---|
| 🔍 **Threat Scan** | Paste a single email body → get a phishing verdict + fraud risk gauge with matched risk categories |
| 📦 **Bulk CSV Scan** | Upload a CSV of emails (`email_body` column) → batch phishing + fraud scoring, downloadable results |
| 🗂 **Scan History** | Review every scan run this session, with summary counts and CSV export |
| 🧠 **Model Training** | Upload a labeled CSV (`email_body`, `label`) to retrain the phishing classifier |

**Example Email to Test:**

- **Phishing Email**:

  ```text
  Congratulations! You've won a $1000 gift card. Click here to claim your prize: http://phishing.com
  ```

- **Safe Email**:

  ```text
  Hey, just checking in on our project. Let me know your availability for a meeting.
  ```

5. Check Prediction
   Click **▶ Run Threat Scan** to see the phishing verdict and fraud risk score for the email you entered.

## 📊 Results

The console displays:
- A **phishing verdict** (Phishing / Safe) based on trained model inference over the email body.
- A **fraud risk score and level** (None / Low / Medium / High) based on matched social-engineering keyword categories.
- A **URL signal score** summarizing domain/path/protocol/status characteristics of any links found.
- A running **scan history** log for the session, exportable to CSV.

## 🛠️ Contributing

Contributions are welcome! If you'd like to improve the system or add new features (e.g., a trained ML-based fraud classifier, header/SPF/DKIM analysis, live threat-intel lookups), feel free to fork the repository and submit a pull request.

## 🙌 Acknowledgements

- Streamlit for creating the amazing interface.
- scikit-learn for machine learning tools.
- Shields.io for badges.
- FontAwesome for awesome icons.

## 💻 Preview

## Phishing Email:

<img width="1920" height="2119" alt="screencapture-localhost-8501-2026-07-14-17_48_27" src="https://github.com/user-attachments/assets/53264ac2-f380-47f8-9742-858a51320629" />

## Safe Email:

<img width="1920" height="2104" alt="screencapture-localhost-8501-2026-07-14-17_49_35" src="https://github.com/user-attachments/assets/8921d5b7-d03d-4604-8575-f7bff5b588de" />

## 🌐 Connect with Me

- 📧 [Email](mailto:gauravghandat12@gmail.com)
- 💼 [LinkedIn](www.linkedin.com/in/gaurav-ghandat-68a5a22b4)
