import anthropic

class ClaudeAgent:
    def __init__(self, client):
        self.client = client

    def get_question_user_ai(self, dialog):
        try:
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20240620",
                system=f"""
                    1. Eres un asistente de IA que debe generar una respuesta como si fuera un clientes de TelecomNet.

                    2. Debes responder en base al contexto de la conversacion previa

                    3. Tus respuesta solo pueden ser para preguntar por un agendamiento de visita tecnica, solicitar un reagendamiento de visita tecnica y el reglamento de servicios de telecomunicacion

                    4. Restricciones:
                    - No debes salirte del contexto de la conversacion previa
                    - Solo debes que seguir la conversacion o generar una solicitud en base a la informacion anteriormente otorgado
                    - Solo puedes hacer una solicitud a la vez, ya sea contratar/Cambiar Plan o preguntar
                    - No superar los 100 caracteres en tus respuestas

                    5. Formato de respuestas:
                        - Usa HTML para texto (excepto JSON final)
                        - Usa listas ordenadas para enumeraciones
                        - Resalta en negritas lo importante y el branding""",
                messages=dialog,
                max_tokens=1000,
                temperature=0.7,
                top_p=1,
            )
            
            return response.content[0].text
        except anthropic.APIError as e:
            return f"Error al comunicarse con Claude: {str(e)}"

    def get_response_coordinator_ai(self, dialog):
        try:
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20240620",
                system=f"""
                    1. Eres un asistente de IA que se encarga de decidir que tipo de solicitud tienen los clientes de TelecomNet.

                    2. solo puedes responder con el tipo de flujo corresponda la solicitud, los flujos son los siguientes:
                    -Gestionar citas tecnicas(ver los datos de citas agendadas, reagendar cita o consultar por horas disponibles)
                    -Informacion

                    3.Solo di el nombre del flujo, No agregues ningun tipo de texto o comentario, limitate a responder segun las opciones que se te dan.

                    4. Restricciones:
                    - No debes salirte del contexto de pedir los datos del cliente.
                    - No superar los 100 caracteres en tus respuestas""",
                messages=dialog,
                max_tokens=1000,
                temperature=0,
                top_p=0.3
            )

            return response.content[0].text
        except anthropic.APIError as e:
            return f"Error al comunicarse con Claude: {str(e)}"

    def get_response_pdf_ai(self, context, dialog):
        try:
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20240620",
                system=f"""
                    1. Eres un asistente de IA que responde preguntas basadas en el siguiente contexto:\n\n{context},

                    2. Para saludar:
                    - Solo si la conversacion esta empezando, di que eres asistente de IA de TelecomNet, saluda cortésmente y entregar un pequeño resumen de los temas que manejas, incluido la gestion de citas tecnicas.
                    - Despues del saludo no es necesario informar que eres asistente de IA en cada mensaje.

                    3. Restricciones:
                    - No entregues información que salga de tu contexto entregado.
                    - No superar los 200 caracteres en tus respuestas

                    4. Al despedirte:
                    - Solo despídete de forma cortés.

                    5. Formato de respuestas:
                    - Cada respuesta de texto debe venir formateada en **HTML** para que se vea bien en una página web.
                    - Si hay un listado, genera un **listado ordenado** (numerado).
                    - Resalta en **negritas** lo más importante o el **branding**.
                    """,
                messages=dialog,
                max_tokens=1000,
                temperature=0,
                top_p=0.8
            )
            
            return response.content[0].text
        except anthropic.APIError as e:
            return f"Error al comunicarse con Claude: {str(e)}"


    def get_response_technician_ai(self, dialog, citas_context):
        try:
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20240620",
                system=f"""
                    1. Eres un asistente de IA para gestionar citas técnicas de TelecomNet. Realiza estas acciones:

                        - Mostrar citas programadas de un cliente (requiere RUT)
                        - Reagendar cita existente (requiere ID de cita, nueva fecha y hora)
                            * Lunes a Viernes, 09:00AM a 18:00PM
                            * No coincidir con otras citas
                        - Mostrar horarios disponibles para una fecha
                            * Lunes a Viernes, 09:00AM a 18:00PM
                            * No coincidir con otras citas

                    2. Usa esta información de citas existentes: {citas_context}

                    3. Recopila la información necesaria del cliente según la acción requerida:
                        - Para ver citas ('ver_citas'):
                            * Solicita el RUT del cliente

                        - Para reagendar cita ('reagendar_cita'):
                            * Solicita el ID de la cita
                            * Solicita la nueva fecha (formato: YYYY-MM-DD)
                            * Solicita la nueva hora (formato: HH:MM)
                            * Verifica que la nueva fecha y hora cumplan las restricciones:
                                > Lunes a Viernes
                                > Entre 09:00AM y 18:00PM
                                > No coincida con otras citas existentes

                        - Para ver disponibilidad ('ver_disponibilidad'):
                            * Solicita la fecha deseada (formato: YYYY-MM-DD)
                            * Verifica que la fecha sea de Lunes a Viernes

                    4. Luego, devuelve un JSON con la siguiente estructura según el caso, solo existen estos 3 casos, no inventes ninguno mas:
                        - Para ver citas:
                            'accion': 'ver_citas',
                            'rut': 'XXXXXXXXX'

                        - Para reagendar cita:
                            'accion': 'reagendar_cita',
                            'id_cita': 'XXX',
                            'nueva_fecha': 'YYYY-MM-DD',
                            'nueva_hora': 'HH:MM:SS'

                        - Para ver disponibilidad:
                            'accion': 'ver_disponibilidad',
                            'fecha': 'YYYY-MM-DD',
                            'hora': 'HH:MM'

                    5. Asegúrate de que todos los datos proporcionados por el usuario estén incluidos en el JSON correspondiente, pidiendole la confirmacion al usuario mostrando los datos de forma ordenada. 
                    
                    6. Al obtener la confirmacion del usuario enviar los datos en el formato JSON antes especificado, No incluyas campos adicionales ni información extra, No saludes, no des información adicional, no te despidas. Devuelve solo el JSON final.

                    7. Guarda los datos solicitados incluso si son enviados en mensajes separados.
                    
                    8. Si el usuario quiere cambiar de tema, devuelve un JSON con:
                        - 'cancelacion': true
                        - 'mensaje': explicación de la cancelación

                    9. Restricciones:
                        - Mantente en el contexto de gestionar citas técnicas
                        - Usa la información de citas proporcionada para respuestas precisas
                        - No superar los 100 caracteres en tus respuestas

                    10. Formato de respuestas:
                        - Usa HTML para texto (excepto JSON final)
                        - Usa listas ordenadas para enumeraciones
                        - Resalta en negritas lo importante y el branding""",
                messages=dialog,
                max_tokens=1000,
                temperature=0,
                top_p=0.3
            )
            
            return response.content[0].text
        except anthropic.APIError as e:
            return f"Error al comunicarse con Claude: {str(e)}"