import re
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2.service_account import Credentials

# Define the markdown text
markdown_text = """# Product Team Sync - May 15, 2023

## Attendees
- Sarah Chen (Product Lead)
- Mike Johnson (Engineering)
- Anna Smith (Design)
- David Park (QA)

## Agenda

### 1. Sprint Review
* Completed Features
  * User authentication flow
  * Dashboard redesign
  * Performance optimization
    * Reduced load time by 40%
    * Implemented caching solution
* Pending Items
  * Mobile responsive fixes
  * Beta testing feedback integration

### 2. Current Challenges
* Resource constraints in QA team
* Third-party API integration delays
* User feedback on new UI
  * Navigation confusion
  * Color contrast issues

### 3. Next Sprint Planning
* Priority Features
  * Payment gateway integration
  * User profile enhancement
  * Analytics dashboard
* Technical Debt
  * Code refactoring
  * Documentation updates

## Action Items
- [ ] @sarah: Finalize Q3 roadmap by Friday
- [ ] @mike: Schedule technical review for payment integration
- [ ] @anna: Share updated design system documentation
- [ ] @david: Prepare QA resource allocation proposal

## Next Steps
* Schedule individual team reviews
* Update sprint board
* Share meeting summary with stakeholders

## Notes
* Next sync scheduled for May 22, 2023
* Platform demo for stakeholders on May 25
* Remember to update JIRA tickets

---
Meeting recorded by: Sarah Chen
Duration: 45 minutes
"""

# Authenticate Google Docs API
SCOPES = [
    'https://www.googleapis.com/auth/documents',
    'https://www.googleapis.com/auth/drive'
]
SERVICE_ACCOUNT_FILE = '/content/spatial-earth-448622-f4-60081961f93c.json'  # Replace with your file path

# Authenticate using service account credentials
def authenticate_google_docs():
    creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    docs_service = build('docs', 'v1', credentials=creds)
    return creds, docs_service

# Parse markdown text and create a document in Google Docs
def create_google_doc(markdown_text):
    try:
        creds, docs_service = authenticate_google_docs()

        # Create a new Google Doc
        document = docs_service.documents().create(body={"title": "Product Team Sync"}).execute()
        document_id = document.get('documentId')
        print(f"Created document with ID: {document_id}")

        # Parse markdown and apply styles
        requests = parse_markdown(markdown_text)

        # Update Google Doc with parsed content
        docs_service.documents().batchUpdate(documentId=document_id, body={"requests": requests}).execute()
        print(f"Document updated successfully: https://docs.google.com/document/d/{document_id}")

        # Share the document with your Google account
        share_document(document_id, creds, "aakashshoraan7@gmail.com")  # Replace with your email

    except HttpError as error:
        print(f"An error occurred: {error}")

# Parse markdown text into Google Docs API requests
def parse_markdown(markdown_text):
    requests = []
    current_index = 1  # Start at index 1 in the document

    lines = markdown_text.split('\n')
    for line in lines:
        if line.startswith('# '):  # Heading 1
            text = line[2:]
            requests.append(insert_text_request(text, current_index))
            requests.append(update_text_style_request(current_index, len(text), 'HEADING_1'))
            current_index += len(text) + 1
        elif line.startswith('## '):  # Heading 2
            text = line[3:]
            requests.append(insert_text_request(text, current_index))
            requests.append(update_text_style_request(current_index, len(text), 'HEADING_2'))
            current_index += len(text) + 1
        elif line.startswith('### '):  # Heading 3
            text = line[4:]
            requests.append(insert_text_request(text, current_index))
            requests.append(update_text_style_request(current_index, len(text), 'HEADING_3'))
            current_index += len(text) + 1
        elif line.startswith('- [ ]'):  # Checkbox
            text = f"\u2610 {line[6:]}"  # Add checkbox symbol
            requests.append(insert_text_request(text, current_index))
            current_index += len(text) + 1
        elif line.startswith('- '):  # Bullet point
            text = f"\u2022 {line[2:]}"  # Add bullet point symbol
            requests.append(insert_text_request(text, current_index))
            current_index += len(text) + 1
        elif line.strip():  # Normal text
            text = line.strip()
            requests.append(insert_text_request(text, current_index))
            current_index += len(text) + 1

    return requests

# Helper function to create text requests
def insert_text_request(text, index):
    """Creates a request to insert text."""
    return {
        'insertText': {
            'location': {
                'index': index
            },
            'text': f"{text}\n"
        }
    }

# Helper function to create style requests
def update_text_style_request(start_index, length, style):
    # Creates a request to apply text style.
    text_style = {
        'bold': True if style.startswith('HEADING') else False,
    }
    if style == 'HEADING_1':
        text_style['fontSize'] = {'magnitude': 18, 'unit': 'PT'}
    elif style == 'HEADING_2':
        text_style['fontSize'] = {'magnitude': 16, 'unit': 'PT'}
    elif style == 'HEADING_3':
        text_style['fontSize'] = {'magnitude': 14, 'unit': 'PT'}

    return {
        'updateTextStyle': {
            'range': {
                'startIndex': start_index,
                'endIndex': start_index + length
            },
            'textStyle': text_style,
            'fields': '*'
        }
    }

# Share the document with a specific email
def share_document(document_id, creds, email):
    drive_service = build('drive', 'v3', credentials=creds)

    # Add permissions
    drive_service.permissions().create(
        fileId=document_id,
        body={
            'type': 'user',
            'role': 'writer',  # Change to 'reader' for view-only access
            'emailAddress': email
        },
        fields='id'
    ).execute()

    print(f"Shared document with {email}")

# Run the script
if __name__ == "__main__":
    create_google_doc(markdown_text)
