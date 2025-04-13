# tools/airport.py
import pygame
from pygame.math import Vector2
import math
import json

class Airport:
    def __init__(self, name, code, location=(0, 0), runways=None, taxiways=None, gates=None):
        self.name = name              # Pełna nazwa lotniska (np. "Los Rodeos Airport")
        self.code = code              # Kod ICAO lotniska (np. "GCXO")
        self.location = Vector2(location)  # Pozycja lotniska na mapie świata
        self.runways = runways or []  # Lista pasów startowych
        self.taxiways = taxiways or [] # Lista dróg kołowania
        self.gates = gates or []      # Lista stanowisk postojowych (gate'ów)
        self.buildings = []           # Lista budynków lotniska (terminal, wieża, hangary)
        self.weather = {              # Warunki pogodowe
            "visibility": 10000,      # Widoczność w metrach
            "fog_density": 0,         # Gęstość mgły (0-1)
            "wind_direction": 0,      # Kierunek wiatru w stopniach
            "wind_speed": 0,          # Prędkość wiatru w węzłach
            "precipitation": None,    # Typ opadów (None, "rain", "snow")
        }
        self.scale = 1.0              # Skala wizualizacji (piksele/metr)
        self.background_image = None  # Opcjonalny obraz tła lotniska
        
    def add_runway(self, name, start_pos, end_pos, width=45, active=True):
        """Dodaje pas startowy do lotniska"""
        runway = {
            "name": name,                     # Oznaczenie pasa (np. "09/27")
            "start_pos": Vector2(start_pos),  # Początek pasa
            "end_pos": Vector2(end_pos),      # Koniec pasa
            "width": width,                   # Szerokość pasa w metrach
            "active": active,                 # Czy pas jest aktywny
            "length": Vector2(start_pos).distance_to(Vector2(end_pos)), # Długość pasa
            "heading": self._calculate_heading(start_pos, end_pos), # Kierunek pasa
        }
        self.runways.append(runway)
        return runway
    
    def add_taxiway(self, name, points, width=15):
        """Dodaje drogę kołowania do lotniska"""
        # Konwersja wszystkich punktów na wektory
        vector_points = [Vector2(p) for p in points]
        
        taxiway = {
            "name": name,
            "points": vector_points,
            "width": width
        }
        self.taxiways.append(taxiway)
        return taxiway
    
    def add_gate(self, name, position, heading=0, size=1):
        """Dodaje stanowisko postojowe (gate) do lotniska"""
        gate = {
            "name": name,
            "position": Vector2(position),
            "heading": heading,  # Kierunek ustawienia samolotu na gate'ie
            "size": size,        # Rozmiar gate'u (mały=1, średni=2, duży=3)
            "occupied": False    # Czy gate jest zajęty
        }
        self.gates.append(gate)
        return gate
    
    def add_building(self, name, polygon, height=10, type="terminal"):
        """Dodaje budynek do lotniska (terminal, wieża, hangar itp.)"""
        # Konwersja wszystkich punktów na wektory
        vector_points = [Vector2(p) for p in polygon]
        
        building = {
            "name": name,
            "polygon": vector_points,
            "height": height,
            "type": type
        }
        self.buildings.append(building)
        return building
    
    def set_weather(self, visibility=None, fog_density=None, wind_direction=None, 
                   wind_speed=None, precipitation=None):
        """Ustawia warunki pogodowe na lotnisku"""
        if visibility is not None:
            self.weather["visibility"] = visibility
        if fog_density is not None:
            self.weather["fog_density"] = max(0, min(1, fog_density))  # Ograniczenie do 0-1
        if wind_direction is not None:
            self.weather["wind_direction"] = wind_direction % 360  # Ograniczenie do 0-359
        if wind_speed is not None:
            self.weather["wind_speed"] = max(0, wind_speed)
        if precipitation is not None:
            self.weather["precipitation"] = precipitation
    
    def get_runway_by_name(self, name):
        """Zwraca pas startowy o podanej nazwie"""
        for runway in self.runways:
            if runway["name"] == name:
                return runway
        return None
    
    def get_taxiway_by_name(self, name):
        """Zwraca drogę kołowania o podanej nazwie"""
        for taxiway in self.taxiways:
            if taxiway["name"] == name:
                return taxiway
        return None
    
    def get_gate_by_name(self, name):
        """Zwraca gate o podanej nazwie"""
        for gate in self.gates:
            if gate["name"] == name:
                return gate
        return None
    
    def get_active_runways(self, wind_direction=None):
        """Zwraca aktywne pasy startowe, optymalne dla podanego kierunku wiatru"""
        if wind_direction is None:
            wind_direction = self.weather["wind_direction"]
            
        active_runways = []
        for runway in self.runways:
            if runway["active"]:
                # Wybór kierunku pasa najbardziej zgodnego z kierunkiem wiatru
                heading = runway["heading"]
                reverse_heading = (heading + 180) % 360
                
                # Obliczenie różnicy kątów między pasem a wiatrem
                diff1 = abs((heading - wind_direction + 180) % 360 - 180)
                diff2 = abs((reverse_heading - wind_direction + 180) % 360 - 180)
                
                # Wybór lepszego kierunku (mniejsza różnica = lepszy)
                if diff1 <= diff2:
                    active_runways.append({
                        "runway": runway,
                        "direction": "normal",
                        "heading": heading,
                        "difference": diff1
                    })
                else:
                    active_runways.append({
                        "runway": runway,
                        "direction": "reverse",
                        "heading": reverse_heading,
                        "difference": diff2
                    })
        
        # Sortowanie pasów wg najmniejszej różnicy do kierunku wiatru
        active_runways.sort(key=lambda x: x["difference"])
        return active_runways
    
    def load_from_file(self, filename):
        """Ładuje dane lotniska z pliku JSON"""
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
            
            # Aktualizacja podstawowych informacji
            self.name = data.get("name", self.name)
            self.code = data.get("code", self.code)
            self.location = Vector2(data.get("location", (0, 0)))
            
            # Ładowanie pasów startowych
            self.runways = []
            for runway_data in data.get("runways", []):
                start_pos = Vector2(runway_data["start_pos"])
                end_pos = Vector2(runway_data["end_pos"])
                self.add_runway(
                    runway_data["name"], 
                    start_pos, 
                    end_pos, 
                    runway_data.get("width", 45),
                    runway_data.get("active", True)
                )
            
            # Ładowanie dróg kołowania
            self.taxiways = []
            for taxiway_data in data.get("taxiways", []):
                points = [Vector2(p) for p in taxiway_data["points"]]
                self.add_taxiway(
                    taxiway_data["name"],
                    points,
                    taxiway_data.get("width", 15)
                )
            
            # Ładowanie gate'ów
            self.gates = []
            for gate_data in data.get("gates", []):
                self.add_gate(
                    gate_data["name"],
                    gate_data["position"],
                    gate_data.get("heading", 0),
                    gate_data.get("size", 1)
                )
            
            # Ładowanie budynków
            self.buildings = []
            for building_data in data.get("buildings", []):
                self.add_building(
                    building_data["name"],
                    building_data["polygon"],
                    building_data.get("height", 10),
                    building_data.get("type", "terminal")
                )
            
            # Ładowanie pogody
            if "weather" in data:
                self.set_weather(**data["weather"])
            
            return True
        except Exception as e:
            print(f"Błąd podczas ładowania lotniska z pliku: {e}")
            return False
    
    def save_to_file(self, filename):
        """Zapisuje dane lotniska do pliku JSON"""
        data = {
            "name": self.name,
            "code": self.code,
            "location": (self.location.x, self.location.y),
            "runways": [],
            "taxiways": [],
            "gates": [],
            "buildings": [],
            "weather": self.weather
        }
        
        # Zapisywanie pasów startowych
        for runway in self.runways:
            data["runways"].append({
                "name": runway["name"],
                "start_pos": (runway["start_pos"].x, runway["start_pos"].y),
                "end_pos": (runway["end_pos"].x, runway["end_pos"].y),
                "width": runway["width"],
                "active": runway["active"]
            })
        
        # Zapisywanie dróg kołowania
        for taxiway in self.taxiways:
            data["taxiways"].append({
                "name": taxiway["name"],
                "points": [(p.x, p.y) for p in taxiway["points"]],
                "width": taxiway["width"]
            })
        
        # Zapisywanie gate'ów
        for gate in self.gates:
            data["gates"].append({
                "name": gate["name"],
                "position": (gate["position"].x, gate["position"].y),
                "heading": gate["heading"],
                "size": gate["size"],
                "occupied": gate["occupied"]
            })
        
        # Zapisywanie budynków
        for building in self.buildings:
            data["buildings"].append({
                "name": building["name"],
                "polygon": [(p.x, p.y) for p in building["polygon"]],
                "height": building["height"],
                "type": building["type"]
            })
        
        try:
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            print(f"Błąd podczas zapisywania lotniska do pliku: {e}")
            return False
    
    def draw(self, surface, camera_offset=(0, 0), debug=False, fog=False):
        """Rysuje lotnisko na powierzchni Pygame"""
        # Zastosowanie skali i przesunięcia kamery
        scale = self.scale
        offset_x, offset_y = camera_offset
        
        # Rysowanie mgły jeśli wymagane
        if fog and self.weather["fog_density"] > 0:
            fog_surface = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
            fog_alpha = int(self.weather["fog_density"] * 200)  # Maksymalne zaciemnienie 200/255
            fog_surface.fill((200, 200, 200, fog_alpha))
            surface.blit(fog_surface, (0, 0))
        
        # Rysowanie pasów startowych
        for runway in self.runways:
            start_pos = (runway["start_pos"].x * scale - offset_x, 
                         runway["start_pos"].y * scale - offset_y)
            end_pos = (runway["end_pos"].x * scale - offset_x, 
                       runway["end_pos"].y * scale - offset_y)
            
            # Rysowanie pasa jako pogrubionych linii
            width = int(runway["width"] * scale)
            pygame.draw.line(surface, (80, 80, 80), start_pos, end_pos, width)
            
            # Oznaczenia pasa (białe paski)
            direction = Vector2(end_pos) - Vector2(start_pos)
            length = direction.length()
            if length > 0:
                direction.normalize_ip()
                num_markings = max(1, int(length / (30 * scale)))
                marking_spacing = length / (num_markings + 1)
                
                for i in range(1, num_markings + 1):
                    pos = Vector2(start_pos) + direction * (i * marking_spacing)
                    marking_length = min(20 * scale, width * 0.75)
                    marking_dir = Vector2(-direction.y, direction.x)  # Prostopadły wektor
                    mark_start = pos - marking_dir * (marking_length / 2)
                    mark_end = pos + marking_dir * (marking_length / 2)
                    pygame.draw.line(surface, (255, 255, 255), mark_start, mark_end, max(1, int(width / 10)))
            
            # Debugowanie - wyświetlanie nazwy pasa
            if debug:
                font = pygame.font.SysFont(None, 24)
                mid_point = ((start_pos[0] + end_pos[0]) / 2, (start_pos[1] + end_pos[1]) / 2)
                text = font.render(runway["name"], True, (255, 255, 255))
                surface.blit(text, mid_point)
        
        # Rysowanie dróg kołowania
        for taxiway in self.taxiways:
            if len(taxiway["points"]) < 2:
                continue
                
            # Konwersja punktów do współrzędnych ekranu
            screen_points = []
            for point in taxiway["points"]:
                screen_point = (point.x * scale - offset_x, point.y * scale - offset_y)
                screen_points.append(screen_point)
            
            # Rysowanie drogi kołowania jako pogrubionej łamanej
            width = int(taxiway["width"] * scale)
            pygame.draw.lines(surface, (50, 50, 50), False, screen_points, width)
            
            # Żółta linia środkowa
            if width > 3:
                pygame.draw.lines(surface, (255, 255, 0), False, screen_points, max(1, int(width / 5)))
            
            # Debugowanie - wyświetlanie nazwy drogi kołowania
            if debug and len(screen_points) > 0:
                font = pygame.font.SysFont(None, 20)
                text = font.render(taxiway["name"], True, (255, 255, 0))
                # Wyświetlenie nazwy przy pierwszym punkcie
                surface.blit(text, screen_points[0])
        
        # Rysowanie gate'ów
        for gate in self.gates:
            pos = (gate["position"].x * scale - offset_x, gate["position"].y * scale - offset_y)
            size = gate["size"] * 10 * scale  # Dostosowanie rozmiaru gate'u
            
            # Rysowanie gate'u jako prostokąt lub koło
            if gate["occupied"]:
                color = (200, 0, 0)  # Czerwony dla zajętego
            else:
                color = (0, 200, 0)  # Zielony dla wolnego
                
            pygame.draw.circle(surface, color, pos, size)
            
            # Strzałka wskazująca kierunek ustawienia samolotu
            arrow_length = size * 1.5
            arrow_end = (pos[0] + math.sin(math.radians(gate["heading"])) * arrow_length,
                         pos[1] - math.cos(math.radians(gate["heading"])) * arrow_length)
            pygame.draw.line(surface, (255, 255, 255), pos, arrow_end, max(1, int(size / 5)))
            
            # Debugowanie - wyświetlanie nazwy gate'u
            if debug:
                font = pygame.font.SysFont(None, 20)
                text = font.render(gate["name"], True, (255, 255, 255))
                text_pos = (pos[0] - text.get_width() / 2, pos[1] - size - text.get_height())
                surface.blit(text, text_pos)
        
        # Rysowanie budynków
        for building in self.buildings:
            # Konwersja punktów do współrzędnych ekranu
            screen_points = []
            for point in building["polygon"]:
                screen_point = (point.x * scale - offset_x, point.y * scale - offset_y)
                screen_points.append(screen_point)
            
            # Wybór koloru w zależności od typu budynku
            if building["type"] == "terminal":
                color = (100, 100, 150)
            elif building["type"] == "tower":
                color = (150, 150, 200)
            elif building["type"] == "hangar":
                color = (100, 130, 100)
            else:
                color = (120, 120, 120)
                
            # Rysowanie budynku jako wypełniony wielokąt
            if len(screen_points) >= 3:
                pygame.draw.polygon(surface, color, screen_points)
                pygame.draw.polygon(surface, (50, 50, 50), screen_points, 2)  # Obrys
            
            # Debugowanie - wyświetlanie nazwy budynku
            if debug and len(screen_points) > 0:
                # Obliczenie środka budynku jako średniej współrzędnych
                center_x = sum(p[0] for p in screen_points) / len(screen_points)
                center_y = sum(p[1] for p in screen_points) / len(screen_points)
                
                font = pygame.font.SysFont(None, 20)
                text = font.render(building["name"], True, (255, 255, 255))
                text_pos = (center_x - text.get_width() / 2, center_y - text.get_height() / 2)
                surface.blit(text, text_pos)
    
    def _calculate_heading(self, start_pos, end_pos):
        """Oblicza kierunek (heading) na podstawie dwóch punktów"""
        delta_x = end_pos[0] - start_pos[0]
        delta_y = end_pos[1] - start_pos[1]
        angle_rad = math.atan2(delta_x, -delta_y)  # Odwrócone y dla Pygame
        angle_deg = math.degrees(angle_rad)
        return angle_deg % 360