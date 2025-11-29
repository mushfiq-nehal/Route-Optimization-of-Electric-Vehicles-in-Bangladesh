# Route Analysis: Palbari to Doratana

## Network Junctions:
- **Palbari** (Start point)
- **New_Market** 
- **Dhormotola**
- **Chachra** (Chacra)
- **Monihar**
- **Doratana** (End point)

## Available Edges:
- **E0**: Palbari → Doratana (Direct, 24.1 km)
- **E1**: Doratana → New_Market
- **E2**: Palbari → New_Market (23.0 km)
- **E3**: Palbari → Dhormotola (18.9 km)
- **E3.189**: Dhormotola → Chachra (22.8 km)
- **E4**: Doratana → Chachra (27.9 km)
- **E5**: Chachra → Muroli (39.0 km)
- **E6**: Muroli → Monihar (25.0 km)
- **E7**: Monihar → Doratana (13.7 km)
- **E8**: Monihar → New_Market (20.3 km)
- **E9**: Dhormotola → Doratana (15.3 km)

## Requested Routes from Palbari to Doratana:

### Route 1: Palbari → Doratana (Direct)
**Edges**: `E0`
**Distance**: 2.41 km
**Description**: Direct route

### Route 2: Palbari → New Market → Doratana
**Problem**: No direct edge from New_Market to Doratana
**Alternative**: Use E2 (Palbari → New_Market), then need to go through Monihar
**Edges**: `E2 -E8 -E7` (going backwards through edges)
**Note**: Need to use reverse edges

### Route 3: Palbari → New Market → Monihar → Doratana
**Edges**: `E2 -E8 E7`
**Distance**: 2.30 + 2.03 + 1.37 = 5.70 km
**Description**: Via New Market and Monihar

### Route 4: Palbari → Dhormotola → Doratana
**Edges**: `E3 E9`
**Distance**: 1.89 + 1.53 = 3.42 km
**Description**: Via Dhormotola

### Route 5: Palbari → Dhormotola → Chachra → Doratana
**Edges**: `E3 E3.189 -E4`
**Distance**: 1.89 + 2.28 + 2.79 = 6.96 km
**Description**: Via Dhormotola and Chachra (using reverse E4)

## Valid Routes Configuration:

Based on network topology, here are the 5 valid routes:

1. **E0** - Direct (2.41 km)
2. **E3 E9** - Via Dhormotola (3.42 km) 
3. **E3 E3.189 -E4** - Via Dhormotola and Chachra (6.96 km)
4. **E2 -E1** - Via New Market (need reverse E1)
5. **Alternative**: E2 to New Market, then to Monihar, then to Doratana
