import base64

class CoordinatorAgent:
    def __init__(self, retrieval_agent, dialog_agent, claude_agent):
        self.retrieval_agent = retrieval_agent
        self.dialog_agent = dialog_agent
        self.claude_agent = claude_agent
        self.current_flow = None

    def process_question(self, question):
        if self.current_flow == "image_question":
            return self.process_image_question(question)
        else:
            return self.process_pdf_query(question)

    def process_image_question(self, question, image_data=None):
        # Asegúrate de que image_data sea una cadena base64 válida
        relevant_chunks = self.retrieval_agent.get_relevant_chunks(self.dialog_agent.dialog[-1]["content"])
        context = "\n".join(relevant_chunks)
        if isinstance(image_data, str) and image_data:
            self.current_flow = "image_question"
            response = self.claude_agent.get_response_image(question, self.dialog_agent.dialog, context, image_data)
        else:
            response = self.claude_agent.get_response_image(question, self.dialog_agent.dialog, context)
        self.dialog_agent.update_dialog(response, is_assistant=True)
        return response

    def process_pdf_query(self, question):
        self.dialog_agent.update_dialog(question)
        relevant_chunks = self.retrieval_agent.get_relevant_chunks(self.dialog_agent.dialog[-1]["content"])
        context = "\n".join(relevant_chunks)
        response = self.claude_agent.get_response_pdf_ai(context, self.dialog_agent.dialog)
        self.dialog_agent.update_dialog(response, is_assistant=True)
        return response

    def create_question(self): 
        self.dialog_agent.update_dialog("Por favor genera una respuesta por mi")
        question = self.claude_agent.get_question_user_ai(self.dialog_agent.dialog)
        self.dialog_agent.delete_last_dialog()
        return question
