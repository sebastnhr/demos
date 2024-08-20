import json

class ReservationAgent:
    def __init__(self):
        self.reservations = []

    def save_reservation(self, reservation_data):
        try:
            if isinstance(reservation_data, str):
                reservation = json.loads(reservation_data)
            elif isinstance(reservation_data, dict):
                reservation = reservation_data
            else:
                return False

            self.reservations.append(reservation)
            
            with open('planes.json', 'w') as f:
                json.dump(reservation, f)
            
            return True
        except json.JSONDecodeError:
            return False
        except IOError:
            return False

    def get_reservations(self):
        return self.reservations