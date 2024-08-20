import anthropic
import base64
import io
from PIL import Image

class ClaudeAgent:
    def __init__(self, client, dialog_agent):
        self.client = client
        self.dialog_agent = dialog_agent

    def get_question_user_ai(self, dialog):
        try:
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20240620",
                system="""
                1. Eres un asistente de IA simulando preguntas de un técnico en terreno de TelecomNet. Basado en el contexto de la conversación previa, genera preguntas sobre:
                    - Routers y conexiones
                    - Luces LED de dispositivos
                    - Servicios de fibra óptica
                    - Procedimientos técnicos

                2. Restricciones:
                    - No salgas del contexto de la conversación previa.
                    - Solo sigue la conversación o genera solicitudes según la información anterior.
                    - No superes los 100 caracteres por respuesta.

                3. Formato de respuestas:
                    - Formatea en HTML.
                    - Usa listado ordenado para listas.
                    - Resalta en negritas lo importante o el branding.""",
                messages=dialog,
                max_tokens=1000,
                temperature=0.7,
                top_p=1,
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
                        - Solo si la conversacion esta empezando, di que eres asistente de IA de TelecomNet, saluda cortésmente y entregar un pequeño resumen de los temas que manejas.
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

    def get_response_image(self, question, dialog, context, image_data=None):
        try:
            # Asegurarse de que user_question sea una cadena
            message = "Describe esta imagen" if not isinstance(question, str) else question

            if image_data is None:
                self.dialog_agent.update_dialog(message)
            else:
                # Verificar que image_data sea una cadena no vacía
                if not isinstance(image_data, str) or not image_data:
                    raise ValueError("image_data debe ser una cadena base64 no vacía")

                # Decodificar la imagen base64
                try:
                    image_bytes = base64.b64decode(image_data)
                except base64.binascii.Error:
                    raise ValueError("image_data no es una cadena base64 válida")

                # Abrir la imagen con PIL para determinar el formato
                try:
                    with Image.open(io.BytesIO(image_bytes)) as img:
                        format = img.format.lower()
                except IOError:
                    raise ValueError("No se pudo abrir la imagen. El formato puede no ser válido.")

                # Mapear el formato a un media_type
                media_type_map = {
                    'png': 'image/png',
                    'jpeg': 'image/jpeg',
                    'jpg': 'image/jpg'
                }
                media_type = media_type_map.get(format, 'image/jpeg')  # Default a JPEG si no se reconoce

                self.dialog_agent.update_dialog_image(message, media_type, image_data)

            response = self.client.messages.create(
                model="claude-3-5-sonnet-20240620",
                system=f"""
                    1. Eres un asistente de IA especializado en telecomunicaciones que analiza imágenes de routers wifi y entrega posibles soluciones a los problemas que presenten.
                    2. Describir brevemente el problema y una posible solución.
                    3. Puedes usar el siguiente contexto para fundamentar tus respuestas:\n\n{context}.
                    3. Restricciones:
                    - Limítate a describir y responder sobre el contenido de la imagen.
                    - No superes los 300 caracteres en tus respuestas.
                    4. Formato de respuestas:
                    - Usa HTML para formatear el texto.
                    - Usa listas ordenadas para enumeraciones.
                    - Resalta en **negritas** lo más importante. """,
                messages=self.dialog_agent.dialog,
                max_tokens=1000,
                temperature=0.5
            )
            
            return response.content[0].text
        except ValueError as ve:
            return f"Error de validación: {str(ve)}"
        except anthropic.APIError as ae:
            return f"Error de API de Anthropic: {str(ae)}"
        except Exception as e:
            return f"Error inesperado al procesar la imagen: {str(e)}"