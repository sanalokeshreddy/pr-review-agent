import os
from transformers import pipeline
from config import Config

class AIClient:
    def __init__(self, api_key=None):
        """
        Initialize the AI client using Hugging Face free models.
        """
        self.api_key = api_key or Config.HF_API_KEY
        if not self.api_key:
            raise ValueError("HF_API_KEY is required for AI review")

        # Initialize Hugging Face text-generation pipeline (Falcon-7B instruct)
        self.generator = pipeline(
            "text-generation",
            model="tiiuae/falcon-7b-instruct",
            device=-1,  # CPU; set 0 for GPU
            use_auth_token=self.api_key
        )

    def _query(self, prompt, max_length=500):
        """Helper to query HF model"""
        output = self.generator(prompt, max_length=max_length, do_sample=True, temperature=0.2)
        return output[0]["generated_text"]

    def generate_review(self, pr_details, diff_content):
        """Generate a comprehensive PR review."""
        prompt = self._create_review_prompt(pr_details, diff_content)
        try:
            output = self._query(prompt)
            return {"review": output}
        except Exception as e:
            return {"error": f"Error generating review: {str(e)}"}

    def generate_inline_comments(self, diff_content):
        """Generate inline comments for a diff."""
        prompt = self._create_inline_comment_prompt(diff_content)
        try:
            output = self._query(prompt)
            comments = [line.strip() for line in output.split("\n") if line.strip()]
            if not comments:
                comments = [{"comment": "No inline comments generated"}]
            return {"inline_comments": comments}
        except Exception as e:
            return {"error": f"Error generating inline comments: {str(e)}"}

    def _create_review_prompt(self, pr_details, diff_content):
        return f"""
You are an expert code reviewer. Review this pull request:

Title: {pr_details.get('title', 'N/A')}
Description: {pr_details.get('description', 'N/A')}

Diff content:
{diff_content}

Provide:
1. Code structure & organization feedback
2. Bugs/issues
3. Code style suggestions
4. Security considerations
5. Performance improvements
6. Readability & maintainability tips
7. Overall assessment

Format response with clear bullet points and sections.
Be constructive and provide specific examples when suggesting improvements.
"""

    def _create_inline_comment_prompt(self, diff_content):
        return f"""
Analyze the following diff and generate inline comments for each change:
Focus on:
- Potential bugs or logical errors
- Code style inconsistencies
- Security vulnerabilities
- Performance issues
- Missing tests or documentation

Diff content:
{diff_content}

Format response in a clear, structured way for parsing.
"""
