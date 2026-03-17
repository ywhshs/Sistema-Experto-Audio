import typing
from typing import Any, Callable, Dict, List, Optional
from dataclasses import dataclass


@dataclass
class Recommendation:
    """Representa una recomendación generada por el sistema experto."""
    category: str  
    details: Dict[str, str]
    confidence: float  

@dataclass
class Rule:
    """Define una regla IF-THEN con su respectiva recomendación y peso."""
    name: str
  
    condition: Callable[[Dict[str, Any]], bool]
    recommendation: Recommendation



class KnowledgeBase:
    """Almacena el conjunto de reglas del dominio de ingeniería de audio."""
    
    def __init__(self) -> None:
        self.rules: List[Rule] = []
        self._initialize_rules()

    def add_rule(self, rule: Rule) -> None:
        self.rules.append(rule)

    def get_rules(self) -> List[Rule]:
        return self.rules

    def _initialize_rules(self) -> None:
        """Carga las reglas predefinidas de mezcla y masterización."""
        
       
        self.add_rule(Rule(
            name="EQ_Voz_Masculina_Boxy",
            condition=lambda facts: facts.get("instrumento") == "voz" and facts.get("problema") == "boxy",
            recommendation=Recommendation(
                category="EQ",
                details={"Frecuencia": "400 Hz", "Acción": "Reducir", "Cantidad": "-3 dB"},
                confidence=0.90
            )
        ))
        self.add_rule(Rule(
            name="EQ_Bombo_Sin_Fuerza",
            condition=lambda facts: facts.get("instrumento") == "bombo" and facts.get("problema") == "sin fuerza",
            recommendation=Recommendation(
                category="EQ",
                details={"Frecuencia": "60-80 Hz", "Acción": "Aumentar", "Cantidad": "+3 dB"},
                confidence=0.95
            )
        ))
        self.add_rule(Rule(
            name="EQ_Mezcla_Opaca",
            condition=lambda facts: facts.get("problema") == "mezcla opaca",
            recommendation=Recommendation(
                category="EQ",
                details={"Frecuencia": "8-12 kHz", "Acción": "Aumentar", "Cantidad": "+2.5 dB (Shelf)"},
                confidence=0.85
            )
        ))

        self.add_rule(Rule(
            name="Comp_BPM_Alto",
            condition=lambda facts: isinstance(facts.get("bpm"), (int, float)) and facts.get("bpm") > 130,
            recommendation=Recommendation(
                category="Compresion",
                details={"Attack": "Rápido (1-5 ms)", "Release": "Rápido (10-50 ms)", "Ratio": "4:1"},
                confidence=0.95
            )
        ))
        self.add_rule(Rule(
            name="Comp_BPM_Medio",
            condition=lambda facts: isinstance(facts.get("bpm"), (int, float)) and 100 <= facts.get("bpm") <= 130,
            recommendation=Recommendation(
                category="Compresion",
                details={"Attack": "Medio (10-30 ms)", "Release": "Medio (100-300 ms)", "Ratio": "3:1"},
                confidence=0.85
            )
        ))
        self.add_rule(Rule(
            name="Comp_BPM_Bajo",
            condition=lambda facts: isinstance(facts.get("bpm"), (int, float)) and facts.get("bpm") < 100,
            recommendation=Recommendation(
                category="Compresion",
                details={"Attack": "Lento (30+ ms)", "Release": "Medio-Lento (300+ ms)", "Ratio": "2:1"},
                confidence=0.90
            )
        ))

        self.add_rule(Rule(
            name="Reverb_Espacio_Pequeño",
            condition=lambda facts: facts.get("espacio") == "pequeño",
            recommendation=Recommendation(
                category="Reverb",
                details={"Tipo": "Room Reverb", "Tamaño del espacio": "Pequeño (Decay < 1.0s)"},
                confidence=0.90
            )
        ))
        self.add_rule(Rule(
            name="Reverb_Espacio_Medio",
            condition=lambda facts: facts.get("espacio") == "medio",
            recommendation=Recommendation(
                category="Reverb",
                details={"Tipo": "Plate Reverb", "Tamaño del espacio": "Medio (Decay 1.2s - 2.0s)"},
                confidence=0.90
            )
        ))
        self.add_rule(Rule(
            name="Reverb_Espacio_Grande",
            condition=lambda facts: facts.get("espacio") == "grande",
            recommendation=Recommendation(
                category="Reverb",
                details={"Tipo": "Hall Reverb", "Tamaño del espacio": "Grande (Decay > 2.5s)"},
                confidence=0.95
            )
        ))



class InferenceEngine:
    """Evalúa los hechos provistos por el usuario contra la base de conocimiento."""
    
    def __init__(self, knowledge_base: KnowledgeBase) -> None:
        self.kb = knowledge_base

    def infer(self, facts: Dict[str, Any]) -> List[Recommendation]:
        """
        Ejecuta el razonamiento hacia adelante (Forward Chaining).
        Retorna la mejor recomendación por cada categoría.
        """
        triggered_recs: List[Recommendation] = []
        
        for rule in self.kb.get_rules():
            try:
                if rule.condition(facts):
                    triggered_recs.append(rule.recommendation)
            except Exception as e:
                continue

        best_recs: Dict[str, Recommendation] = {}
        for rec in triggered_recs:
            if rec.category not in best_recs or rec.confidence > best_recs[rec.category].confidence:
                best_recs[rec.category] = rec

        return list(best_recs.values())



class VirtualAudioEngineer:
    """Controlador principal que orquesta el sistema experto y maneja la I/O."""
    
    def __init__(self) -> None:
        self.kb = KnowledgeBase()
        self.engine = InferenceEngine(self.kb)

    def format_output(self, recommendations: List[Recommendation]) -> str:
        """Formatea las recomendaciones según los requisitos del sistema."""
        if not recommendations:
            return "\nNo se encontraron recomendaciones con un nivel de certeza suficiente para estos parámetros."

        output = "\n=== Recomendaciones de Mezcla ===\n"
        
        for rec in recommendations:
            if rec.category == "EQ":
                output += "\nEQ:\n"
                for key, value in rec.details.items():
                    output += f"- {key}: {value}\n"
            
            elif rec.category == "Compresion":
                output += "\nCompresión:\n"
                output += f"- Attack recomendado: {rec.details.get('Attack')}\n"
                output += f"- Release recomendado: {rec.details.get('Release')}\n"
                output += f"- Ratio sugerido: {rec.details.get('Ratio')}\n"
            
            elif rec.category == "Reverb":
                output += "\nReverb:\n"
                output += f"- Tipo: {rec.details.get('Tipo')}\n"
                output += f"- Tamaño del espacio: {rec.details.get('Tamaño del espacio')}\n"
                
        return output

    def run_cli(self) -> None:
        """Inicia la interfaz de línea de comandos interactiva."""
        print("🎙️ Bienvenido al Ingeniero de Audio Virtual 🎙️")
        print("Por favor, ingresa los detalles de tu mezcla:\n")
        
        facts: Dict[str, Any] = {}
        facts["genero"] = input("1. Género musical: ").strip().lower()
        facts["instrumento"] = input("2. Instrumento o elemento (ej. bombo, voz): ").strip().lower()
        facts["problema"] = input("3. Problema detectado (ej. sin fuerza, boxy, mezcla opaca): ").strip().lower()
        
        try:
            facts["bpm"] = float(input("4. BPM de la canción: ").strip())
        except ValueError:
            print("[Error] El BPM debe ser un número. Se asumirá 120 por defecto.")
            facts["bpm"] = 120.0
            
        facts["espacio"] = input("5. Tipo de espacio deseado (pequeño, medio, grande): ").strip().lower()

        recommendations = self.engine.infer(facts)
        print(self.format_output(recommendations))

    def run_demo(self) -> None:
        """Ejecuta una prueba hardcodeada para demostración."""
        print("🎧 Ejecutando simulación de datos de prueba...")
        demo_facts = {
            "genero": "trance",
            "instrumento": "bombo",
            "problema": "sin fuerza",
            "bpm": 138.0,
            "espacio": "grande"
        }
        
        print(f"Datos de entrada: {demo_facts}")
        recommendations = self.engine.infer(demo_facts)
        print(self.format_output(recommendations))

if __name__ == "__main__":
    system = VirtualAudioEngineer()
    
    system.run_cli()
   ## system.run_demo()
