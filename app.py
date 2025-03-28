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

def wrap_label(label, max_length=20):
    """Wrap a label into multiple lines if it exceeds max_length characters."""
    words = label.split()
    lines = []
    current_line = []
    current_length = 0
    for word in words:
        if current_length + len(word) <= max_length:
            current_line.append(word)
            current_length += len(word) + 1
        else:
            lines.append(" ".join(current_line))
            current_line = [word]
            current_length = len(word) + 1
    if current_line:
        lines.append(" ".join(current_line))
    return "\\n".join(lines)

def generate_mermaid_mindmap(text):
    entities = extract_entities(text)
    print("Extracted Entities:", entities)
    
    # Create a directed graph with size attributes
    G = pgv.AGraph(directed=True, rankdir="TB", bgcolor="white")
    
    # Set graph attributes to control the size of the output image
    G.graph_attr['size'] = "30,20"  # Width=30 inches, Height=20 inches
    G.graph_attr['dpi'] = "150"     # DPI for higher resolution (default is 96)
    G.graph_attr['ratio'] = "fill"  # Ensure the graph fills the specified size
    G.graph_attr['pad'] = "0.5"     # Add padding around the graph (in inches)
    G.graph_attr['ranksep'] = "5.0"  # Increase vertical spacing between ranks (in inches)
    G.graph_attr['nodesep'] = "2.0"  # Increase horizontal spacing between nodes (in inches)
    
    # Set default node and edge attributes for better readability
    G.node_attr['fontsize'] = "24"  # Increase font size for node labels
    G.node_attr['width'] = "4.0"    # Increase node width (in inches)
    G.node_attr['height'] = "2.0"   # Increase node height (in inches)
    G.edge_attr['arrowsize'] = "2.5"  # Increase arrow size for edges
    
    # Add root node
    G.add_node("Document", shape="ellipse", style="filled", fillcolor="lightblue", label=wrap_label("Document"))
    
    # Keep track of node names to ensure uniqueness
    node_counter = {}
    
    for category, values in entities.items():
        # Sanitize category name for the node identifier
        safe_category = re.sub(r'[^a-zA-Z0-9_]', '', category)
        if not safe_category or safe_category.startswith('.'):
            safe_category = "Category_" + str(hash(category) % 10000)
        
        # Add category node
        G.add_node(safe_category, shape="box", style="filled", fillcolor="lightgreen", label=wrap_label(category))
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
            G.add_node(safe_value, shape="ellipse", style="filled", fillcolor="lightyellow", label=wrap_label(cleaned_value))
            G.add_edge(safe_category, safe_value)
    
    # Ensure the output directory exists
    output_dir = "mindmap_output"
    os.makedirs(output_dir, exist_ok=True)
    
    # Render the graph to a PNG file
    output_path = os.path.join(output_dir, "mindmap.png")
    G.draw(output_path, format="png", prog="dot")  # 'dot' is the layout engine
    
    return output_path
# import networkx as nx
# import matplotlib.pyplot as plt
# import re
# import os

# def generate_mermaid_mindmap(text):
#     entities = extract_entities(text)
#     print("Extracted Entities:", entities)
    
#     # Create a directed graph
#     G = nx.DiGraph()
    
#     # Add root node
#     G.add_node("Document")
    
#     # Keep track of node names to ensure uniqueness
#     node_counter = {}
    
#     for category, values in entities.items():
#         safe_category = re.sub(r'[^a-zA-Z0-9_]', '', category)
#         if not safe_category or safe_category.startswith('.'):
#             safe_category = "Category_" + str(hash(category) % 10000)
#         G.add_node(safe_category)
#         G.add_edge("Document", safe_category)
        
#         for value in values:
#             cleaned_value = value.strip().rstrip(')').lstrip(',')
#             if not cleaned_value:
#                 cleaned_value = "Unknown"
#             if len(cleaned_value) > 50:
#                 cleaned_value = cleaned_value[:47] + "..."
#             safe_value = re.sub(r'[^a-zA-Z0-9_]', '', cleaned_value)
#             if not safe_value:
#                 safe_value = "Value_" + str(hash(cleaned_value) % 10000)
#             node_key = safe_value
#             node_counter[node_key] = node_counter.get(node_key, 0) + 1
#             if node_counter[node_key] > 1:
#                 safe_value = f"{safe_value}_{node_counter[node_key]}"
#             G.add_node(safe_value)
#             G.add_edge(safe_category, safe_value)
    
#     # Create a layout for the graph
#     pos = nx.spring_layout(G)
    
#     # Draw the graph with a larger figure size and higher DPI
#     plt.figure(figsize=(20, 15), dpi=150)  # Increased size to 20x15 inches, DPI to 150
#     node_colors = []
#     for node in G.nodes():
#         if node == "Document":
#             node_colors.append("lightblue")
#         elif node in [safe_category for category in entities.keys() for safe_category in [re.sub(r'[^a-zA-Z0-9_]', '', category)]]:
#             node_colors.append("lightgreen")
#         else:
#             node_colors.append("lightyellow")
    
#     nx.draw(G, pos, with_labels=True, node_color=node_colors, node_size=3000, font_size=12, font_weight="bold", arrows=True)
    
#     # Ensure the output directory exists
#     output_dir = "mindmap_output"
#     os.makedirs(output_dir, exist_ok=True)
    
#     # Save the graph to a PNG file
#     output_path = os.path.join(output_dir, "mindmap.png")
#     plt.savefig(output_path, format="png", bbox_inches="tight")
#     plt.close()
    
#     return output_path
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
        output_mindmap = gr.Image(label="Mind Map", height=600, width=1200)  # Use HTML instead of Textbox

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
