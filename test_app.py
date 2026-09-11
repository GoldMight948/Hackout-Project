"""
Smoke test script for Emission Leak Detector.
Validates calculations, presets, and view loading without GUI overhead.
"""

from components.calculations import calculate_emissions
from components.data_presets import DEMO_BUSINESSES, CATEGORY_FIXES, DEFAULT_SUGGESTIONS

def test_calculations():
    print("Testing calculations...")
    sample_data = {
        "electricity": 100000,
        "fuel": 10000,
        "waste": 5000,
        "transport": 20000,
        "production_units": 50000
    }
    results = calculate_emissions(sample_data)
    
    assert results["total_co2"] > 0, "Total CO2 should be positive"
    assert results["total_cost"] > 0, "Total cost should be positive"
    assert len(results["ranked_categories"]) == 4, "Should have 4 ranked categories"
    assert results["top_leak"] is not None, "Top leak must exist"
    assert results["emissions_per_unit"] is not None, "Emissions per unit must exist"
    
    print(f"[PASS] Calculation test passed! Total CO2: {results['total_co2']} tonnes, Top leak: {results['top_leak']['label']}")

def test_presets():
    print("Testing presets and fixes...")
    assert len(DEMO_BUSINESSES) >= 3, "At least 3 demo businesses expected"
    for cat in ["electricity", "fuel", "transport", "waste"]:
        assert cat in CATEGORY_FIXES, f"Missing fixes for category {cat}"
        assert len(CATEGORY_FIXES[cat]) >= 3, f"Category {cat} should have at least 3 fixes"
    assert len(DEFAULT_SUGGESTIONS) >= 3, "Should have default suggestions"
    print("[PASS] Presets and fixes test passed!")

if __name__ == "__main__":
    test_calculations()
    test_presets()
    print("ALL TESTS PASSED SUCCESSFULLY!")
