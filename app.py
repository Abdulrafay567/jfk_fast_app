from fastapi import FastAPI,HTTPException
from pydantic import BaseModel
from fastapi.responses import FileResponse
import gradio as gr
from entity_recognition import  extract_entities # Import entity extraction function
#from entity_recognition import generate_word_cloud 
from wordcloud import WordCloud
from summarization import summarizer
from utils import list_files,process_file

# import threading
TEXT_FOLDER = "jfk_text"
app = FastAPI()

# Request Model
class TextRequest(BaseModel):
    text: str
import pygraphviz as pgv
import re
import os

def generate_mermaid_mindmap(text):
    entities = extract_entities(text)
    print("Extracted Entities:", entities)
    
    # Create a directed graph
    G = pgv.AGraph(directed=True, rankdir="TB", bgcolor="white")
    
    # Add root node
    G.add_node("Document", shape="ellipse", style="filled", fillcolor="lightblue", label="Document")
    
    # Keep track of node names to ensure uniqueness
    node_counter = {}
    
    for category, values in entities.items():
        # Sanitize category name for the node identifier
        safe_category = re.sub(r'[^a-zA-Z0-9_]', '', category)
        if not safe_category or safe_category.startswith('.'):
            safe_category = "Category_" + str(hash(category) % 10000)
        
        # Add category node
        G.add_node(safe_category, shape="box", style="filled", fillcolor="lightgreen", label=category)
        G.add_edge("Document", safe_category)
        
        for value in values:
            # Clean up the value
            cleaned_value = value.strip().rstrip(')').lstrip(',')
            if not cleaned_value:
                cleaned_value = "Unknown"
            
            # Truncate long values for readability (max 50 characters)
            if len(cleaned_value) > 50:
                cleaned_value = cleaned_value[:47] + "..."
            
            # Sanitize value name for the node identifier
            safe_value = re.sub(r'[^a-zA-Z0-9_]', '', cleaned_value)
            if not safe_value:
                safe_value = "Value_" + str(hash(cleaned_value) % 10000)
            
            # Ensure unique node name
            node_key = safe_value
            node_counter[node_key] = node_counter.get(node_key, 0) + 1
            if node_counter[node_key] > 1:
                safe_value = f"{safe_value}_{node_counter[node_key]}"
            
            # Add value node
            G.add_node(safe_value, shape="ellipse", style="filled", fillcolor="lightyellow", label=cleaned_value)
            G.add_edge(safe_category, safe_value)
    
    # Ensure the output directory exists
    output_dir = "mindmap_output"
    os.makedirs(output_dir, exist_ok=True)
    
    # Render the graph to a PNG file
    output_path = os.path.join(output_dir, "mindmap.png")
    G.draw(output_path, format="png", prog="dot")  # 'dot' is the layout engine
    
    return output_path
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
    wordcloud = WordCloud(width=800, height=800,max_font_size=40, min_font_size=10, background_color="white").generate(request.text)
    img_path = "wordcloud.png"
    wordcloud.to_file(img_path)
    return FileResponse(img_path, media_type="image/png", filename="wordcloud.png")


# Gradio UI
with gr.Blocks() as iface:
    gr.Markdown("File Selector")
    gr.Markdown("Choose a file and process it for summarization, entity recognition, and word cloud generation.")

    # **File selection & process button**
    with gr.Row():
        file_dropdown = gr.Dropdown(choices=list_files(), label=" Select a File", interactive=True)
        process_button = gr.Button(" Process")

    # **First Row (Original Text & Summary)**
    with gr.Row():
        full_doc_text = gr.Textbox(label=" Full Document")
        output_summary = gr.Textbox(label=" Summarized Text")

    # **Second Row (Entities & Word Cloud)**
    with gr.Row():
        output_entities = gr.JSON(label=" Entities")
        output_wordcloud = gr.Image(label=" Word Cloud")
    with gr.Row():
        generate_mindmap_button = gr.Button("Generate Mind Map")
        output_mindmap = gr.Image(label="Mind Map")  # Use HTML instead of Textbox

    generate_mindmap_button.click(
        fn=generate_mermaid_mindmap,
        inputs=full_doc_text,
        outputs=output_mindmap
    )
        

    # # **Mind Map Generation**
    # with gr.Row():
    #     generate_mindmap_button = gr.Button("Generate Mind Map")
    #     output_mindmap = gr.Image(label="Mind Map")
    # Mind Map Generation Section
    # with gr.Row():
    #     generate_mindmap_button = gr.Button("Generate Mind Map")
    #     output_mindmap = gr.HTML(label="Mind Map")

    # Process selected file
    process_button.click(
        fn=process_file, 
        inputs=file_dropdown, 
        outputs=[full_doc_text, output_summary, output_entities, output_wordcloud]
    )

    # # Connect mind map button to function (MOVE THIS INSIDE `with gr.Blocks()`)
    # generate_mindmap_button.click(
    #     fn=generate_mind_map,
    #     inputs=full_doc_text,  # Use the full document text
    #     outputs=output_mindmap
    # )
#     generate_mindmap_button.click(
#     fn=generate_mermaid_mindmap,
#     inputs=full_doc_text,
#     outputs=output_mindmap
# )
# Launch Gradio app
if __name__ == "__main__":
    iface.launch(server_name="0.0.0.0", server_port=7860, share=False, debug=True)
