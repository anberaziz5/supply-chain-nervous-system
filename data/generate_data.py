import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

def generate_supply_chain_data(num_records=10000):
    np.random.seed(42)
    
    ports = ["Rotterdam", "Singapore", "Los Angeles", "Shanghai", "Hamburg", "Dubai"]
    carriers = ["Maersk", "MSC", "COSCO", "Hapag-Lloyd", "Evergreen"]
    weather_conditions = ["Clear", "Rain", "Storm", "Typhoon", "Fog"]
    
    data = []
    start_date = datetime(2025, 1, 1)
    
    for i in range(num_records):
        origin = random.choice(ports)
        destination = random.choice([p for p in ports if p != origin])
        carrier = random.choice(carriers)
        weather = random.choices(weather_conditions, weights=[0.6, 0.2, 0.1, 0.05, 0.05])[0]
        
        # Operational metrics
        container_weight_tons = round(random.uniform(10.0, 30.0), 2)
        port_congestion_index = round(random.uniform(0.1, 1.0), 2)
        route_distance_nm = random.randint(3000, 12000)
        
        # Introduce logic for delays (The Bullwhip Catalyst)
        delay_probability = 0.1
        if weather in ["Storm", "Typhoon"]: delay_probability += 0.4
        if port_congestion_index > 0.75: delay_probability += 0.3
        if carrier == "Evergreen" and route_distance_nm > 8000: delay_probability += 0.15
        
        is_delayed = 1 if random.random() < delay_probability else 0
        actual_delay_days = random.randint(2, 14) if is_delayed else 0
        
        data.append({
            "Shipment_ID": f"SHP-{10000 + i}",
            "Date": start_date + timedelta(days=random.randint(0, 365)),
            "Origin_Port": origin,
            "Destination_Port": destination,
            "Carrier": carrier,
            "Weather_En_Route": weather,
            "Container_Weight_Tons": container_weight_tons,
            "Port_Congestion_Index": port_congestion_index,
            "Route_Distance_NM": route_distance_nm,
            "Is_Delayed": is_delayed,
            "Delay_Days": actual_delay_days
        })
        
    df = pd.DataFrame(data)
    df.to_csv("data/historical_logistics.csv", index=False)
    print(f"Generated {num_records} logistics records successfully.")

if __name__ == "__main__":
    generate_supply_chain_data(15000)