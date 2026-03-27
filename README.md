# 🤖 AI-ATS Resume Architect
**Tailor. Optimize. Validate. In Seconds.**

An intelligent, local-first resume generator that uses **LangChain**, **Ollama**, and **LangSmith** to transform your master career history into a high-scoring, one-page resume tailored specifically to any Job Description (JD).

---

## 🎯 The Problem
Standard resumes are "one size fits all," which leads to low ATS (Applicant Tracking System) scores. Manual tailoring is time-consuming. Most AI resume tools are either paid cloud services or produce "fluffy" content that recruiters ignore.

## 💡 The Solution
This tool automates the **strategic** part of resume writing:
1.  **JD Extraction:** Identifying the exact keywords an ATS is looking for.
2.  **Strategic Selection:** Picking only the relevant 40% of your experience that matches the role.
3.  **Quantifiable Rewriting:** Forcing every bullet point into the **Google XYZ Formula**.
4.  **Hard Constraints:** Strictly enforcing a **1-page limit** and **ATS readability**.

---

## 🛠️ Tech Stack & Decisions

| Component | Technology | Why? |
| :--- | :--- | :--- |
| **Orchestration** | **LangChain** | Handles the complex "chaining" of JD analysis -> Tailoring -> Validation. |
| **Inference** | **Ollama** | Enables free, private, local execution using models like **Llama 3** or **Mistral**. |
| **Observability** | **LangSmith** | Essential for debugging the AI's "thought process" and improving prompt accuracy. |
| **Data Storage** | **JSON** | A structured "Master Profile" allows the AI to programmatically "pick and choose" data. |
| **PDF Rendering** | **WeasyPrint / HTML** | Allows precise CSS control over the "1-page" constraint. |

---

## 🚀 Key Features

- [ ] **ATS Score > 80:** Automated keyword injection and structural validation.
- [ ] **Google XYZ Enforcement:** Automatically converts "I managed a team" to "Managed a team of 10, increasing output by 20% through Agile implementation."
- [ ] **Page Buffer Logic:** If the AI writes too much, the system triggers a "Truncation Chain" to trim the least relevant content until it fits on exactly one page.
- [ ] **Privacy First:** By using Ollama, your personal career data never leaves your machine.

---

## 📂 Project Structure (Planned)

```text
├── data/
│   └── master_profile.json   # Your full career "Source of Truth"
├── src/
│   ├── chains/
│   │   ├── analyzer.py       # JD Keyword Extraction
│   │   ├── generator.py      # The "Tailoring" Engine
│   │   └── validator.py      # The "1-page" checker
│   ├── templates/            # HTML/CSS ATS-friendly layouts
│   └── main.py               # The CLI Entry point
├── tests/                    # LangSmith eval datasets
├── .env                      # API Keys (LangSmith/OpenAI)
└── README.md