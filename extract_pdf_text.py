import PyPDF2

pdf_path = "/Users/soliv112/Library/CloudStorage/GoogleDrive-sergioro.2007@gmail.com/My Drive/SimpleLearn/7 - ME-AGS CAPSTONE PROJECT/Support_Documents/Healthcare_Assistant/1754386259_capstone_problem_statement_agentic_healthcare_assistant_for_medical_task_automation.pdf"
output_path = "extracted_text.txt"

with open(pdf_path, "rb") as file:
    reader = PyPDF2.PdfReader(file)
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"

with open(output_path, "w", encoding="utf-8") as out:
    out.write(text)

print(f"Extracted text saved to {output_path}")