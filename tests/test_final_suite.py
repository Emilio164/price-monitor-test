from src.logic.matcher import ProductMatcher

def run_suite():
    matcher = ProductMatcher()
    
    test_cases = [
        {
            "id": 1,
            "n1": " Monitor Gamer ASUS TUF VG249QL3A-J 24\" FHD IPS 180Hz Freesync Premium G-SYNC Compatible ",
            "n2": "MONITOR GAMER 24\" ASUS TUF VG249QL3A IPS FHD HDMI 180HZ 1MS",
            "expected": "IGUALES"
        },
        {
            "id": 2,
            "n1": "FUENTE 850W GIGABYTE GP-UD850GM 80 PLUS GOLD",
            "n2": "FUENTE GIGABYTE 850W 80 PLUS WHITE GP-UD850GM PG5W ",
            "expected": "IGUALES"
        },
        {
            "id": 3,
            "n1": "Auriculares gamer inalámbricos HyperX Cloud III Wireless Black",
            "n2": "Auriculares Gamer HyperX Cloud III Black",
            "expected": "DIFERENTES"
        },
        {
            "id": 4,
            "n1": "JOYSTICK GAMEPAD WIRELESS REDRAGON HARROW G808 PC PS3",
            "n2": "Joystick Inalámbrico Redragon Harrow G808 PC/PS3",
            "expected": "IGUALES"
        }
    ]

    print("\n" + "="*60)
    print("VALIDACIÓN DE CASOS CRÍTICOS")
    print("="*60)

    for case in test_cases:
        res = matcher.get_similarity_score(case["n1"], case["n2"])
        print(f"CASO {case['id']}:")
        print(f"  A: {case['n1'][:50]}...")
        print(f"  B: {case['n2'][:50]}...")
        print(f"  Score: {res['score']} | Es Match? {res['is_match']}")
        print(f"  Resultado Esperado: {case['expected']}")
        
        # Validación de éxito
        status = "✅ PASÓ" if (res['is_match'] and case['expected'] == "IGUALES") or (not res['is_match'] and case['expected'] == "DIFERENTES") else "❌ FALLÓ"
        print(f"  ESTADO: {status}")
        if status == "❌ FALLÓ":
            print(f"  RAZÓN: {res.get('reason', 'Score no coincide con expectativa')}")
        print("-" * 60)

if __name__ == "__main__":
    run_suite()
