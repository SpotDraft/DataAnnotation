# Contract Review Interface

This Streamlit application provides an interface for reviewing contracts against a set of guidelines. It allows users to evaluate contract clauses, provide reasons for compliance or non-compliance, and suggest improvements.

## Features

- Display contract text with selectable paragraphs
- Review guidelines one by one
- Evaluate guideline quality and suggest improvements
- Determine if a guideline is followed, not followed, or not applicable
- Provide reasons for guideline status with quality evaluation
- Add comments with quality evaluation
- Suggest updated clause text with improvement options
- Save review results to Google Sheets
- Navigate through guidelines with progress tracking

## Requirements

- Python 3.6+
- Streamlit
- pandas
- streamlit-gsheets

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/contract-review-interface.git
   cd contract-review-interface
   ```

2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

3. Set up your Google Sheets connection:
   - Create a Google Cloud project and enable the Google Sheets API
   - Create a service account and download the JSON key
   - Share your Google Sheet with the service account email

4. Create a `.streamlit/secrets.toml` file with your Google Sheets credentials:
   ```toml
   spreadsheet = "YOUR_SPREADSHEET_ID"
   [connections.gsheets]
    private_key_id = "YOUR_PRIVATE_KEY_ID"
    private_key = "YOUR_PRIVATE_KEY"
    client_email = "YOUR_CLIENT_EMAIL"
    client_id = "YOUR_CLIENT_ID"
    type = "YOUR_TYPE"
    project_id = "YOUR_PROJECT_ID"
    auth_uri = "YOUR_AUTH_URI"
    token_uri = "YOUR_TOKEN_URI"
    auth_provider_x509_cert_url = "YOUR_AUTH_PROVIDER"
    client_x509_cert_url = "YOUR_CLIENT_X509"
    universe_domain = "YOUR_DOMAIN"
   
   ```

## Usage

Run the Streamlit app:

```
streamlit run app.py
```

Navigate to the provided URL to access the Contract Review Interface.

## Data Structure

The application expects the following worksheets in your Google Sheet:

1. "Data": Contains the guidelines and contract text
2. "ReviewResults": Stores the review results

### Input Data Format

The "Data" worksheet should have the following columns:

- `id`: Unique identifier for each guideline
- `guideline`: The text of the guideline
- `contract`: The full text of the contract (this will be the same for all rows)
- `reason`: ...
- `status`: ...
- `comment`: ...
- `updated_clause_text`: ...

Example:

| id | guideline | contract | reason | status | comment | updated_clause_text |
|----|-----------|----------|--------|--------|---------| ------------------- |
| 1  | Ensure all parties are clearly identified | Full contract text here... | counterparty is missing | NOT_FOLLOWED | Please add counterparty | Counterparty is.. |
| ... | ... | ... |

### Output Data Format

The "ReviewResults" worksheet will store the review results with the following columns:

- `id`: Unique identifier for the guideline (matching the input data)
- `guideline`: The text of the guideline
- `guideline_quality`: Quality assessment of the guideline (Pending, Excellent, Good, Better, Bad)
- `guideline_improvement`: Suggested improvement area for the guideline
- `guideline_improvement_other`: Custom improvement suggestion if "Other" was selected
- `status`: Whether the guideline is FOLLOWED, NOT_FOLLOWED, or NOT_APPLICABLE
- `reason`: Explanation for the status
- `reason_quality`: Quality assessment of the reason (Pending, Excellent, Good, Better, Bad)
- `reason_improvement_other`: Custom improvement suggestion for the reason if "Other" was selected
- `comment`: Additional comments
- `comment_quality`: Quality assessment of the comment (Pending, Excellent, Good, Better, Bad)
- `comment_improvement_other`: Custom improvement suggestion for the comment if "Other" was selected
- `selected_sources`: Comma-separated list of paragraph numbers from the contract text that are relevant to this guideline
- `update_clause_text`: Suggested updated text for the relevant clause
- `update_clause_improvement`: Assessment of the updated clause text (NA, Changes too extensive, Does not meet guideline, Content inaccuracies, Other)
- `update_clause_improvement_other`: Custom improvement suggestion for the updated clause if "Other" was selected

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
