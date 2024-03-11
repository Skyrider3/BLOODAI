
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