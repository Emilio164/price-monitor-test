import re
import unicodedata
from typing import Dict, Any, List, Set

class ProductMatcher:
    def __init__(self):
        self.known_brands = [
            "samsung", "lg", "viewsonic", "asus", "gigabyte", "msi", "corsair", 
            "logitech", "kingston", "wd", "western digital", "crucial", "patriot",
            "team", "razer", "hyperx", "redragon", "arctic", "sentey", "evga", "fury"
        ]
        
        self.unit_map = {
            r'"|pul|pulgadas|in': "pulg",
            r'gramos|gr|g(?!\w)': "g",
            r'hz|hertz': "hz",
            r'watts|w(?!\w)': "w",
            r'terabytes|tb': "tb",
            r'gigabytes|gb|gigas|gb': "gb",
            r'megabytes|mb': "mb",
            r'mhz': "mhz",
            r'va|voltios': "v"
        }
        
        self.MATCH_THRESHOLD = 0.85

    def normalize_text(self, text: str) -> str:
        if not text: return ""
        text = text.lower()
        text = "".join(c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn')
        
        # Normalización especial para RAM: DDR4, DDR5
        text = re.sub(r'ddr\s*(\d)', r' ddr\1 ', text)
        
        for pattern, replacement in self.unit_map.items():
            text = re.sub(pattern, " " + replacement + " ", text)
        
        text = re.sub(r'[^a-z0-9\s]', ' ', text)
        return re.sub(r'\s+', ' ', text).strip()

    def extract_specs(self, normalized_name: str) -> Dict[str, str]:
        specs = {}
        # 1. Unidades estándar (Número + Unidad)
        units = "|".join(set(self.unit_map.values()))
        pattern = rf'(\d+(?:\.\d+)?)\s*({units})'
        matches = re.findall(pattern, normalized_name)
        for value, unit in matches:
            specs[unit] = value
            
        # 2. Inteligencia para MHz huérfanos (ej: 3200 sin mhz)
        if "mhz" not in specs:
            mhz_match = re.search(r'\b(2400|2666|3000|3200|3600|4800|5200|5600|6000)\b', normalized_name)
            if mhz_match:
                specs["mhz"] = mhz_match.group(1)

        # 3. Inteligencia para RAM DDR
        ddr_match = re.search(r'\bddr(\d)\b', normalized_name)
        if ddr_match:
            specs["ddr"] = ddr_match.group(1)

        return specs

    def get_similarity_score(self, name1: str, name2: str) -> Dict[str, Any]:
        n1 = self.normalize_text(name1)
        n2 = self.normalize_text(name2)
        
        specs1 = self.extract_specs(n1)
        specs2 = self.extract_specs(n2)
        
        # 1. BLOQUEO POR CONFLICTO TÉCNICO
        for unit in specs1:
            if unit in specs2 and specs1[unit] != specs2[unit]:
                return {"score": 0.0, "is_match": False, "reason": f"Conflicto de {unit}: {specs1[unit]} vs {specs2[unit]}"}

        # 2. COMPARACIÓN DE MARCAS
        brand1 = next((b for b in self.known_brands if b in n1), None)
        brand2 = next((b for b in self.known_brands if b in n2), None)
        if brand1 and brand2 and brand1 != brand2:
            return {"score": 0.0, "is_match": False, "reason": f"Marcas diferentes: {brand1} vs {brand2}"}

        # 3. SIMILITUD DE TOKENS (Jaccard)
        stop_words = {"de", "con", "para", "negro", "black", "white", "blanco", "pulg", "g", "hz", "w", "tb", "gb", "mb", "memoria", "ram"}
        set1 = set([t for t in n1.split() if t not in stop_words and len(t) > 1])
        set2 = set([t for t in n2.split() if t not in stop_words and len(t) > 1])
        
        if not set1 or not set2:
            return {"score": 0.0, "is_match": False}
            
        intersection = set1.intersection(set2)
        union = set1.union(set2)
        jaccard = len(intersection) / len(union)
        
        # 4. PENALIZACIÓN POR VARIANTES CRÍTICAS (Evitar falsos positivos)
        # Añadimos 'rgb' y 'pro' para que no se mezclen memorias con y sin luces
        critical_variants = {"fe", "pro", "ti", "ultra", "plus", "max", "slim", "light", "rgb", "oc"}
        for variant in critical_variants:
            if (variant in set1 and variant not in set2) or (variant in set2 and variant not in set1):
                jaccard *= 0.5 # Penalización del 50%
        
        # 5. BONUS POR COINCIDENCIA DE SPECS
        # Si coinciden en specs clave (DDR, MHz, GB), subimos el score
        if specs1 and specs2 and specs1 == specs2:
            jaccard += 0.1

        final_score = round(min(1.0, jaccard), 2)
        
        return {
            "score": final_score,
            "is_match": final_score >= self.MATCH_THRESHOLD,
            "specs": specs1
        }
