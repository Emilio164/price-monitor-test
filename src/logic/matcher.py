import re
import unicodedata
from typing import Dict, Any, List, Set

class ProductMatcher:
    def __init__(self):
        self.known_brands = [
            "samsung", "lg", "viewsonic", "asus", "tuf", "gigabyte", "msi", "corsair", 
            "logitech", "kingston", "wd", "western digital", "crucial", "patriot",
            "team", "razer", "hyperx", "redragon", "arctic", "sentey", "evga", "fury", "beast", "harrow"
        ]
        
        # Mapeo de sinónimos para unificar conceptos
        self.synonyms = {
            "wireless": "inalambrico",
            "bluetooth": "bt",
            "power supply": "fuente",
            "solid state drive": "ssd",
            "display": "monitor"
        }

        self.units = ["pulg", "g", "hz", "w", "tb", "gb", "mb", "mhz", "v"]
        self.MATCH_THRESHOLD = 0.75 

    def normalize_text(self, text: str) -> str:
        if not text: return ""
        text = text.lower()
        text = "".join(c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn')
        
        # 1. Normalizar sinónimos
        for word, syn in self.synonyms.items():
            text = text.replace(word, syn)

        text = text.replace('"', ' pulg ')
        text = re.sub(r'(ddr)\s*(\d)', r' \1 \2 ', text)
        
        # 2. Normalizar unidades (evitar que 5w en un código de modelo se capture si es < 10)
        # Solo capturamos unidades si el número tiene 2 o más cifras o si es g/pulg
        text = re.sub(r'(\d+)\s*(mhz|hz|gb|tb|w|g|mb|v)', r' \1 \2 ', text)
        
        text = re.sub(r'[^a-z0-9\s]', ' ', text)
        return re.sub(r'\s+', ' ', text).strip()

    def extract_specs(self, normalized_name: str) -> Dict[str, str]:
        specs = {}
        # Filtro: No capturamos Watts menores a 10 (suelen ser ruidos de nombres de modelos como PG5W)
        pattern = rf'(\d+(?:\.\d+)?)\s*({"|".join(self.units)})'
        matches = re.findall(pattern, normalized_name)
        for value, unit in matches:
            val_float = float(value)
            if unit == "w" and val_float < 10: continue 
            specs[unit] = value
            
        if "mhz" not in specs:
            mhz_match = re.search(r'\b(2400|2666|3000|3200|3600|4800|5200|5600|6000)\b', normalized_name)
            if mhz_match: specs["mhz"] = mhz_match.group(1)

        ddr_match = re.search(r'\bddr\s*(\d)\b', normalized_name)
        if ddr_match: specs["ddr"] = ddr_match.group(1)

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
        # Añadimos palabras genéricas a las stopwords para que no "inflen" ni "desinflen" el score
        cat_words = {"monitor", "fuente", "joystick", "gamepad", "teclado", "mouse", "auricular", "auriculares", "gamer", "gaming", "disco", "solido", "ssd", "memoria", "ram"}
        stop_words = {"de", "con", "para", "negro", "black", "white", "blanco", "pulg", "g", "hz", "w", "tb", "gb", "mb", "mhz"} | cat_words
        
        set1 = set([t for t in n1.split() if t not in stop_words and len(t) > 1])
        set2 = set([t for t in n2.split() if t not in stop_words and len(t) > 1])
        
        if not set1 or not set2: return {"score": 0.0, "is_match": False}
            
        intersection = set1.intersection(set2)
        union = set1.union(set2)
        jaccard = len(intersection) / len(union)
        
        # 4. PENALIZACIÓN POR VARIANTES CRÍTICAS
        # Bajamos la penalización a 0.4 para ser muy estrictos
        critical_variants = {"fe", "pro", "ti", "ultra", "plus", "max", "slim", "light", "rgb", "oc", "inalambrico", "bt"}
        for variant in critical_variants:
            if (variant in set1 and variant not in set2) or (variant in set2 and variant not in set1):
                jaccard *= 0.4
        
        # 5. BONUS POR COINCIDENCIA TÉCNICA
        # Si las specs (ej: 180hz, 24pulg) son idénticas y existen, damos un gran salto
        if specs1 and specs2 and specs1 == specs2:
            jaccard += 0.25

        final_score = round(min(1.0, jaccard), 2)
        
        return {
            "score": final_score,
            "is_match": final_score >= self.MATCH_THRESHOLD,
            "specs": specs1
        }
