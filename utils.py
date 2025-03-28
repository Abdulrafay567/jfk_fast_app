import os
from entity_recognition import extract_entities
from pydantic import BaseModel
from wordcloud import WordCloud
# Define paths
TEXT_FOLDER = "jfk_text"
SUMMARY_FOLDER = "summaryoutput"
MINDMAP_FOLDER = "mindmap_output"
WORDCLOUD_FOLDER = "wordcloud_output"

# Request model
class TextRequest(BaseModel):
    text: str

def list_files():
    """List all Markdown (.md) files in the 'jfk_text' folder."""
    if os.path.exists(TEXT_FOLDER):
        return [f for f in os.listdir(TEXT_FOLDER) if f.endswith(".md")]
    return []

def read_file(file_path):
    """Read the content of a given file."""
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()

def get_summary(file_name):
    """Get the summary of a file if it exists."""
    summary_file = f"summary_{file_name}"
    summary_path = os.path.join(SUMMARY_FOLDER, summary_file)
    
    if os.path.exists(summary_path):
        return read_file(summary_path)
    return "Summary not found."

def process_file(file_name):
    try:
        # 1. Validate input and paths
        if not file_name or not os.path.exists(os.path.join(TEXT_FOLDER, file_name)):
            raise FileNotFoundError("Invalid file selection")
        
        # 2. Read file
        text = read_file(os.path.join(TEXT_FOLDER, file_name))
        
        # 3. Generate outputs
        wordcloud_path = os.path.join(WORDCLOUD_FOLDER, f"wordcloud_{file_name}.png")
        os.makedirs(WORDCLOUD_FOLDER, exist_ok=True)
        
        # 4. Create visualizations
        wc = WordCloud(width=800, height=400, background_color="white").generate(text)
        wc.to_file(wordcloud_path)
        
    
        
        return (
            text,
            get_summary(file_name),
            {"entities": extract_entities(text)},
            wordcloud_path,
            
        )
    except Exception as e:
        error_msg = f"Error: {str(e)}"
        return error_msg, error_msg, {"entities": {}}, None, f"<div>{error_msg}</div>"


# def process_file(file_name):
#     try:
#         # 1. Validate input and paths
#         if not file_name or not os.path.exists(os.path.join(TEXT_FOLDER, file_name)):
#             raise FileNotFoundError("Invalid file selection")
        
#         # 2. Read file
#         text = read_file(os.path.join(TEXT_FOLDER, file_name))
        
#         # 3. Generate outputs
#         wordcloud_path = os.path.join(WORDCLOUD_FOLDER, f"wordcloud_{file_name}.png")
#         os.makedirs(WORDCLOUD_FOLDER, exist_ok=True)
        
#         # 4. Create visualizations
#         wc = WordCloud(width=800, height=400, background_color="white").generate(text)
#         wc.to_file(wordcloud_path)
        
#         # 5. Generate mind map HTML
#         mindmap_html = generate_mind_map(text)
        
#         return (
#             text,
#             get_summary(file_name),
#             {"entities": extract_entities(text)},
#             wordcloud_path,  # Word Cloud image path
#             mindmap_html     # Mind Map HTML content
#         )
#     except Exception as e:
#         error_msg = f"Error: {str(e)}"
#         return error_msg, error_msg, {"entities": {}}, None, f"<div>{error_msg}</div>"    
# # def process_file(file_name):
#     """Process file and return all outputs including mind map."""
#     try:
#         if not file_name:  # Check if file_name is empty
#             raise ValueError("No file selected")
        
#         file_path = os.path.join(TEXT_FOLDER, file_name)
#         if not os.path.exists(file_path):
#             raise FileNotFoundError(f"File {file_name} not found in {TEXT_FOLDER}")
        
#         text = read_file(file_path)
#         return (
#             text,  # Full text
#             get_summary(file_name),  # Summary
#             {"entities": extract_entities(text)},  # Entities
#             generate_word_cloud(text, os.path.join(WORDCLOUD_FOLDER, f"wordcloud_{file_name}.png")),  # Word Cloud
#             generate_mind_map(text)  # Mind Map (returns HTML)
#         )
#     except Exception as e:
#         error_msg = f"Error: {str(e)}"
#         return error_msg, error_msg, {"entities": {}}, None, "<div>Error generating visualization</div>"
#     return summary, entities, wordcloud_path
# from entity_recognition import extract_entities
# from wordcloud import WordCloud
# from summarization import summarizer
# def process_file(filename):
#     file_path = f"your_data_folder/{filename}"  # Update this to the correct file path
#     try:
#         with open(file_path, "r", encoding="utf-8") as f:
#             text = f.read()

#         # Summarize the text
#         chunks = [text[i:i+500] for i in range(0, len(text), 500)]
#         summaries = []
#         for chunk in chunks:
#             summary = summarizer(chunk, max_length=130, min_length=30, do_sample=False, truncation=True)
#             summaries.append(summary[0]['summary_text'])

#         # Extract entities
#         entities = extract_entities(text)

#         # Generate word cloud
#         wordcloud = WordCloud(width=800, height=600, max_font_size=40, min_font_size=10, background_color="white").generate(text)
#         img_path = f"wordcloud_output/wordcloud_{filename}.png"  # Ensure the path is valid
#         wordcloud.to_file(img_path)

#         return text, " ".join(summaries), entities, img_path  # ✅ Returning exactly 4 values

#     except Exception as e:
#         return f"Error processing file: {str(e)}", "", {}, ""