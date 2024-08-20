import pandas as pd
from datetime import datetime

class TechnicianAppointmentAgent:
    def __init__(self, excel_path):
        self.excel_path = excel_path
        self.df = pd.read_excel(excel_path, parse_dates=['Fecha_Cita'])
        self.df['Hora_Cita'] = pd.to_datetime(self.df['Hora_Cita'], format='%H:%M:%S').dt.time

        


    def get_all_appointments(self):
        return self.df.to_dict('records')

    def get_appointments(self, rut):
        return self.df[self.df['RUT_Cliente'] == rut].to_dict('records')

    def reschedule_appointment(self, appointment_id, new_date, new_time):
        appointment_id = int(appointment_id)
        appointment = self.df[self.df['ID_Cita'] == appointment_id]
        
        if not appointment.empty:
            new_date = pd.to_datetime(new_date).date()
            self.df.loc[self.df['ID_Cita'] == appointment_id, 'Fecha_Cita'] = new_date
            self.df.loc[self.df['ID_Cita'] == appointment_id, 'Hora_Cita'] = new_time
            
            try:
                self.df.to_excel(self.excel_path, index=False)
                print(f"Cita {appointment_id} reagendada exitosamente para {new_date} a las {new_time}")
                return True
            except Exception as e:
                print(f"Error al guardar los cambios: {str(e)}")
                return False
        else:
            print(f"No se encontró la cita con ID {appointment_id}")
            return False


    def available_slots(self, date):
        date = pd.to_datetime(date).date()
        date_appointments = self.df[self.df['Fecha_Cita'].dt.date == date]
        all_hours = pd.date_range("09:00", "18:00", freq="1H").time
        busy_hours = date_appointments['Hora_Cita'].tolist()
        available = [hour.strftime("%H:%M") for hour in all_hours if hour not in busy_hours]
        
        return available