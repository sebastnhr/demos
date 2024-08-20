import json

class CoordinatorAgent:
    def __init__(self, retrieval_agent, dialog_agent, claude_agent):
        self.retrieval_agent = retrieval_agent
        self.dialog_agent = dialog_agent
        self.claude_agent = claude_agent
        self.current_flow = None

    def create_question(self): 
        self.dialog_agent.update_dialog("Por favor genera una respuesta por mi")
        question = self.claude_agent.get_question_user_ai(self.dialog_agent.dialog)
        self.dialog_agent.delete_last_dialog()
        return question 

    def process_question(self, question):
        self.dialog_agent.update_dialog(question)
        
        if self.current_flow == "reservation":
            return self.process_reservation()
        
        response = self.claude_agent.get_response_coordinator_ai(self.dialog_agent.dialog)
        if response == "Reservacion":
            self.current_flow = "reservation"
            return self.process_reservation()
        else:
            return self.process_pdf_query()

    def process_pdf_query(self):
        relevant_chunks = self.retrieval_agent.get_relevant_chunks(str(self.dialog_agent.dialog[-1]["content"]))
        context = "\n".join(relevant_chunks)
        response = self.claude_agent.get_response_pdf_ai(context, self.dialog_agent.dialog)
        self.dialog_agent.update_dialog(response, is_assistant=True)
        return response

    def process_reservation(self):
        response = self.claude_agent.get_response_reservation_ai(self.dialog_agent.dialog)
        self.dialog_agent.update_dialog(response, is_assistant=True)
        
        try:
            reservation_data = json.loads(response)
            if reservation_data.get('confirmacion') == True:
                if self.claude_agent.reservation_agent.save_reservation(reservation_data):
                    self.current_flow = None  # Resetear el flujo
                    self.dialog_agent.clear_dialog()  # Limpiar el diálogo después de una reservación exitosa
                    return "<p>Su reservación será evaluada. Próximamente le llegará un correo confirmando su vuelo. En caso contrario, un ejecutivo se pondrá en contacto con usted. Muchas gracias por contactar con LATAM Air Lines.</p><br><p>¿Necesita ayuda con algún otro tema?</p>"
                else:
                    return "<p>Lo siento, hubo un problema al procesar su reservación. Por favor, intente nuevamente.</p>"
            elif reservation_data.get('cancelacion') == True:
                self.current_flow = None  # Resetear el flujo
                self.dialog_agent.clear_dialog()  # Limpiar el diálogo después de una reservación exitosa
                
                return reservation_data.get('message')
            else:
                return response
        except json.JSONDecodeError:
            return response