import gradio as gr

def setup_gradio_ui():
    with gr.Blocks(theme=gr.themes.Soft(), title="Ask my invoices") as app:
        gr.Markdown("# Ask Question to from PDF Documents")
    
    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("### 1 Manage Documents")
            file_uploader = gr.File(label="Upload PDFs", file_count="multiple", file_types=[".pdf"])
            process_button = gr.Button("Add to knowledge base", variant="primary")

            gr.Markdown("### 2. Current Documents")
            pdf_list_dropdown = gr.Dropdown(label="Select PDF to Remove", choices=get_pdf_list(), interactive=True)


if __name__ == "__main__":
    gradio_app = setup_gradio_ui()
    gradio_app.launch(share=True, debug=True)