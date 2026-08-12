---
description: Perform a security review of project code changes locally within the IDE
---

# Local Security Review Command

Perform a thorough security audit directly using the local IDE model. No external API keys or remote cloud actions required.

## Audit Checklist

1. **Injection Attacks**:
   - SQL / NoSQL / Command Injection
   - HTML Injection / XSS in PDF generation (`write_html` in `fpdf2`) or Streamlit UI (`unsafe_allow_html=True`)
2. **Authentication & Data Exposure**:
   - Hardcoded API keys, passwords, tokens, or sensitive credentials
   - Unsanitized user inputs written directly into HTML or PDF streams
3. **Insecure Code Execution**:
   - Usage of `eval()`, `exec()`, `pickle.loads()`, `os.system()`, or unescaped `subprocess` calls
4. **Supply Chain & Dependencies**:
   - Outdated or vulnerable Python packages in `requirements.txt`
5. **False Positive Filtering**:
   - Focus on actionable high-impact security vulnerabilities.

## How to Trigger

Type `/security-review` or ask the assistant: *"Lakukan security review lokal untuk kode ini"*.

