def calculate_sustainability_score(sustainability_data):
    # Normalize values (assuming max possible footprint per category is 100kg CO₂e)
    weights = {
        'materials': 0.3,
        'production': 0.25,
        'packaging': 0.2,
        'transportation': 0.15,
        'disposal': 0.1
    }
    
    scores = {
        'materials': max(0, 100 - sustainability_data.materials_footprint),
        'production': max(0, 100 - sustainability_data.production_footprint),
        'packaging': max(0, 100 - sustainability_data.packaging_footprint),
        'transportation': max(0, 100 - sustainability_data.transportation_footprint),
        'disposal': max(0, 100 - sustainability_data.disposal_footprint),
    }
    
    total_score = sum(weight * (score/100) for weight, score in zip(weights.values(), scores.values()))
    return round(total_score * 100, 2)