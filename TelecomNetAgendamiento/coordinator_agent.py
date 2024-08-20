import json
from datetime import datetime

class CoordinatorAgent:
    def __init__(self, retrieval_agent, dialog_agent, claude_agent, technician_appointment_agent):
        self.retrieval_agent = retrieval_agent
        self.dialog_agent = dialog_agent
        self.claude_agent = claude_agent
        self.technician_appointment_agent = technician_appointment_agent
        self.current_flow = None

    # def welcome(self): 
    #     self.dialog_agent.update_dialog("Por favor genera una respuesta por mi")
    #     welcome = self.claude_agent.get_question_user_ai(self.dialog_agent.dialog)
    #     self.dialog_agent.delete_last_dialog()
    #     return welcome 

    def create_question(self): 
        self.dialog_agent.update_dialog("Por favor genera una respuesta por mi")
        question = self.claude_agent.get_question_user_ai(self.dialog_agent.dialog)
        self.dialog_agent.delete_last_dialog()
        return question 
        
    def process_question(self, question):
        self.dialog_agent.update_dialog(question)
        
        if self.current_flow == "Gestionar_citas_tecnicas":
            return self.process_technician_appointment()
        
        response = self.claude_agent.get_response_coordinator_ai(self.dialog_agent.dialog)
        if response == "Gestionar citas tecnicas":
            self.current_flow = "Gestionar_citas_tecnicas"
            return self.process_technician_appointment()
        else:
            return self.process_pdf_query()

    def process_pdf_query(self):
        relevant_chunks = self.retrieval_agent.get_relevant_chunks(self.dialog_agent.dialog[-1]["content"])
        context = "\n".join(relevant_chunks)
        response = self.claude_agent.get_response_pdf_ai(context, self.dialog_agent.dialog)
        self.dialog_agent.update_dialog(response, is_assistant=True)
        return response

    def process_technician_appointment(self):
        # Obtener todas las citas para proporcionar contexto
        all_appointments = self.technician_appointment_agent.get_all_appointments()
        citas_context = self.format_appointments_for_context(all_appointments)
        
        response = self.claude_agent.get_response_technician_ai(self.dialog_agent.dialog, citas_context)
        self.dialog_agent.update_dialog(response, is_assistant=True)
        
        try:
            appointment_data = json.loads(response)
            if appointment_data.get('cancelacion') == True:
                self.current_flow = None
                self.dialog_agent.clear_dialog()
                return appointment_data.get('mensaje')
            
            if appointment_data.get('accion') == 'ver_citas':
                citas = self.technician_appointment_agent.get_appointments(appointment_data['rut'])
                return self.format_appointments(citas)
            elif appointment_data.get('accion') == 'reagendar_cita':
                success = self.technician_appointment_agent.reschedule_appointment(
                    appointment_data['id_cita'],
                    appointment_data['nueva_fecha'],
                    appointment_data['nueva_hora']
                )
                if success:
                    self.current_flow = None
                    return "<p>La cita ha sido reagendada exitosamente.</p><p>¿hay algo mas en lo que pueda ayudarlo?</p>"
                else:
                    return "<p>No se pudo reagendar la cita. Por favor, verifique el ID de la cita e intente nuevamente.</p>"
            elif appointment_data.get('accion') == 'ver_disponibilidad':
                slots = self.technician_appointment_agent.available_slots(appointment_data['fecha'])
                return self.format_available_slots(slots)
            else:
                return response
        except json.JSONDecodeError as e:
            return response

    def format_appointments_for_context(self, citas):
        context = "Citas existentes:\n"
        for cita in citas:
            context += f"ID: {cita['ID_Cita']}, RUT: {cita['RUT_Cliente']}, Fecha: {cita['Fecha_Cita']}, Hora: {cita['Hora_Cita']}, Servicio: {cita['Tipo_Servicio']}\n"
        return context

    def format_appointments(self, citas):
        if not citas:
            return "<p>No se encontraron citas programadas para este RUT.</p>"
        
        html = "<h3>Citas programadas:</h3><ol>"
        for cita in citas:
            html += f"<li><strong>ID:</strong> {cita['ID_Cita']}, <strong>Fecha:</strong> {cita['Fecha_Cita'].strftime('%d/%m/%Y')}, <strong>Hora:</strong> {cita['Hora_Cita']}, <strong>Servicio:</strong> {cita['Tipo_Servicio']}</li>"
        html += "</ol>"
        return html

    def format_available_slots(self, slots):
        if not slots:
            return "<p>No hay horarios disponibles para la fecha seleccionada.</p>"
        
        html = "<h3>Horarios disponibles:</h3><ul>"
        for slot in slots:
            html += f"<li>{slot}</li>"
        html += "</ul>"
        return html