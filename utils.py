import os
from entity_recognition import extract_entities
from entity_recognition import generate_word_cloud
from pydantic import BaseModel

# Define paths
TEXT_FOLDER = "jfk_text"
SUMMARY_FOLDER = "summaryoutput"

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
    """Process a file to generate summary, entities, and word cloud."""
    file_path = os.path.join(TEXT_FOLDER, file_name)
    
    if not os.path.exists(file_path):
        return "Error: File not found", {}, None
    
    # Read content
    text = read_file(file_path)
    
    # Get precomputed summary
    summary = get_summary(file_name)
    
    # Extract entities
    entities = {"entities": extract_entities(text)}
    
    wordcloud_path = os.path.join("wordcloud_output", f"wordcloud_{file_name}.png")  # Ensure a valid file path
    os.makedirs("wordcloud_output", exist_ok=True)  # Ensure output directory exists
    generate_word_cloud(text,wordcloud_path)  # Correct function call


    return summary, entities, wordcloud_path
