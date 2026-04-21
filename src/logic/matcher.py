import re
import unicodedata
from typing import Dict, Any, List, Set

class ProductMatcher:
    def __init__(self):
        # Marcas conocidas para mejorar la precisión (opcional, el sistema es dinámico)
        self.known_brands = [
            "samsung", "lg", "viewsonic", "asus", "gigabyte", "msi", "corsair", 
            "logitech", "kingston", "wd", "western digital", "crucial", "patriot",
            "team", "razer", "hyperx", "redragon", "arctic", "sentey", "evga"
        ]
        
        # Diccionario de normalización de unidades
        self.unit_map = {
            r'"|pul|pulgadas|in': "pulg",
            r'gramos|gr|g(?!\w)': "g",
            r'hz|hertz': "hz",
            r'watts|w(?!\w)': "w",
            r'terabytes|tb': "tb",
            r'gigabytes|gb': "gb",
            r'megabytes|mb': "mb",
            r'mhz': "mhz",
            r'va|voltios': "v"
        }
        
        self.MATCH_THRESHOLD = 0.85

    def normalize_text(self, text: str) -> str:
        """Sanitización universal de texto."""
        if not text: return ""
        text = text.lower()
        # Quitar tildes
        text = "".join(c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn')
        # Normalizar unidades comunes antes de limpiar símbolos
        for pattern, replacement in self.unit_map.items():
            text = re.sub(pattern, " " + replacement + " ", text)
        
        # Limpiar símbolos, mantener letras y números
        text = re.sub(r'[^a-z0-9\s]', ' ', text)
        return re.sub(r'\s+', ' ', text).strip()

    def extract_specs(self, normalized_name: str) -> Dict[str, str]:
        """
        Extrae cualquier especificación de tipo Número+Unidad.
        Ejemplo: "monitor 24 pulg 144 hz" -> {'pulg': '24', 'hz': '144'}
        """
        specs = {}
        # Busca patrones de: número + (pulg|g|hz|w|tb|gb|mb|mhz|v)
        units = "|".join(set(self.unit_map.values()))
        pattern = rf'(\d+(?:\.\d+)?)\s*({units})'
        
        matches = re.findall(pattern, normalized_name)
        for value, unit in matches:
            specs[unit] = value
        return specs

    def get_similarity_score(self, name1: str, name2: str) -> Dict[str, Any]:
        """
        Calcula la similitud universal entre dos nombres de productos.
        """
        n1 = self.normalize_text(name1)
        n2 = self.normalize_text(name2)
        
        specs1 = self.extract_specs(n1)
        specs2 = self.extract_specs(n2)
        
        # 1. DETECCIÓN DE CONFLICTOS TÉCNICOS (Bloqueo)
        # Si ambos tienen la misma unidad pero distinto valor, no pueden ser iguales.
        for unit in specs1:
            if unit in specs2 and specs1[unit] != specs2[unit]:
                return {"score": 0.0, "is_match": False, "reason": f"Conflicto de {unit}: {specs1[unit]} vs {specs2[unit]}"}

        # 2. COMPARACIÓN DE MARCAS
        brand1 = next((b for b in self.known_brands if b in n1), None)
        brand2 = next((b for b in self.known_brands if b in n2), None)
        
        brand_score = 1.0
        if brand1 and brand2 and brand1 != brand2:
            return {"score": 0.0, "is_match": False, "reason": f"Marcas diferentes: {brand1} vs {brand2}"}

        # 3. SIMILITUD DE TOKENS (Jaccard)
        # Quitamos las unidades de los tokens para comparar solo el "modelo"
        stop_words = {"de", "con", "para", "negro", "black", "white", "blanco", "pulg", "g", "hz", "w", "tb", "gb", "mb"}
        set1 = set([t for t in n1.split() if t not in stop_words and len(t) > 1])
        set2 = set([t for t in n2.split() if t not in stop_words and len(t) > 1])
        
        if not set1 or not set2:
            return {"score": 0.0, "is_match": False, "reason": "No hay suficientes datos"}
            
        intersection = set1.intersection(set2)
        union = set1.union(set2)
        jaccard = len(intersection) / len(union)
        
        # 4. CASOS ESPECIALES (Penalizar diferencias críticas en modelos parecidos)
        # Si un nombre tiene "fe" o "pro" o "ti" y el otro no, es un conflicto.
        critical_variants = {"fe", "pro", "ti", "ultra", "plus", "max", "slim", "light"}
        for variant in critical_variants:
            if (variant in set1 and variant not in set2) or (variant in set2 and variant not in set1):
                jaccard *= 0.6 # Penalización fuerte

        final_score = round(jaccard, 2)
        
        return {
            "score": final_score,
            "is_match": final_score >= self.MATCH_THRESHOLD,
            "specs": specs1,
            "tokens_matched": list(intersection)
        }

if __name__ == "__main__":
    # Test rápido de escritorio
    matcher = ProductMatcher()
    print(matcher.get_similarity_score("Monitor 24\" 144hz", "Monitor 24 pulgadas 75hz")) # 0.0 por conflicto Hz
    print(matcher.get_similarity_score("SSD Kingston 1TB", "Disco Solido Kingston NV3 1 TB")) # Match alto
    print(matcher.get_similarity_score("Logitech G305", "Mouse G305 Logitech Inalámbrico")) # Match alto
