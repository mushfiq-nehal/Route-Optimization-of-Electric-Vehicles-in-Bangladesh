"""
RSU Visualization Tool
Visualizes RSU positions and coverage areas on the road network
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from typing import List, Dict, Tuple

# RSU positions from the network
RSU_POSITIONS = {
    'RSU_Chachra': (-165.47, -199.59),
    'RSU_Dhormotola': (-194.59, 27.16),
    'RSU_Doratana': (-44.04, 49.98),
    'RSU_Monihar': (79.98, -8.38),
    'RSU_Muroli': (223.72, -213.15),
    'RSU_NewMarket': (2.93, 170.72),
    'RSU_Palbari': (-218.70, 214.90),
}

# Road network boundaries (from CustomRoadNetwork.net.xml)
NETWORK_BOUNDS = {
    'min_x': -218.70,
    'max_x': 223.72,
    'min_y': -215.27,
    'max_y': 214.90
}

def visualize_rsu_coverage(coverage_radius: float = 500.0, save_file: str = None):
    """
    Visualize RSU positions and their coverage areas
    
    Args:
        coverage_radius: Coverage radius in meters
        save_file: Optional filename to save the plot
    """
    fig, ax = plt.subplots(figsize=(14, 12))
    
    # Set network boundaries
    ax.set_xlim(NETWORK_BOUNDS['min_x'] - 100, NETWORK_BOUNDS['max_x'] + 100)
    ax.set_ylim(NETWORK_BOUNDS['min_y'] - 100, NETWORK_BOUNDS['max_y'] + 100)
    
    # Draw coverage circles for each RSU
    colors = plt.cm.rainbow([i/len(RSU_POSITIONS) for i in range(len(RSU_POSITIONS))])
    
    for idx, (rsu_id, position) in enumerate(RSU_POSITIONS.items()):
        x, y = position
        color = colors[idx]
        
        # Draw coverage circle
        circle = patches.Circle(
            (x, y), 
            coverage_radius, 
            color=color, 
            alpha=0.15, 
            label=f'{rsu_id} Coverage'
        )
        ax.add_patch(circle)
        
        # Draw RSU position marker
        ax.plot(x, y, 'o', color=color, markersize=12, markeredgecolor='black', 
                markeredgewidth=2, label=f'{rsu_id} Position')
        
        # Add RSU label
        ax.annotate(
            rsu_id.replace('RSU_', ''), 
            (x, y), 
            textcoords="offset points", 
            xytext=(0, 15), 
            ha='center',
            fontsize=10,
            fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.5', facecolor=color, alpha=0.7)
        )
    
    # Draw network boundary
    boundary = patches.Rectangle(
        (NETWORK_BOUNDS['min_x'], NETWORK_BOUNDS['min_y']),
        NETWORK_BOUNDS['max_x'] - NETWORK_BOUNDS['min_x'],
        NETWORK_BOUNDS['max_y'] - NETWORK_BOUNDS['min_y'],
        linewidth=2,
        edgecolor='black',
        facecolor='none',
        linestyle='--',
        label='Network Boundary'
    )
    ax.add_patch(boundary)
    
    # Styling
    ax.set_xlabel('X Coordinate (m)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Y Coordinate (m)', fontsize=12, fontweight='bold')
    ax.set_title(
        f'RSU Network Coverage Map\nCoverage Radius: {coverage_radius}m', 
        fontsize=16, 
        fontweight='bold',
        pad=20
    )
    ax.grid(True, alpha=0.3, linestyle=':', linewidth=0.5)
    ax.set_aspect('equal')
    
    # Add legend (remove duplicates)
    handles, labels = ax.get_legend_handles_labels()
    unique_labels = {}
    for handle, label in zip(handles, labels):
        if 'Coverage' in label:
            rsu_name = label.split(' Coverage')[0]
            if rsu_name not in unique_labels:
                unique_labels[rsu_name] = handle
    
    # Add network boundary to legend
    unique_labels['Network Boundary'] = boundary
    
    ax.legend(
        unique_labels.values(), 
        unique_labels.keys(), 
        loc='upper left', 
        bbox_to_anchor=(1.02, 1),
        fontsize=9,
        framealpha=0.9
    )
    
    plt.tight_layout()
    
    if save_file:
        plt.savefig(save_file, dpi=300, bbox_inches='tight')
        print(f"RSU coverage map saved to {save_file}")
    
    plt.show()

def calculate_coverage_statistics(coverage_radius: float = 500.0):
    """
    Calculate coverage statistics for the RSU network
    
    Args:
        coverage_radius: Coverage radius in meters
    """
    print("="*60)
    print("RSU NETWORK COVERAGE STATISTICS")
    print("="*60)
    print(f"Coverage Radius: {coverage_radius}m")
    print(f"Number of RSUs: {len(RSU_POSITIONS)}")
    print()
    
    # Calculate total coverage area
    total_coverage = len(RSU_POSITIONS) * 3.14159 * (coverage_radius ** 2)
    
    # Calculate network area
    network_width = NETWORK_BOUNDS['max_x'] - NETWORK_BOUNDS['min_x']
    network_height = NETWORK_BOUNDS['max_y'] - NETWORK_BOUNDS['min_y']
    network_area = network_width * network_height
    
    coverage_percentage = (total_coverage / network_area) * 100
    
    print(f"Network Dimensions: {network_width:.2f}m × {network_height:.2f}m")
    print(f"Network Area: {network_area:,.2f} m²")
    print(f"Total Coverage Area: {total_coverage:,.2f} m²")
    print(f"Coverage Percentage: {coverage_percentage:.2f}%")
    print()
    
    # RSU positions
    print("RSU Positions:")
    for rsu_id, position in RSU_POSITIONS.items():
        print(f"  {rsu_id}: {position}")
    print("="*60)

def find_coverage_gaps(coverage_radius: float = 500.0, grid_resolution: int = 50):
    """
    Identify areas not covered by any RSU
    
    Args:
        coverage_radius: Coverage radius in meters
        grid_resolution: Number of grid points to check
    """
    import numpy as np
    
    x_points = np.linspace(NETWORK_BOUNDS['min_x'], NETWORK_BOUNDS['max_x'], grid_resolution)
    y_points = np.linspace(NETWORK_BOUNDS['min_y'], NETWORK_BOUNDS['max_y'], grid_resolution)
    
    uncovered_points = []
    
    for x in x_points:
        for y in y_points:
            covered = False
            for rsu_pos in RSU_POSITIONS.values():
                distance = ((x - rsu_pos[0])**2 + (y - rsu_pos[1])**2)**0.5
                if distance <= coverage_radius:
                    covered = True
                    break
            
            if not covered:
                uncovered_points.append((x, y))
    
    coverage_ratio = 1 - (len(uncovered_points) / (grid_resolution ** 2))
    
    print()
    print("Coverage Gap Analysis:")
    print(f"Grid Resolution: {grid_resolution}×{grid_resolution}")
    print(f"Uncovered Grid Points: {len(uncovered_points)}/{grid_resolution**2}")
    print(f"Coverage Ratio: {coverage_ratio*100:.2f}%")
    
    return uncovered_points

def main():
    """Main visualization function"""
    coverage_radius = 500.0  # meters
    
    # Calculate and print statistics
    calculate_coverage_statistics(coverage_radius)
    
    # Find coverage gaps
    find_coverage_gaps(coverage_radius)
    
    # Visualize RSU coverage
    print("\nGenerating visualization...")
    visualize_rsu_coverage(
        coverage_radius=coverage_radius,
        save_file="rsu_coverage_map.png"
    )

if __name__ == "__main__":
    main()
