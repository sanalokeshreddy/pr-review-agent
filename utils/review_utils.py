import re

class ReviewUtils:
    @staticmethod
    def format_review_response(review_text):
        """Format the AI review response for better readability"""
        # Split into sections if they exist
        sections = re.split(r'\n(?=[A-Z][a-z]+(?: [A-Z][a-z]+)*:)', review_text)
        
        formatted_html = ""
        for section in sections:
            if ':' in section:
                title, content = section.split(':', 1)
                formatted_html += f"<h3>{title.strip()}</h3>"
                # Convert bullet points to HTML
                content = re.sub(r'^\s*[-*]\s+(.+)$', r'<li>\1</li>', content, flags=re.MULTILINE)
                if '<li>' in content:
                    content = f"<ul>{content}</ul>"
                formatted_html += f"<div>{content.strip()}</div>"
            else:
                formatted_html += f"<p>{section.strip()}</p>"
        
        return formatted_html
    
    @staticmethod
    def calculate_pr_score(review_text):
        """Calculate a simple PR quality score based on review content"""
        positive_indicators = [
            'good', 'excellent', 'well', 'properly', 'clean', 'efficient',
            'secure', 'maintainable', 'readable', 'follows', 'standard'
        ]
        
        negative_indicators = [
            'error', 'issue', 'problem', 'bug', 'vulnerability', 'security risk',
            'inefficient', 'poor', 'bad', 'wrong', 'incorrect', 'missing'
        ]
        
        text_lower = review_text.lower()
        positive_count = sum(1 for word in positive_indicators if word in text_lower)
        negative_count = sum(1 for word in negative_indicators if word in text_lower)
        
        if positive_count + negative_count == 0:
            return 80  # Neutral score if no indicators found
        
        score = (positive_count / (positive_count + negative_count)) * 100
        return round(score)
    
    @staticmethod
    def extract_code_suggestions(review_text):
        """Extract code suggestions from review text"""
        suggestions = []
        # Look for patterns that might indicate code suggestions
        lines = review_text.split('\n')
        
        for line in lines:
            if any(phrase in line.lower() for phrase in ['suggest', 'recommend', 'consider', 'instead of', 'use']):
                suggestions.append(line.strip())
        
        return suggestions if suggestions else ["No specific code suggestions found in the review."]