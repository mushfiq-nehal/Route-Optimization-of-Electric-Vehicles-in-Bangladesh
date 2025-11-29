"""
RSU (Roadside Unit) Module
Handles communication between vehicles and the server
"""

import math
from typing import List, Dict, Set
import requests
from datetime import datetime


class RSU:
    """Represents a Roadside Unit in the V2I communication system"""
    
    def __init__(self, rsu_id: str, position: tuple, coverage_radius: float, server_url: str):
        """
        Initialize RSU
        
        Args:
            rsu_id: Unique identifier for the RSU
            position: (x, y) coordinates of the RSU
            coverage_radius: Communication range in meters
            server_url: URL of the backend server
        """
        self.rsu_id = rsu_id
        self.position = position  # (x, y)
        self.coverage_radius = coverage_radius
        self.server_url = server_url
        self.vehicle_buffer = []  # Buffer for collected vehicle data
        self.connected_vehicles: Set[str] = set()  # Currently connected vehicles
        
    def is_vehicle_in_range(self, vehicle_position: tuple) -> bool:
        """
        Check if a vehicle is within communication range
        
        Args:
            vehicle_position: (x, y) coordinates of the vehicle
            
        Returns:
            True if vehicle is in range, False otherwise
        """
        distance = math.sqrt(
            (vehicle_position[0] - self.position[0]) ** 2 +
            (vehicle_position[1] - self.position[1]) ** 2
        )
        return distance <= self.coverage_radius
    
    def collect_vehicle_data(self, vehicle_id: str, vehicle_data: Dict, is_ev: bool = True):
        """
        Collect data from a vehicle within range
        
        Args:
            vehicle_id: ID of the vehicle
            vehicle_data: Dictionary containing vehicle telemetry data
            is_ev: Whether the vehicle is an EV (only EVs are tracked)
        """
        # Only collect data from EVs
        if not is_ev:
            return
        
        # Add RSU metadata to the vehicle data
        enriched_data = {
            **vehicle_data,
            'rsu_id': self.rsu_id,
            'rsu_position': self.position,
            'collection_timestamp': datetime.utcnow().isoformat(timespec="seconds") + "Z",
            'vehicle_type': 'EV'
        }
        
        self.vehicle_buffer.append(enriched_data)
        self.connected_vehicles.add(vehicle_id)
        
    def send_data_to_server(self, batch_size: int = 50) -> bool:
        """
        Send buffered vehicle data to the server
        
        Args:
            batch_size: Maximum number of records to send in one batch
            
        Returns:
            True if data was sent successfully, False otherwise
        """
        if not self.vehicle_buffer:
            return True
        
        # Prepare batch
        batch = self.vehicle_buffer[:batch_size]
        
        payload = {
            'rsu_id': self.rsu_id,
            'rsu_position': self.position,
            'vehicle_data': batch,
            'timestamp': datetime.utcnow().isoformat(timespec="seconds") + "Z"
        }
        
        try:
            response = requests.post(
                f"{self.server_url}/ingest_rsu",
                json=payload,
                timeout=5
            )
            response.raise_for_status()
            
            # Remove sent data from buffer
            self.vehicle_buffer = self.vehicle_buffer[batch_size:]
            print(f"[RSU-{self.rsu_id}] Successfully sent {len(batch)} records to server")
            return True
            
        except Exception as e:
            print(f"[RSU-{self.rsu_id}] Failed to send data to server: {e}")
            return False
    
    def update_connected_vehicles(self, current_vehicle_ids: Set[str]):
        """
        Update the list of connected vehicles
        
        Args:
            current_vehicle_ids: Set of vehicle IDs currently in range
        """
        # Remove vehicles that are no longer in range
        disconnected = self.connected_vehicles - current_vehicle_ids
        if disconnected:
            print(f"[RSU-{self.rsu_id}] Vehicles disconnected: {disconnected}")
        
        # Add new vehicles
        new_connections = current_vehicle_ids - self.connected_vehicles
        if new_connections:
            print(f"[RSU-{self.rsu_id}] New vehicles connected: {new_connections}")
        
        self.connected_vehicles = current_vehicle_ids
    
    def get_status(self) -> Dict:
        """
        Get current status of the RSU
        
        Returns:
            Dictionary containing RSU status information
        """
        return {
            'rsu_id': self.rsu_id,
            'position': self.position,
            'coverage_radius': self.coverage_radius,
            'connected_vehicles': len(self.connected_vehicles),
            'buffered_records': len(self.vehicle_buffer)
        }


class RSUNetwork:
    """Manages a network of RSUs"""
    
    def __init__(self, server_url: str):
        """
        Initialize RSU Network
        
        Args:
            server_url: URL of the backend server
        """
        self.rsus: List[RSU] = []
        self.server_url = server_url
        
    def add_rsu(self, rsu_id: str, position: tuple, coverage_radius: float = 500.0):
        """
        Add an RSU to the network
        
        Args:
            rsu_id: Unique identifier for the RSU
            position: (x, y) coordinates
            coverage_radius: Communication range in meters (default: 500m)
        """
        rsu = RSU(rsu_id, position, coverage_radius, self.server_url)
        self.rsus.append(rsu)
        print(f"[RSU Network] Added RSU-{rsu_id} at position {position} with {coverage_radius}m range")
        
    def find_nearest_rsu(self, vehicle_position: tuple) -> RSU:
        """
        Find the nearest RSU to a vehicle
        
        Args:
            vehicle_position: (x, y) coordinates of the vehicle
            
        Returns:
            The nearest RSU that can communicate with the vehicle, or None
        """
        nearest_rsu = None
        min_distance = float('inf')
        
        for rsu in self.rsus:
            if rsu.is_vehicle_in_range(vehicle_position):
                distance = math.sqrt(
                    (vehicle_position[0] - rsu.position[0]) ** 2 +
                    (vehicle_position[1] - rsu.position[1]) ** 2
                )
                if distance < min_distance:
                    min_distance = distance
                    nearest_rsu = rsu
        
        return nearest_rsu
    
    def collect_vehicle_data(self, vehicle_id: str, vehicle_position: tuple, vehicle_data: Dict, is_ev: bool = True):
        """
        Route vehicle data to the nearest RSU
        
        Args:
            vehicle_id: ID of the vehicle
            vehicle_position: (x, y) coordinates
            vehicle_data: Vehicle telemetry data
            is_ev: Whether the vehicle is an EV (only EVs are tracked)
        """
        # Only process EVs
        if not is_ev:
            return
        
        nearest_rsu = self.find_nearest_rsu(vehicle_position)
        
        if nearest_rsu:
            nearest_rsu.collect_vehicle_data(vehicle_id, vehicle_data, is_ev)
        else:
            # Silent skip for non-EVs, only warn for EVs
            if is_ev:
                print(f"[RSU Network] Warning: EV {vehicle_id} not in range of any RSU")
    
    def send_all_data(self, batch_size: int = 50):
        """
        Send data from all RSUs to the server
        
        Args:
            batch_size: Maximum number of records per batch
        """
        for rsu in self.rsus:
            rsu.send_data_to_server(batch_size)
    
    def get_network_status(self) -> List[Dict]:
        """
        Get status of all RSUs in the network
        
        Returns:
            List of RSU status dictionaries
        """
        return [rsu.get_status() for rsu in self.rsus]
    
    def print_network_status(self):
        """Print network status to console"""
        print("\n" + "="*60)
        print("RSU NETWORK STATUS")
        print("="*60)
        for rsu in self.rsus:
            status = rsu.get_status()
            print(f"RSU-{status['rsu_id']}:")
            print(f"  Position: {status['position']}")
            print(f"  Coverage: {status['coverage_radius']}m")
            print(f"  Connected Vehicles: {status['connected_vehicles']}")
            print(f"  Buffered Records: {status['buffered_records']}")
        print("="*60 + "\n")
