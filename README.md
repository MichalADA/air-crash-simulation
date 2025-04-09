# air-crash-simulation

# ✈️ Air Crash Simulations – Realistic Aircraft Accident Simulations in Python

This project is my personal way of learning Python and data visualization libraries by building realistic simulations of historical air disasters.

## 🎯 Project Goals

The aim is to recreate real-world aviation accidents based on:
- official reports (e.g. NTSB, ICAO),
- cockpit voice recorder (CVR) and ATC transcripts,
- technical data of aircraft and airports,
- analysis of crew decisions and ATC communication.

Each simulation will feature:
- a step-by-step timeline (real-time sequence),
- a visual component (2D rendering),
- potential for "what-if" alternative scenarios and experiments.

## 🧱 Project Structure

Each crash is organized in a dedicated module/folder containing:
- `data.py` – aircraft and airport data,
- `atc_log.txt` – radio communication transcripts,
- `simulation.py` – main simulation runner,
- `map.png` – optional simplified visual layout.

Shared logic (e.g. `Aircraft`, `Airport`, `ATC` classes) is stored in the `tools/` directory.

## 📦 Technologies

- Python 3.x
- Pygame (for 2D visualization)
- Matplotlib / Plotly (for technical data & charts)
- [Optional] NumPy, VPython, or PyOpenGL

## 🛫 First Case: Tenerife 1977

Simulation of the deadliest accident in civil aviation history, including realistic fog conditions, misunderstood communication, and aircraft movement logic for both the KLM and Pan Am 747s.

## 🔜 Planned Features

- Additional cases (Helios 522, Swissair 111, Concorde, etc.)
- Interactive simulations with decision-making
- Experimental "What if..." mode for alternative scenario testing

## 📚 Status

This is a personal educational project focused on improving my programming skills, deepening my understanding of aviation, and exploring the use of simulations as learning tools.
