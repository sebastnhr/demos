from flask import Flask
import anthropic
from dotenv import load_dotenv
import os
from ui_agent import UIAgent
from coordinator_agent import CoordinatorAgent
from retrieval_agent import RetrievalAgent
from dialog_agent import DialogAgent
from claude_agent import ClaudeAgent
from pdf_processing_agent import PDFProcessingAgent
from technician_appointment_agent import TechnicianAppointmentAgent


class MultiAgentSystem:
    def __init__(self):
        load_dotenv()
        api_key = os.getenv('ANTHROPIC_API_KEY')
        client = anthropic.Anthropic(api_key=api_key)
        
        template_dir = os.path.abspath(os.path.dirname(__file__))
        template_dir = os.path.join(template_dir, 'templates')
        self.app = Flask(__name__, template_folder=template_dir)  # Cambiamos app por self.app
        
        self.pdf_agent = PDFProcessingAgent()
        self.retrieval_agent = None
        self.dialog_agent = DialogAgent()
        self.claude_agent = ClaudeAgent(client)
        self.technician_appointment_agent = TechnicianAppointmentAgent("./TelecomNetAgendamiento/data/citas_agendadas.xlsx")
        self.coordinator_agent = CoordinatorAgent(self.retrieval_agent, self.dialog_agent, self.claude_agent, self.technician_appointment_agent)
        self.ui_agent = UIAgent(self.app)  # Pasamos self.app en lugar de app
        
        self.app.agent_coordinator = self.coordinator_agent

    def initialize(self):
        pdf_paths = [
            "./TelecomNetAgendamiento/pdf/Reglamento-de-servicios-de-Telecomunicaciones.pdf"
        ]
        all_text = self.pdf_agent.read_multiple_pdfs(pdf_paths)
        chunks = self.pdf_agent.split_text(all_text)
        vectorizer, tfidf_matrix = self.pdf_agent.create_index(chunks)
        self.retrieval_agent = RetrievalAgent(vectorizer, tfidf_matrix, chunks)
        self.coordinator_agent.retrieval_agent = self.retrieval_agent

    def run(self):
        self.ui_agent.run()