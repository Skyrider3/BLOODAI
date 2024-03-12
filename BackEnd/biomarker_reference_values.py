
# Define function to get reference values based on biomarker
def get_reference_values(biomarker):
    # Mockup of reference values for demonstration purposes
    if biomarker == "Ferritin":
        return [
            {"id": "1", "color": "red", "min": 0, "max": 3.35},
            {"id": "2", "color": "orange", "min": 3.35, "max": 3.72},
            {"id": "3", "color": "yellow", "min": 3.72, "max": 4.09},
            {"id": "4", "color": "green", "min": 4.09, "max": 4.83},
            {"id": "5", "color": "yellow", "min": 4.83, "max": 5.2},
            {"id": "6", "color": "orange", "min": 5.2, "max": 5.57},
            {"id": "7", "color": "red", "min": 5.7, "max": 6.07}
        ]
    else : 
        return [
            {"id": "1", "color": "red", "min": 0, "max": 3.35},
            {"id": "2", "color": "orange", "min": 3.35, "max": 3.72},
            {"id": "3", "color": "yellow", "min": 3.72, "max": 4.09},
            {"id": "4", "color": "green", "min": 4.09, "max": 4.83},
            {"id": "5", "color": "yellow", "min": 4.83, "max": 5.2},
            {"id": "6", "color": "orange", "min": 5.2, "max": 5.57},
            {"id": "7", "color": "red", "min": 5.7, "max": 6.07}
            ]
    
####for bar plot 
    
def get_reference_values_barplot(biomarker):
    # Mockup of reference values for demonstration purposes
    if biomarker == "Ferritin":
        return [
            {"id": "alarm-one", "color": "red", "min": 0, "max": 3.35},
            {"id": "lab-one", "color": "orange", "min": 3.35, "max": 3.72},
            {"id": "lab-two", "color": "yellow", "min": 3.72, "max": 4.09},
            {"id": "optimal", "color": "green", "min": 4.09, "max": 4.83},
            {"id": "lab-three", "color": "yellow", "min": 4.83, "max": 5.2},
            {"id": "lab-four", "color": "orange", "min": 5.2, "max": 5.57},
            {"id": "alarm-two", "color": "red", "min": 5.7, "max": 6.07}
        ]
    else : 
        return [
            {"id": "alarm-one", "color": "red", "min": 0, "max": 3.35},
            {"id": "lab-one", "color": "orange", "min": 3.35, "max": 3.72},
            {"id": "lab-two", "color": "yellow", "min": 3.72, "max": 4.09},
            {"id": "optimal", "color": "green", "min": 4.09, "max": 4.83},
            {"id": "lab-three", "color": "yellow", "min": 4.83, "max": 5.2},
            {"id": "lab-four", "color": "orange", "min": 5.2, "max": 5.57},
            {"id": "alarm-two", "color": "red", "min": 5.7, "max": 6.07}
            ]

##page3 dynamic part of it 
# Sample data for reference values (you can replace this with your actual data) --------------fill this 
def biomarker_LowHigh_range_values():
    reference_values = {
        "Ferritin": {"normal_range": [11, 306], "units": "ng/mL"},
        "HCT": {"normal_range": [36, 46], "units": "g/dL"},
        "Hematocrit": {"normal_range": [34, 46.6], "units": "g/dL"},
        "Iron Serum": {"normal_range": [28, 170], "units": "ug/dL"},
        "Mean Corp HGB": {"normal_range": [26.6, 33], "units": "pg"},
        "Mean Corp HGB Conc.": {"normal_range": [31.5, 35.7], "units": "g/dL"},
        "Mean Corp Volume": {"normal_range": [79, 97], "units": "fL"},
        "Mean Corpuscular Volume (MCV)": {"normal_range": [80, 100], "units": "fL"},
        "Mean Platelet Volume (MPV)": {"normal_range": [8.4, 12], "units": "fl"},
        "Platelet": {"normal_range": [320, 320], "units": "x10e3/uL"},
        "RBC": {"normal_range": [4, 5.2], "units": "M/uL"},
        "RED DISTRIB. WIDTH": {"normal_range": [12.3, 15.4], "units": "g/dL"},
        "Cholesterol": {"normal_range": [100, 200], "units": "mg/dL"},
        "HDL Cholesterol": {"normal_range": [35, 100], "units": "mg/dL"},
        "LDL Cholesterol": {"normal_range": [50, 129], "units": "mg/dL"},
        "Triglycerides": {"normal_range": [40, 150], "units": "mg/dL"},
        "Basophil #": {"normal_range": [44.4, 44.4], "units": "x10e3/uL"},
        "Basophil %": {"normal_range": [1, 1], "units": "g/dL"},
        "Eosinophil #": {"normal_range": [0.3, 0.3], "units": "x10e3/uL"},
        "Eosinophil %": {"normal_range": [4, 4], "units": "g/dL"},
        "Lymphocyte #": {"normal_range": [2, 2], "units": "x10e3/uL"},
        "Lymphocyte %": {"normal_range": [24.6, 24.6], "units": "g/dL"},
        "Monocyte #": {"normal_range": [0.6, 0.6], "units": "x10e3/uL"},
        "Monocyte %": {"normal_range": [8.2, 8.2], "units": "g/dL"},
        "Neutrophil #": {"normal_range": [4.8, 4.8], "units": "x10e3/uL"},
        "Neutrophil %": {"normal_range": [61, 61], "units": "g/dL"},
        "WBC": {"normal_range": [4.5, 11], "units": "k/uL"},
        "Immature Granulocytes (Auto) #": {"normal_range": [0.03, 0.03], "units": "x10e3/uL"},
        "Immature Granulocytes (Auto) %": {"normal_range": [0.4, 0.4], "units": "g/dL"},
        "ALT": {"normal_range": [7, 33], "units": "U/L"},
        "ALT (SGPT)": {"normal_range": [44.4, 40], "units": "IU/L"},
        "Glucose": {"normal_range": [70, 110], "units": "mg/dL"},
        "Hemoglobin A1C": {"normal_range": [4.3, 5.9], "units": "g/dL"},
        "Albumin": {"normal_range": [4, 5], "units": "g/dL"},
        "Albumin, BLD": {"normal_range": [3.5, 5.5], "units": "g/dL"},
        "AST": {"normal_range": [9, 32], "units": "U/L"},
        "AST (SGOT)": {"normal_range": [44.4, 32], "units": "IU/L"},
        "Potassium": {"normal_range": [3.4, 5], "units": "mmol/L"},
        "Sodium": {"normal_range": [134, 144], "units": "mmol/L"},
        "A/G Ratio": {"normal_range": [1.2, 2.2], "units": "g/dL"},
        "ABSOLUTE NRBC": {"normal_range": [44.4, 0.01], "units": "k/uL"},
        "Alanine Aminotransferase": {"normal_range": [14, 54], "units": "U/L"},
        "Albumin / Globulin Ratio": {"normal_range": [1, 2.6], "units": "g/dL"},
        "Alkaline Phosphatase": {"normal_range": [39, 117], "units": "IU/L"},
        "Anion Gap": {"normal_range": [3, 17], "units": "mmol/L"},
        "Aspartate Amino Transferase": {"normal_range": [15, 41], "units": "U/L"},
        "Bilirubin total": {"normal_range": [44.4, 1.2], "units": "mg/dL"},
        "BUN": {"normal_range": [8, 25], "units": "mg/dL"},
        "Bun / CREAT": {"normal_range": [9, 23], "units": "g/dL"},
        "Calcium": {"normal_range": [8.7, 10.2], "units": "mg/dL"},
        "Carbon Dioxide, Total": {"normal_range": [20, 29], "units": "mmol/L"},
        "Cardiac Risk Ratio": {"normal_range": [44.4, 5], "units": "g/dL"},
        "Chloride": {"normal_range": [96, 106], "units": "mmol/L"},
        "Cholesterol / HDL Ratio": {"normal_range": [3.27, 7.05], "units": "g/dL"},
        "Creatinine": {"normal_range": [0.57, 1], "units": "mg/dL"},
        "EGFR": {"normal_range": [59, 120], "units": "mL/min/1.73m2"},
    
    }
    return reference_values
 #---this is connected to get_biomarkers_info() function