import json
import os
import sys
from datetime import datetime

class ProjectEngine:
    def __init__(self):
        # 1. Detectar la raíz del proyecto de forma absoluta
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.data_path = os.path.join(self.base_dir, '_data', 'project-schedule.json')
        
        self.rate_hh_uf = 0.25  # Tu factor de 0.25 UF por hora
        self.data = self._load()

    def _load(self):
        """Carga el JSON asegurando que la ruta existe."""
        if os.path.exists(self.data_path):
            with open(self.data_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            print(f"AVISO: No se encontró el archivo en {self.data_path}. Creando nuevo.")
            return {"projects": [], "metadata": {}}

    def save(self):
        """Guarda el JSON con los cálculos procesados y actualiza el timestamp."""
        if 'metadata' not in self.data:
            self.data['metadata'] = {}
            
        self.data['metadata']['last_updated'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        os.makedirs(os.path.dirname(self.data_path), exist_ok=True)
        
        with open(self.data_path, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)
        print(f"Archivo guardado exitosamente en: {self.data_path}")

    def add_project(self, name, uf_value, mora_rate):
        """Añade un proyecto y dispara la sincronización automática."""
        try:
            uf_clean = float(str(uf_value).replace(',', '.'))
            mora_clean = float(str(mora_rate).replace(',', '.'))

            new_item = {
                "name": name,
                "status": "Activo",
                "dates": {
                    "contract_start": datetime.now().strftime("%Y-%m-%d"),
                    "contract_end": datetime.now().strftime("%Y-%m-%d") 
                },
                "metrics": {
                    "uf_base": uf_clean,
                    "mora": mora_clean,
                    "total_progress": 0,
                    "total_hh": 0,
                    "total_uf": 0,
                    "days_diff": 0,
                    "status_label": "Iniciado"
                },
                "phases": [] 
            }
            
            self.data['projects'].append(new_item)
            # Al añadir, sincronizamos para calcular fechas iniciales
            self.sync()
            print(f">>> Proyecto '{name}' añadido y sincronizado.")
        except Exception as e:
            print(f"Error al añadir proyecto: {e}")

    def calculate_metrics(self, project):
        """
        EL MOTOR DINÁMICO:
        Desarma el proyecto y recalcula todo basándose en las tareas y fechas.
        """
        try:
            # --- 1. CÁLCULO DE PLAZOS (days_diff) ---
            # Soporta tanto 'contract_start' como 'start' por flexibilidad
            end_date_str = project.get('dates', {}).get('contract_end') or project.get('dates', {}).get('end', '')
            
            if end_date_str:
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
                today = datetime.now()
                # Diferencia real en días
                diff_days = (end_date - today).days
            else:
                diff_days = 0

            total_tasks = 0
            completed_tasks = 0
            total_hh_spent = 0
            sum_phase_progress = 0

            # --- 2. PROCESAMIENTO DE FASES Y TAREAS ---
            phases = project.get('phases', [])
            for phase in phases:
                tasks = phase.get('tasks', [])
                p_total = len(tasks)
                # Solo contamos como terminadas las que dicen exactamente 'completada'
                p_done = len([t for t in tasks if str(t.get('status', '')).lower() == 'completada'])
                
                # Dinamismo de la fase: (Completadas / Total) * 100
                phase_progress = round((p_done / p_total * 100), 1) if p_total > 0 else 0
                phase['progress'] = phase_progress
                
                sum_phase_progress += phase_progress
                total_tasks += p_total
                completed_tasks += p_done
                # Suma todas las HH registradas en la fase
                total_hh_spent += sum(float(t.get('hh_spent', 0)) for t in tasks)

            # --- 3. MÉTRICAS GLOBALES ---
            num_phases = len(phases)
            # El avance global es el promedio del progreso de las fases
            global_progress = round(sum_phase_progress / num_phases, 1) if num_phases > 0 else 0
            
            project['metrics'].update({
                "days_diff": diff_days,
                "total_progress": global_progress,
                "total_hh": total_hh_spent,
                "total_uf": round(total_hh_spent * self.rate_hh_uf, 2),
                "status_label": "Al día" if diff_days >= 0 else "Retrasado"
            })
            
            return project
        except Exception as e:
            print(f"Error procesando proyecto {project.get('name')}: {e}")
            return project

    def sync(self):
        """Recorre todos los proyectos y fuerza el recalculado de métricas."""
        if not self.data.get('projects'):
            print("No hay proyectos para procesar.")
            return

        for i in range(len(self.data['projects'])):
            self.data['projects'][i] = self.calculate_metrics(self.data['projects'][i])
        
        self.save()
        print(">>> Sincronización exitosa: El JSON ahora es dinámico.")

if __name__ == "__main__":
    engine = ProjectEngine()
    
    # Argumentos para la GitHub Action
    if len(sys.argv) == 4:
        engine.add_project(sys.argv[1], sys.argv[2], sys.argv[3])
    elif len(sys.argv) == 2 and sys.argv[1] == "--sync":
        engine.sync()
    else:
        # Por defecto, si se corre sin argumentos, sincroniza para asegurar integridad
        engine.sync()
