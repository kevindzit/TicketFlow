import json
from datetime import datetime
import ollama

# categories the AI can assign
CATEGORIES = ['Network', 'Hardware', 'Software', 'Security', 'Email', 'Other']
PRIORITIES = ['Low', 'Medium', 'High', 'Critical']

def classify_ticket(subject, description):
    """Send ticket to Ollama for classification and summary."""
    prompt = f"""You are a helpdesk ticket classifier for an MSP. Analyze this support ticket and return a JSON response.

Ticket Subject: {subject}
Ticket Description: {description}

Return ONLY valid JSON with these fields:
- category: one of {CATEGORIES}
- priority: one of {PRIORITIES}
- urgency: Low, Medium, or High
- summary: a brief 1-2 sentence summary of the issue

JSON Response:"""

    try:
        response = ollama.chat(
            model='llama3.1',
            messages=[{'role': 'user', 'content': prompt}],
            options={'temperature': 0.3}
        )

        result_text = response['message']['content'].strip()

        # try to parse the json from the response
        # sometimes the model wraps it in markdown code blocks
        if '```json' in result_text:
            result_text = result_text.split('```json')[1].split('```')[0].strip()
        elif '```' in result_text:
            result_text = result_text.split('```')[1].split('```')[0].strip()

        result = json.loads(result_text)

        # validate the fields
        if result.get('category') not in CATEGORIES:
            result['category'] = 'Other'
        if result.get('priority') not in PRIORITIES:
            result['priority'] = 'Medium'

        return result

    except ConnectionError as e:
        print(f'[{datetime.utcnow()}] AI classification connection error: {e}')
        return {
            'category': 'Other',
            'priority': 'Medium',
            'urgency': 'Medium',
            'summary': f'{subject} - needs manual review',
            'ai_classified': False
        }
    except Exception as e:
        print(f'[{datetime.utcnow()}] AI classification error: {e}')
        return {
            'category': 'Other',
            'priority': 'Medium',
            'urgency': 'Medium',
            'summary': f'{subject} - needs manual review',
            'ai_classified': False
        }


def check_known_issues(category, description):
    """Check if the ticket matches any known issues using AI."""
    from app.models.known_issue import KnownIssue

    # get active known issues in the same category
    known = KnownIssue.query.filter_by(category=category, status='active').all()
    if not known:
        return None

    issues_text = ""
    for issue in known:
        issues_text += f"- {issue.title}: {issue.description}\n"

    prompt = f"""Compare this support ticket description to the known issues below. If the ticket matches a known issue, return the title of the matching issue. If no match, return "NO_MATCH".

Ticket: {description}

Known Issues:
{issues_text}

Return ONLY the title of the matching issue or "NO_MATCH"."""

    try:
        response = ollama.chat(
            model='llama3.1',
            messages=[{'role': 'user', 'content': prompt}],
            options={'temperature': 0.1}
        )

        result = response['message']['content'].strip()
        if result != 'NO_MATCH':
            # find the matching known issue
            for issue in known:
                if issue.title.lower() in result.lower():
                    return issue
        return None

    except Exception as e:
        print(f'Known issue check error: {e}')
        return None
