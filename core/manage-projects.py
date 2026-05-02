import json
import os
from datetime import datetime

class VartoBackend:
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
        """Agrega un proyecto con el contrato de datos acordado."""
        new_project = {
            "id": len(self.data['projects']) + 1,
            "name": name,
            "values": {
                "uf": uf,
                "mora": mora
            },
            "status": "Activo"
        }
        self.data['projects'].append(new_project)
        self.save()
        print(f"✅ Proyecto '{name}' inyectado con éxito.")

# --- BLOQUE DE EJECUCIÓN ---
if __name__ == "__main__":
    app = VartoBackend()
    
    # Vamos a crear tu primer proyecto de prueba
    app.add_project(name="Proyecto Alfa - React Hub", uf=35.5, mora=1.2)
