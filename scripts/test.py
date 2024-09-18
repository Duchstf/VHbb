import awkward as ak
import numpy as np

def get_ddt_value_elementwise(pt, rho, pt_edges, rho_edges, smooth_ddtmap):
    # Define an inner function that works on individual pt and rho values
    def get_ddt_value_single(pt_val, rho_val):
        # Find the pt bin index
        pt_bin = np.digitize([pt_val], pt_edges)[0] - 1
        if pt_bin < 0 or pt_bin >= len(pt_edges) - 1:
            raise ValueError(f"pt value {pt_val} is out of range of the pt edges.")
        
        # Find the rho bin index
        rho_bin = np.digitize([rho_val], rho_edges)[0] - 1
        if rho_bin < 0 or rho_bin >= len(rho_edges) - 1:
            raise ValueError(f"rho value {rho_val} is out of range of the rho edges.")
        
        # Get the corresponding value from the smooth_ddtmap
        return smooth_ddtmap[pt_bin, rho_bin]
    
    # Apply the get_ddt_value_single function element-wise to pt and rho using ak.Array's map-like behavior
    ddt_values = ak.Array([get_ddt_value_single(p, r) for p, r in zip(pt, rho)])
    
    return ddt_values

# Example usage
pt_edges = [200, 300, 400, 500, 600]  # Example pt bin edges
rho_edges = [-6.0, -4.5, -3.0, -1.5, 0.0]  # Example rho bin edges
smooth_ddtmap = np.array([
    [0.1, 0.2, 0.3, 0.4],
    [0.15, 0.25, 0.35, 0.45],
    [0.2, 0.3, 0.4, 0.5],
    [0.25, 0.35, 0.45, 0.55]
])  # Example smooth_ddtmap (4x4 matrix)

# Example Awkward arrays for pt and rho
pt_array = ak.Array([250, 350, 450, 500])
rho_array = ak.Array([-5.0, -3.5, -2.0, -1.0])

# Apply the function
try:
    ddt_values = get_ddt_value_elementwise(pt_array, rho_array, pt_edges, rho_edges, smooth_ddtmap)
    print(f"DDT values: {ddt_values}")
except ValueError as e:
    print(e)
