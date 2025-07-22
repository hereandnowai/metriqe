import gradio as gr
from vector_store_manager import get_pdf_list,add_to_vector_store, clear_all_data
from qa_chain_builder import get_answer

def setup_gradio_ui():
    """Sets up the launch of gradio web interface"""

    with gr.Blocks(title= "Ask my PDF Invoices", theme=gr.themes.Soft()) as app:
        gr.Markdown("# Ask Questions on PDF Invoices")
    
        with gr.Row():
            with gr.Column(scale =1):
               
               gr.Markdown("### 1. Manage the Documents")
               file_uploader = gr.File(label="Upload PDFs",file_count="multiple",file_types=[".pdf"])
               process_button = gr.Button("Add to Knowldegebase", variant="primary")

               gr.Markdown("### 2. Current Documents")
               pdf_list_dropdown = gr.Dropdown(label="Select PDF to remove", choices=get_pdf_list(), interactive= True)
               remove_button = gr.Button("Remove from Knowldegebase", variant="stop")
               clear_button = gr.Button("Clear all data", variant="stop")

               processing_status = gr.Markdown("Status: Ready for uploading the PDFS")

            with gr.Column(scale = 2):
                gr.Markdown("### 3. Ask a Question")
                question_input = gr.Text(label="Question",placeholder= "eg: what is the total of invocices")
                ask_button = gr.Button("Ask the LLM and Get Answers",variant= "primary")

                gr.Markdown("### 4. Ask a Question")
                answer_output = gr.Markdown("your answer will appear here")
                gr.Markdown("### 5. Sources")
                sources_output = gr.Markdown("source document will appear here")


        app.load(get_pdf_list,outputs=pdf_list_dropdown)

        process_button.click(
            add_to_vector_store,
            inputs=[file_uploader],
            outputs=[processing_status,pdf_list_dropdown]
        )

        ask_button.click(
            get_answer,
            inputs=[question_input],
            outputs=[answer_output,sources_output]
        )

        clear_button.click(
            clear_all_data, 
            inputs=[], 
            outputs=[processing_status, pdf_list_dropdown]
        )
        

    return app


if __name__ =="__main__":
    app = setup_gradio_ui()
    app.launch(share=True, debug = True)     