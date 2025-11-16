# EU5 Production Mechanics

This document provides a comprehensive overview of production, buildings, and
resource management in Europa Universalis 5.

## Buildings Overview

Buildings in EU5 serve diverse functions, from manufacturing goods to unlocking
specialized military units. Building productivity depends directly on how many
pops (population units) are employed within them.

### Production Methods

Each building has one or more Production Methods, which determine:

- **Input**: What goods/resources the building consumes
- **Output**: What goods/resources the building produces
- **Employment**: How many pops are needed for full efficiency

Production methods can be changed to adapt to different economic needs and resource
availability.

## Construction Mechanics

### Construction Costs

Base gold costs for construction vary by technological age:

| Age | Base Cost |
|-----|-----------|
| Age of Traditions (or unlocked without advances) | 50 gold |
| Age of Renaissance | 100 gold |
| Age of Discovery | 200 gold |
| Age of Reformation | 400 gold |
| Age of Absolutism | 800 gold |
| Age of Revolutions | 1200 gold |

**Special Cases**:

- Some buildings cost **4x their standard age price**
- Other buildings use predefined fixed amounts

### Resource Requirements

Construction also requires specific goods beyond gold:

- **If not enough goods are supplied, construction will pause**
- Resources must be available in your market
- Ensure market capacity and trade routes support construction needs

### Construction Process

1. Select location for building
2. Verify gold and resource availability
3. Construction begins (time varies by building type)
4. If resources run out, construction pauses until supply resumes
5. Building completes when both time and resources are satisfied

## Building Levels & Capacity

### Location Capacity

Each location has a **Building Levels cap** determining how many structures can
operate efficiently.

**Exceeding Capacity**:

- Each building level above capacity increases costs by **+5%**
- Penalties compound for multiple excess buildings
- Plan expansion carefully to avoid cost increases

### Capacity Modifiers

Building capacity increases from:

| Source | Capacity Bonus |
|--------|----------------|
| Development points | **+1** per point |
| Town status | **+25** |
| City status | **+100** |
| Capital status | **+5** |
| Market center designation | **+5** |

**Strategic Implication**: Develop locations and promote to cities to support more
buildings.

## Employment & Workforce

### Employment Systems

Four employment systems determine worker allocation to buildings:

1. **Equality**: Jobs distributed equally across all buildings
2. **Most Profitable First**: Prioritizes staffing the most profitable buildings

   first

3. **Infrastructure, then Most Profitable**: Infrastructure buildings staffed

   first, then by profitability

4. **Custom**: Manual control over employment priorities

**Each employment system affects ideological development** of your nation.

### Hiring and Firing

- Buildings **hire at 10% monthly** when profitable
- Buildings **fire at 10% monthly** when unprofitable
- Hiring/firing continues until building reaches optimal employment level

### Building Subsidies

The country can choose to give the building subsidies, which will:

- Prevent firing of employees even when unprofitable
- Maintain employment for strategic buildings
- Cost ongoing gold to maintain
- Useful for critical infrastructure or transitional periods

### Staffing Strategy

**Critical Mistake**: Building more structures than you have workers

- Unstaffed buildings produce nothing
- Waste gold on maintenance for idle buildings
- **Solution**: **Food → Housing → Jobs** sequence
  - Ensure pops have food
  - Provide housing
  - Then build production buildings

**Best Practice**: Fill existing buildings to full capacity before constructing new
ones.

## Building Management

### Autonomous Construction

**Estates construct buildings autonomously** and player cannot override these
decisions:

- Estates build according to their interests
- Nobility builds military and administrative buildings
- Burghers build economic and trade buildings
- Clergy builds religious buildings
- This can conflict with player strategy

### Overlord Construction

- Overlords may initiate construction in subject territories
- Cannot cancel construction once started
- Useful for developing vassals and colonial subjects

### Construction Automation

Available automation options:

- **Automated construction** with customizable gold thresholds
- Set maximum spending per construction project
- Enable/disable automation by building type
- Useful for hands-off economic management

## Production Efficiency

### Factors Affecting Efficiency

Building efficiency depends on:

1. **Staffing Level**:
   - 100% staffed = 100% efficiency
   - 50% staffed = 50% efficiency
   - 0% staffed = 0% production (building idle)

2. **Input Availability**:
   - Missing inputs reduce or halt production
   - Ensure market has required goods
   - Trade routes must supply inputs

3. **Production Method**:
   - Different methods have different efficiency
   - Upgrade methods through advances
   - Balance input costs vs. output value

4. **Location Development**:
   - Higher development improves production
   - Infrastructure buildings boost local efficiency
   - Provincial modifiers apply

### Profitability

#### Profitability Formula

Output Value - Input Costs - Labor Costs

Buildings are profitable when:

- Output goods value exceeds input costs
- Market prices favor production
- Efficient staffing levels maintained

Unprofitable buildings:

- Begin firing workers
- Should be given subsidies or closed
- May need production method change

## Resource Production (RGOs)

Resource Gathering Operations (RGOs) produce raw materials:

### RGO Types

- **Agricultural**: Food, livestock, textiles
- **Mining**: Metals, minerals, precious materials
- **Forestry**: Wood, naval supplies
- **Fishing**: Food from coastal areas

### RGO Mechanics

- Produce goods based on terrain and location
- Limited by local workforce
- Can be improved through:
  - Development investment
  - Technology advances
  - Infrastructure buildings

## Infrastructure Buildings

Infrastructure buildings don't produce goods directly but provide bonuses:

### Types of Infrastructure

- **Roads**: Reduce movement penalties, improve trade
- **Ports**: Enable naval construction, improve trade range
- **Marketplaces**: Increase market capacity (critical for trade)
- **Administration**: Improve local efficiency

### Infrastructure Strategy

**Priority**: Infrastructure should be built **before** production buildings:

- Marketplaces enable trade capacity for imports/exports
- Roads improve army movement and trade
- Ports essential for naval nations
- Administration improves all local production

## Strategic Considerations

### Early Game

1. Focus on **Food and Housing** first
2. Build **Marketplaces** in trade hubs early
3. Ensure population growth before expanding production
4. Don't overbuild—match buildings to available workforce

### Mid Game

1. Expand building capacity through development
2. Upgrade production methods as advances unlock
3. Build infrastructure to support larger economy
4. Balance estate construction with player needs

### Late Game

1. Maximize efficiency with advanced production methods
2. Automate routine construction
3. Focus on high-value goods production
4. Maintain sufficient capacity for continued expansion

### Common Pitfalls

1. **Overbuilding**: More buildings than workers to staff them
2. **Ignoring Inputs**: Building production without securing input supplies
3. **Neglecting Infrastructure**: Production buildings without supporting

   infrastructure

4. **Exceeding Capacity**: Building beyond location capacity, increasing costs
5. **Wrong Employment System**: Using system that doesn't match your economic

   strategy

## Automation Best Practices

- Set reasonable gold thresholds to avoid overspending
- Monitor estate construction to prevent conflicts
- Use infrastructure-first employment for development
- Switch to most-profitable-first for established economies
- Review automated decisions periodically

## References

[1] [Building - Europa Universalis 5
Wiki](https://eu5.paradoxwikis.com/Building)
[2] [Common Buildings - Europa Universalis 5
Wiki](https://eu5.paradoxwikis.com/Common_buildings)
