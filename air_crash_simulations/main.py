#!/usr/bin/env python3
import os
import sys
import importlib
import argparse




def list_available_simulations():
    """Wypisuje wszystkie dostępne symulacje (foldery, które zawierają simulation.py)"""
    simulations = []
    for item in os.listdir():
        if os.path.isdir(item) and not item.startswith('_') and not item == 'tools':
            if os.path.exists(os.path.join(item, 'simulation.py')):
                simulations.append(item)
    return simulations

def run_simulation(simulation_name, args=None):
    """Uruchamia konkretną symulację"""
    try:
        # Dynamiczne importowanie modułu symulacji
        simulation_module = importlib.import_module(f"{simulation_name}.simulation")
        
        # Uruchomienie symulacji
        if hasattr(simulation_module, 'run_simulation'):
            simulation_module.run_simulation(args)
        else:
            print(f"Błąd: Moduł {simulation_name} nie zawiera funkcji run_simulation()")
    except ImportError:
        print(f"Błąd: Nie można zaimportować modułu symulacji {simulation_name}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description='Air Crash Simulation Runner')
    available_simulations = list_available_simulations()
    
    parser.add_argument('--list', action='store_true', 
                        help='Wypisuje wszystkie dostępne symulacje')
    parser.add_argument('--simulation', type=str, choices=available_simulations,
                        help='Nazwa symulacji do uruchomienia')
    parser.add_argument('--headless', action='store_true',
                        help='Uruchamia symulację bez interfejsu graficznego')
    
    args = parser.parse_args()
    
    if args.list:
        print("Dostępne symulacje:")
        for sim in available_simulations:
            print(f"  - {sim}")
        return
    
    if not args.simulation:
        if len(available_simulations) == 0:
            print("Nie znaleziono żadnych symulacji. Utwórz folder z plikiem simulation.py.")
            return
        
        # Proste menu konsolowe, jeśli nie podano symulacji jako argument
        print("Wybierz symulację do uruchomienia:")
        for i, sim in enumerate(available_simulations, 1):
            print(f"{i}. {sim}")
        
        choice = input("Wybór (numer): ")
        try:
            choice_idx = int(choice) - 1
            if 0 <= choice_idx < len(available_simulations):
                selected_simulation = available_simulations[choice_idx]
            else:
                print("Nieprawidłowy wybór.")
                return
        except ValueError:
            print("Wprowadź liczbę.")
            return
    else:
        selected_simulation = args.simulation
    
    print(f"Uruchamianie symulacji: {selected_simulation}")
    run_simulation(selected_simulation, args)

if __name__ == "__main__":
    main()