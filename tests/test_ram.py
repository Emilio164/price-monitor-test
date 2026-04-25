from src.logic.matcher import ProductMatcher
import os

def run_test():
    matcher = ProductMatcher()
    
    # Nombres exactos que fallaron
    p1 = "Memoria RAM Kingston Fury Beast 16GB DDR4 3200MHZ"
    p2 = "MEMORIA 16GB DDR4 3200 KINGSTON FURY BEAST"
    
    # Análisis detallado
    n1 = matcher.normalize_text(p1)
    n2 = matcher.normalize_text(p2)
    
    specs1 = matcher.extract_specs(n1)
    specs2 = matcher.extract_specs(n2)
    
    res = matcher.get_similarity_score(p1, p2)
    
    print("\n" + "="*40)
    print("TEST DE SIMILITUD DE MEMORIAS")
    print("="*40)
    print(f"P1: {p1}")
    print(f"P2: {p2}")
    print("-" * 40)
    print(f"Normalizado 1: {n1}")
    print(f"Normalizado 2: {n2}")
    print(f"Specs 1: {specs1}")
    print(f"Specs 2: {specs2}")
    print("-" * 40)
    print(f"SCORE FINAL: {res['score']}")
    print(f"¿ES MATCH?: {res['is_match']}")
    if not res['is_match']:
        print(f"RAZÓN DE RECHAZO: {res.get('reason', 'Score por debajo del umbral 0.85')}")
    print("="*40 + "\n")

if __name__ == "__main__":
    run_test()
