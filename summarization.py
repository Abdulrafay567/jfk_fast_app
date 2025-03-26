import os
from transformers import pipeline, BartTokenizer
from entity_recognition import generate_word_cloud, extract_entities
from pydantic import BaseModel
# Initialize the summarization pipeline
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")  # device=-1 for CPU

# Initialize the tokenizer
tokenizer = BartTokenizer.from_pretrained("facebook/bart-large-cnn")
class TextRequest(BaseModel):
    text: str
# Paths
folder_path = "jfk_text"  # Folder containing the documents
output_dir = "summaryoutput"  # Folder to save summaries
os.makedirs(output_dir, exist_ok=True)

# Get a list of already summarized files
existing_summaries = set(os.listdir(output_dir))

# Function to split text into meaningful chunks (e.g., paragraphs or sentences)
def split_text_into_chunks(text, max_tokens=500):
    paragraphs = text.split("\n\n")  # Split by double newlines (paragraphs)
    chunks = []
    current_chunk = ""
    
    for paragraph in paragraphs:
        tokens = tokenizer.tokenize(paragraph)
        if len(tokens) > max_tokens:
            words = paragraph.split()
            sub_chunks = [' '.join(words[i:i + max_tokens]) for i in range(0, len(words), max_tokens)]
            chunks.extend(sub_chunks)
        else:
            if len(tokenizer.tokenize(current_chunk + " " + paragraph)) > max_tokens:
                chunks.append(current_chunk.strip())
                current_chunk = paragraph
            else:
                current_chunk += " " + paragraph
    
    if current_chunk.strip():
        chunks.append(current_chunk.strip())
    
    return chunks

# Process each document separately
def summarize_all_files():
            for filename in os.listdir(folder_path):
                if filename.endswith(".md"):  # Process Markdown files
                    summary_filename = f"summary_{filename}"
                    summary_filepath = os.path.join(output_dir, summary_filename)
                    
                    if summary_filename in existing_summaries:
                        print(f"⏭ Skipping {filename}, already summarized.")
                        continue  # Skip this file
                    
                    file_path = os.path.join(folder_path, filename)
                    
                    with open(file_path, 'r', encoding='utf-8') as file:
                        text = file.read()

                    # Split text into chunks
                    chunks = split_text_into_chunks(text)

                    # Summarize each chunk
                    summaries = []
                    for chunk in chunks:
                        try:
                            summary = summarizer(
                                                    chunk, 
                                                    max_length=min(130, len(tokenizer.tokenize(chunk))),  # Ensure max_length is not more than input tokens
                                                    min_length=min(30, len(tokenizer.tokenize(chunk)) // 2),  # Ensure min_length is reasonable
                                                    do_sample=False
                                                )

                            summaries.append(summary[0]['summary_text'])
                        except Exception as e:
                            print(f"Error summarizing chunk in {filename}: {e}")

                    # Save individual document summary
                    summary_text = "\n\n".join(summaries)
                    with open(summary_filepath, "w", encoding="utf-8") as f:
                        f.write(summary_text)

                    print(f"✅ Summary saved for {filename} -> {summary_filepath}")

            print("🎉 All files summarized successfully!")

if __name__ == "__main__":
    summarize_all_files()    