# test_overlap.py
from overlap_calculator import OverlapCalculator
from config import ALPHA_VANTAGE_API_KEY

print("Iniciando teste...")

calculator = OverlapCalculator(ALPHA_VANTAGE_API_KEY)

print("\nTestando cálculo de overlap...")

try:
    result = calculator.calculate_overlap("SPY", "VOO")
    print("\n✅ SUCESSO!")
    print(f"Overlap médio: {result['overlap_average']:.2f}%")
except Exception as e:
    print(f"\n❌ ERRO: {e}")
    import traceback
    traceback.print_exc()
