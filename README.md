🤖 AI-Powered PR Review Agent
This project is an intelligent code review agent designed to analyze pull requests from multiple Git providers. It uses a powerful AI model to provide comprehensive feedback on code structure, quality, potential bugs, and overall best practices.

This solution was developed for the CodeMate Hackathon, specifically addressing the "PR (Pull Request) Review Agent" problem statement.

<!-- Remember to replace this with a real screenshot of your app! -->

Key Features
Multi-Provider Support: Seamlessly analyzes pull requests from GitHub, GitLab, and Bitbucket.

Comprehensive AI Analysis: Leverages the tiiuae/falcon-7b-instruct model via Hugging Face to generate in-depth code reviews covering:

Code Structure & Quality

Potential Bugs & Issues

Security Vulnerabilities

Performance Optimizations

PR Quality Scoring: Calculates a quality score for each pull request based on the AI's analysis to provide an at-a-glance assessment.

Dual Review Modes:

URL Analysis: Simply paste a PR link for a full review.

Direct Diff Upload: Paste raw git diff content for a quick analysis without needing a URL.

Clean Web Interface: A simple and intuitive UI built with Flask and vanilla JavaScript for ease of use.

Tech Stack
Backend: Flask (Python)

AI Integration: Hugging Face transformers library

Frontend: HTML, CSS, JavaScript

Deployment: Docker

🚀 Getting Started
Follow these instructions to get the PR Review Agent running on your local machine.

Prerequisites
Python 3.9+

A Hugging Face account and an API Key with access to the tiiuae/falcon-7b-instruct model.

Step 1: Clone the Repository
git clone [https://github.com/sanalokeshreddy/pr-review-agent.git](https://github.com/sanalokeshreddy/pr-review-agent.git)
cd pr-review-agent

Step 2: Set Up Environment Variables
Create a file named .env in the root of the project.

Add your Hugging Face API key to this file:

HF_API_KEY=hf_YourHuggingFaceApiKeyGoesHere

Step 3: Create and Activate a Virtual Environment
# Create the environment
python -m venv venv

# Activate it
# On Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# On macOS/Linux:
source venv/bin/activate

Step 4: Install Dependencies
Install all the required Python packages from the requirements.txt file.

pip install -r requirements.txt

Step 5: Run the Application
Start the Flask server.

python app.py

The application will be available at http://127.0.0.1:5000. Open this URL in your browser to start reviewing pull requests!
