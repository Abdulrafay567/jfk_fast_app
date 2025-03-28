import os
import torch
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from gliner import GLiNER
import spacy
import re
# Load spaCy English model
nlp = spacy.load("en_core_web_sm")

# Function to remove stop words
def preprocess_text(text):
    doc = nlp(text)
    filtered_words = [ token.lemma_  # Convert to base form
                    for token in doc
                    if not token.is_stop  # Remove stop words
                    and not token.is_punct  # Remove punctuation
                    and not token.is_digit  # Remove numbers
                    and len(token.text) > 2  ]
    
    return " ".join(filtered_words)
    
# 📂 Define input/output directories
input_dir = "summaryoutput"  # Folder containing summarized documents
entity_output_dir = "extracted_entities"  # Folder to save extracted entities
os.makedirs(entity_output_dir, exist_ok=True)

# ⚡ Load Named Entity Recognition (NER) model
device = "cuda" if torch.cuda.is_available() else "cpu"  # Use GPU if available
model = GLiNER.from_pretrained("urchade/gliner_medium-v2.1").to(device)

# Define labels for entity extraction
labels = ["person", "organization", "location", "date", "document", "event", "role", "cryptonym", "operation", "nationality", "contact","SUBJECT","REFERENCE","FROM","TO","DATE","REF","INFO"]
#  Get already processed files
existing_entity_files = set(os.listdir(entity_output_dir))
def extract_entities(text):
    entities = model.predict_entities(text, labels)
    extracted = {}
    regex_patterns = {
        "TO": r"(?i)\bTO[:\s]+([^\n]+)",
        "FROM": r"(?i)\bFROM[:\s]+([^\n]+)",
        "DATE": r"(?i)\bDATE[:\s]+([^\n]+)",
        "REF": r"(?i)\bREF[:\s]+([^\n]+)",
        "SUBJECT": r"(?i)\bSUBJECT[:\s]+([^\n]+)",
    }
    for label, pattern in regex_patterns.items():
        matches = re.findall(pattern, text)
        if matches:
            # Clean up matches
            cleaned_matches = [m.strip().rstrip(')').lstrip(',') for m in matches]
            extracted[label] = list(set(cleaned_matches))  # Remove duplicates
    for entity in entities:
        entity_type = entity["label"]
        entity_text = entity["text"].strip().rstrip(')').lstrip(',')
        if entity_type not in extracted:
            extracted[entity_type] = []
        if entity_text not in extracted[entity_type]:  # Avoid duplicates
            extracted[entity_type].append(entity_text)
    return extracted
# def extract_entities(text):
#     entities = model.predict_entities(text, labels)
#     extracted = {}
#     regex_patterns = {
#         "TO": r"(?i)\bTO[:\s]+([^\n]+)",    # Matches "TO: some text"
#         "FROM": r"(?i)\bFROM[:\s]+([^\n]+)",  # Matches "FROM: some text"
#         "DATE": r"(?i)\bDATE[:\s]+([^\n]+)",  # Matches "DATE: some text"
#         "REF": r"(?i)\bREF[:\s]+([^\n]+)",    # Matches "REF: some text"
#         "SUBJECT": r"(?i)\bSUBJECT[:\s]+([^\n]+)",  # Matches "SUBJECT: some text"
#     }
#     # Apply regex patterns
#     for label, pattern in regex_patterns.items():
#         matches = re.findall(pattern, text)
#         if matches:
#             extracted[label] = matches

#     for entity in entities:
#         entity_type = entity["label"]
#         entity_text = entity["text"]
#         if entity_type not in extracted:
#             extracted[entity_type] = []
#         extracted[entity_type].append(entity_text)
#     return extracted
#  Function to generate word cloud
def generate_word_cloud(text, output_filename):
    os.makedirs(os.path.dirname(output_filename), exist_ok=True)
    filtered_text = preprocess_text(text)
    wordcloud = WordCloud(width=800, height=400, background_color="white").generate(filtered_text)
    wordcloud.to_file(output_filename)
    
    
    # Save word cloud image
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")
    plt.savefig(output_filename, bbox_inches="tight")
    plt.close()

#  Process each document
def extract_entities_from_summaries():
            all_text = ""  # Store all text for a combined word cloud

            for filename in os.listdir(input_dir):
                if filename.endswith(".md"):  # Process Markdown files
                    entity_file = f"entities_{filename}"
                    word_cloud_file = f"wordcloud_{filename}.png"
                    entity_file_path = os.path.join(entity_output_dir, entity_file)
                    word_cloud_path = os.path.join(entity_output_dir, word_cloud_file)

                    # ⏭ Skip if entity file & word cloud already exist
                    if entity_file in existing_entity_files and word_cloud_file in existing_entity_files:
                        print(f"⏩ Skipping {filename}, already processed.")
                        continue

                    file_path = os.path.join(input_dir, filename)
                    
                    with open(file_path, "r", encoding="utf-8") as file:
                        text = file.read()
                    
                    all_text += text + "\n\n"  # Collect text for a combined word cloud

                    #  Extract entities
                    if entity_file not in existing_entity_files:
                        entities = extract_entities(text)

                        #  Save extracted entities to a file
                        with open(entity_file_path, "w", encoding="utf-8") as f:
                            for entity_type, entity_words in entities.items():
                                f.write(f"{entity_type}:")
                                f.write(", ".join(entity_words) + "\n\n")

                        print(f" Extracted entities saved for {filename} -> {entity_file_path}")

                    #  Generate a word cloud for the document
                    if word_cloud_file not in existing_entity_files:
                        generate_word_cloud(text, word_cloud_path)
                        print(f"🌥 Word cloud saved for {filename} -> {word_cloud_path}")

            #  Generate a word cloud for the entire dataset
            combined_word_cloud_path = os.path.join(entity_output_dir, "wordcloud_combined.png")

            if all_text.strip() and "wordcloud_combined.png" not in existing_entity_files:
                generate_word_cloud(all_text, combined_word_cloud_path)
                print(f"🌥 Combined word cloud saved -> {combined_word_cloud_path}")

            print(" Entity extraction and word cloud generation completed!")


if __name__ == "__main__"and False:
    extract_entities_from_summaries()
