# tools/aircraft.py
import math
import pygame
from pygame.math import Vector2

class Aircraft:
    def __init__(self, callsign, aircraft_type, position=(0, 0), heading=0, speed=0, size=(50, 50)):
        self.callsign = callsign          # Identyfikator samolotu (np. "KLM4805")
        self.aircraft_type = aircraft_type # Typ samolotu (np. "Boeing 747-200")
        self.position = Vector2(position)  # Pozycja (x, y) na mapie jako wektor
        self.heading = heading            # Kierunek w stopniach (0-359)
        self.speed = speed                # Prędkość w węzłach
        self.altitude = 0                 # Wysokość w stopach
        self.fuel = 100                   # Poziom paliwa w procentach
        self.size = size                  # Rozmiar samolotu na ekranie (szerokość, wysokość)
        self.status = "parked"            # Status: "parked", "taxiing", "takeoff", "landing", "airborne", "crashed"
        self.color = (255, 255, 255)      # Domyślny kolor do rysowania
        self.commands = []                # Lista komend do wykonania (np. zmiana kierunku, prędkości)
        self.flight_data = []             # Historia pozycji dla celów śledzenia trasy
        
    def move(self, delta_time):
        """Przesunięcie samolotu w oparciu o jego prędkość, kierunek i upływ czasu (w sekundach)"""
        if self.status == "crashed":
            return
            
        # Przeliczenie prędkości z węzłów na piksele/s dla symulacji
        # 1 węzeł = ok. 0.514 m/s, skalowanie do przestrzeni symulacji
        speed_factor = self.speed * 0.1  # To będzie wymagało dostosowania do skali mapy
        
        # Obliczenie nowej pozycji w oparciu o kierunek
        rad = math.radians(self.heading)
        dx = math.sin(rad) * speed_factor * delta_time
        dy = -math.cos(rad) * speed_factor * delta_time  # Odwrócone dla Pygame (y rośnie w dół)
        
        new_position = self.position + Vector2(dx, dy)
        self.position = new_position
        
        # Zapisanie danych lotu do historii (co sekunda)
        if len(self.flight_data) == 0 or (len(self.flight_data) > 0 and self.flight_data[-1][0] + 1 < pygame.time.get_ticks() / 1000):
            self.flight_data.append((pygame.time.get_ticks() / 1000, (self.position.x, self.position.y), self.heading, self.speed, self.status))
    
    def set_course(self, new_heading):
        """Zmiana kursu samolotu"""
        self.heading = new_heading % 360
    
    def change_speed(self, new_speed):
        """Zmiana prędkości samolotu"""
        self.speed = max(0, new_speed)
    
    def change_status(self, new_status):
        """Zmiana statusu samolotu"""
        valid_statuses = ["parked", "taxiing", "takeoff", "landing", "airborne", "crashed"]
        if new_status in valid_statuses:
            self.status = new_status
    
    def add_command(self, command_type, value, execution_time=None):
        """
        Dodanie komendy do kolejki wykonania
        command_type: "heading", "speed", "status", "altitude"
        value: nowa wartość
        execution_time: czas wykonania (None = natychmiast)
        """
        self.commands.append({
            "type": command_type,
            "value": value,
            "execution_time": execution_time,
            "completed": False
        })
    
    def process_commands(self, current_time):
        """Przetwarzanie kolejki komend samolotu"""
        for cmd in self.commands:
            if cmd["completed"]:
                continue
                
            # Sprawdzenie czy komenda powinna być wykonana
            if cmd["execution_time"] is None or current_time >= cmd["execution_time"]:
                if cmd["type"] == "heading":
                    self.set_course(cmd["value"])
                elif cmd["type"] == "speed":
                    self.change_speed(cmd["value"])
                elif cmd["type"] == "status":
                    self.change_status(cmd["value"])
                elif cmd["type"] == "altitude":
                    self.altitude = cmd["value"]
                
                cmd["completed"] = True
    
    def draw(self, surface, camera_offset=(0, 0), debug=False):
        """Rysowanie samolotu na powierzchni Pygame"""
        # Pozycja na ekranie z uwzględnieniem przesunięcia kamery
        screen_pos = (int(self.position.x - camera_offset[0]), int(self.position.y - camera_offset[1]))
        
        # Rysowanie samolotu jako trójkąt wskazujący kierunek lotu
        points = []
        # Przód samolotu
        front_x = screen_pos[0] + math.sin(math.radians(self.heading)) * self.size[0] / 2
        front_y = screen_pos[1] - math.cos(math.radians(self.heading)) * self.size[1] / 2
        points.append((front_x, front_y))
        
        # Lewe skrzydło
        left_x = screen_pos[0] + math.sin(math.radians(self.heading - 140)) * self.size[0] / 2
        left_y = screen_pos[1] - math.cos(math.radians(self.heading - 140)) * self.size[1] / 2
        points.append((left_x, left_y))
        
        # Ogon
        tail_x = screen_pos[0] + math.sin(math.radians(self.heading + 180)) * self.size[0] / 4
        tail_y = screen_pos[1] - math.cos(math.radians(self.heading + 180)) * self.size[1] / 4
        points.append((tail_x, tail_y))
        
        # Prawe skrzydło
        right_x = screen_pos[0] + math.sin(math.radians(self.heading + 140)) * self.size[0] / 2
        right_y = screen_pos[1] - math.cos(math.radians(self.heading + 140)) * self.size[1] / 2
        points.append((right_x, right_y))
        
        # Rysowanie samolotu
        if self.status == "crashed":
            pygame.draw.polygon(surface, (255, 0, 0), points)  # Czerwony dla rozbitego
        else:
            pygame.draw.polygon(surface, self.color, points)
        
        # Rysowanie informacji debugowych
        if debug:
            # Callsign
            font = pygame.font.SysFont(None, 24)
            text = font.render(self.callsign, True, (255, 255, 255))
            surface.blit(text, (screen_pos[0] + 20, screen_pos[1] - 10))
            
            # Status i prędkość
            status_text = font.render(f"{self.status}, {self.speed} kts", True, (200, 200, 200))
            surface.blit(status_text, (screen_pos[0] + 20, screen_pos[1] + 10))
            
            # Ślad lotu
            if len(self.flight_data) > 1:
                points = [(p[1][0] - camera_offset[0], p[1][1] - camera_offset[1]) for p in self.flight_data[-100:]]
                pygame.draw.lines(surface, (100, 100, 100), False, points, 1)
