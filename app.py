from fastapi import FastAPI,HTTPException
from pydantic import BaseModel
from fastapi.responses import FileResponse
import gradio as gr
from entity_recognition import  extract_entities   # Import entity extraction function
from entity_recognition import generate_word_cloud 
from wordcloud import WordCloud
from summarization import summarizer
import os
from utils import list_files,process_file

# import threading
import time
app = FastAPI()

# Request Model
class TextRequest(BaseModel):
    text: str

# Summarization Endpoint
@app.post("/summarize")
def summarize_text(request: TextRequest):
    chunks = [request.text[i:i+500] for i in range(0, len(request.text), 500)]
    summaries = []
    for chunk in chunks:
        try:
            summary = summarizer(
                chunk, 
                max_length=130, 
                min_length=30, 
                do_sample=False,
                truncation=True  # Explicitly enable truncation
            )
            summaries.append(summary[0]['summary_text'])
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Summarization error: {str(e)}")
    return {"summary": " ".join(summaries)}

# Entity Recognition Endpoint
@app.post("/entities")
def extract_entities_endpoint(request: TextRequest):
    return {"entities": extract_entities(request.text)}

# Word Cloud Generation Endpoint
@app.post("/wordcloud")
def generate_word_cloud(request: TextRequest):
    wordcloud = WordCloud(width=800, height=600,max_font_size=40, min_font_size=10, background_color="white").generate(request.text)
    img_path = "wordcloud.png"
    wordcloud.to_file(img_path)
    return FileResponse(img_path, media_type="image/png", filename="wordcloud.png")



# Gradio UI
with gr.Blocks() as iface:
    gr.Markdown("File Selector")
    gr.Markdown("Choose a file and process it for summarization, entity recognition, and word cloud generation.")

    # File selection dropdown
    file_dropdown = gr.Dropdown(choices=list_files(), label="Select a File", interactive=True)
    process_button = gr.Button("Process")


    # Outputs
    output_summary = gr.Textbox(label="Summarized Text")
    output_entities = gr.JSON(label="Entities")
    output_wordcloud = gr.Image(label="Word Cloud")

    
    # Process selected file
    process_button.click(
        fn=process_file, 
        inputs=file_dropdown, 
        outputs=[output_summary, output_entities, output_wordcloud]
    )



if __name__ == "__main__":
    iface.launch(server_name="0.0.0.0", server_port=7860, share=False)
    time.sleep(1)  # Allow time for logs
    print("\n\n **Gradio Interface is LIVE at: http://localhost:7860 ** \n")