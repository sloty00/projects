import json
import os
import sys
from datetime import datetime

class ProjectEngine:
    """Motor genérico para la gestión de datos de proyectos."""
    
    def __init__(self, data_path='_data/project-schedule.json'):
        self.data_path = data_path
        self.data = self._load()

    def _load(self):
        if os.path.exists(self.data_path):
            with open(self.data_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"projects": [], "metadata": {}}

    def save(self):
        self.data['metadata']['last_updated'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(self.data_path, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)

    def add_project(self, name, uf, mora):
        """Añade una entrada al registro de proyectos."""
        new_project = {
            "id": len(self.data['projects']) + 1,
            "name": name,
            "values": {
                "uf": float(uf),
                "mora": float(mora)
            },
            "timestamp": datetime.now().isoformat()
        }
        self.data['projects'].append(new_project)
        self.save()
        print(f"Registro actualizado: {name}")

if __name__ == "__main__":
    engine = ProjectEngine()
    if len(sys.argv) > 3:
        engine.add_project(sys.argv[1], sys.argv[2], sys.argv[3])
    else:
        print("Uso: python3 manage_projects.py <nombre> <uf> <mora>")
