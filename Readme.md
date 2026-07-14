# System Engine: Project Management Orchestrator

## Visión General
System Engine es un motor de gestión técnica basado en arquitectura **GitOps**. A diferencia de los sistemas tradicionales que dependen de bases de datos centralizadas, este sistema utiliza el control de versiones como fuente de verdad (*Source of Truth*) y como capa de persistencia documental (JSON).

## Arquitectura del Sistema
El sistema se compone de tres pilares integrados:

1.  **Frontend (UI/UX):** Interfaz desacoplada construida con HTML5/CSS3 y lógica JavaScript que interactúa con la API de GitHub mediante eventos `repository_dispatch`.
2.  **Motor de Lógica (Backend Serverless):** Script en Python (`manage-projects.py`) ejecutado mediante GitHub Actions. Este motor normaliza datos, calcula métricas de progreso (HH, UF, % avance) y garantiza la integridad del esquema JSON.
3.  **Persistencia (Data Layer):** Almacenamiento plano en `_data/project-schedule.json`. Este archivo funciona como una base de datos NoSQL versionada, lo que permite auditoría total de cambios mediante `git log`.

## Flujo de Trabajo (CI/CD)
* **Acción:** El usuario interactúa con el Dashboard.
* **Dispatch:** El evento se envía a GitHub vía API (Autenticado).
* **Orquestación:** El workflow `.github/workflows/add_project.yml` dispara el motor de Python.
* **Sincronización:** El script actualiza el JSON, realiza el commit y hace push al repositorio.
* **Despliegue:** El workflow `deploy.yml` detecta el cambio y reconstruye el sitio mediante Jekyll Pages.

## Seguridad y Gobernanza
* **Acceso:** Limitado estrictamente a tokens con permisos de escritura (PAT).
* **Integridad:** No se exponen endpoints públicos de escritura; el sistema opera bajo una arquitectura de disparadores de eventos.
* **Filosofía:** Este repositorio es un laboratorio de ingeniería pragmática. La lógica de negocio crítica opera bajo entornos privados y NDA. El código expuesto es exclusivamente de experimentación funcional.

## Configuración Técnica
* **Engine:** Python 3.10+
* **Persistence:** JSON (Normalización estricta)
* **Platform:** GitHub Actions / GitHub Pages
* **Frontend:** Vanilla JS, CSS Glassmorphism
