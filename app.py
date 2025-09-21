from flask import Flask, render_template, request, jsonify
from utils.git_utils import GitUtils
from utils.ai_client import AIClient
from utils.review_utils import ReviewUtils
from config import Config

app = Flask(__name__)

# Initialize AI client
try:
    ai_client = AIClient()
except ValueError as e:
    print(f"Warning: {e}. Some features may not work without a valid HF API key.")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/review', methods=['POST'])
def review_pr():
    data = request.json
    pr_url = data.get('pr_url')

    if not pr_url:
        return jsonify({'error': 'PR URL is required'}), 400

    # Get PR details and diff
    pr_details = GitUtils.get_pr_details(pr_url)
    diff_content = GitUtils.get_pr_diff(pr_url)
    if isinstance(diff_content, dict) and "error" in diff_content:
        return jsonify({'error': diff_content['error']}), 400
    if 'error' in pr_details:
        pr_details = {
            'title': f"PR Review for {pr_url}",
            'description': 'Unable to fetch full PR details. Proceeding with diff analysis only.',
            'author': 'Unknown',
            'state': 'unknown',
            'base_branch': 'main',
            'head_branch': 'feature',
        }

    # Generate review and inline comments
    review_data = ai_client.generate_review(pr_details, diff_content)
    inline_data = ai_client.generate_inline_comments(diff_content)

    review = review_data.get("review") or review_data.get("error")
    inline_comments = inline_data.get("inline_comments") or [inline_data.get("error")]

    # Format and return JSON
    return jsonify({
        'pr_details': pr_details,
        'review': review,
        'inline_comments': inline_comments,
        'pr_score': ReviewUtils.calculate_pr_score(review),
        'suggestions': ReviewUtils.extract_code_suggestions(review)
    })

@app.route('/upload', methods=['POST'])
def upload_diff():
    data = request.json
    diff_text = data.get('diff_text')

    if not diff_text:
        return jsonify({'error': 'Diff text is required'}), 400

    pr_details = {
        'title': 'Uploaded Diff Review',
        'description': 'This review was generated from directly uploaded diff content.',
        'author': 'User',
        'state': 'uploaded'
    }

    review_data = ai_client.generate_review(pr_details, diff_text)
    inline_data = ai_client.generate_inline_comments(diff_text)

    review = review_data.get("review") or review_data.get("error")
    inline_comments = inline_data.get("inline_comments") or [inline_data.get("error")]

    return jsonify({
        'pr_details': pr_details,
        'review': review,
        'inline_comments': inline_comments,
        'pr_score': ReviewUtils.calculate_pr_score(review),
        'suggestions': ReviewUtils.extract_code_suggestions(review)
    })

if __name__ == '__main__':
    app.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG)
