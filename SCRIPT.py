standards = {
    "Pb": 0.01,   # Lead
    "Cd": 0.003,  # Cadmium
    "As": 0.01,   # Arsenic
    "Cr": 0.05,   # Chromium
    "Ni": 0.02    # Nickel
}

def calc_CF(M, S):
    return M/S

def calc_HEI(data):
    return sum([M/standards[metal] for metal, M in data.items()])

# Example input
sample = {"Pb": 0.02, "Cd": 0.004, "As": 0.015}
hei_value = calc_HEI(sample)
print("HEI:", hei_value)
