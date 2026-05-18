import json

with open('dog_breeds_enriched.json') as f:
    data = json.load(f)

print("\n=== SIZE AUDIT ===\n")
for breed in data:
    print(f"{breed['name']:30} {breed['size']:8} {breed.get('weight', 'no weight')}")

print("\n=== BY SIZE ===")
for size in ['Small', 'Medium', 'Large']:
    breeds = [b['name'] for b in data if b['size'] == size]
    print(f"\n{size} ({len(breeds)}):")
    for b in breeds:
        print(f"  - {b}")
