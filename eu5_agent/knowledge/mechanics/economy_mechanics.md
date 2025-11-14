# EU5 Economy Mechanics

This document provides a comprehensive overview of the economy in Europa Universalis 5, based on information from the official Paradox Wiki. [1]

## Gold (Ducats)

Gold, or Ducats, represents the liquid wealth of a nation and is the primary currency for most in-game transactions. It is spent on a wide range of activities, from constructing buildings to maintaining armies. The flow of gold is primarily driven by market activities, with various sources of income and expenses.

| Sources of Income          | Sources of Expenses              |
| -------------------------- | -------------------------------- |
| Minting                    | Cost of the Court                |
| Estate Tax                 | Army Maintenance                 |
| Trade Income               | Navy Maintenance                 |
| Selling Food               | Fort Maintenance (min 50%)       |
| Foreign Buildings          | Cost of Colonies                 |
| Mercenary Income           | Diplomatic Spending              |
| Positive Diplomatic Deals  | Stability Spending               |
| Interest from Lent Gold    | Exploration Cost                 |
|                            | Building Subsidies               |
|                            | Mercenary Paying                 |
|                            | Negative Diplomatic Deals        |
|                            | Interest from Borrowed Gold      |

### Taxation

Each location possesses a tax base, which is calculated from the combined profits of its Resource Gathering Operations (R.G.O.s) and buildings that sell goods to the market, along with Burgher activities. This is then multiplied by the control percentage in the location. The tax base is distributed among the estates of its populations based on their relative population size. Each estate then contributes a portion of this tax to the state, determined by the tax rate imposed upon it. Estate taxation can be automated to maintain a 50% satisfaction equilibrium.

### Minting and Inflation

Minting is a primary method for generating ducats, with a scale ranging from 0% to 25% of the country's tax base. This action increases the demand for Gold and Silver in the capital's market by an equivalent amount. Every country has a minting threshold, which starts at 5%. Minting above this threshold will lead to inflation.

Inflation represents a general increase in prices across the game. It naturally decreases by **-0.1%** each month but is increased by **+0.005** for each 1% of minting above the threshold. Inflation can also be actively reduced through a Cabinet Action.

### Expected Expenses

Countries are expected to cover three main expenses, with payment levels ranging from 0% to 100%. While optional, funding these expenses provides significant bonuses. The cost of these expenses scales with the country's tax base.

| Expense                | % of Tax Base | Effect per 1% Paid                                                                                                                            |
| ---------------------- | ------------- | --------------------------------------------------------------------------------------------------------------------------------------------- |
| **Cost of the Court**    | 10%           | **+0.01** Monthly Government Power                                                                                                            |
| **Stability Investment** | 20%           | **+0.005** Monthly Stability                                                                                                                  |
| **Diplomatic Spending**  | 25%           | **+0.1** Loyalty of Subjects<br>**+0.5%** Diplomatic Capacity<br>**+0.02** Maximum Diplomats<br>**+0.004** Monthly Diplomats<br>**+0.001** Monthly Progress to Conciliatory |

### Maintenance

Armies, navies, and forts all incur monthly maintenance costs. While the default is full payment, these costs can be reduced, albeit with penalties. Reducing army or navy maintenance lowers their morale proportionally. Reducing fort maintenance results in the following penalties for each 1% reduction:

*   −0.0005 Monthly Prestige
*   −2% Fort Defense
*   −0.5% Garrison Size

### Loans and Bankruptcy

Loans provide an immediate influx of cash but must be repaid over 60 months with interest. The base interest rate is 10%, with a possible range of 1% to 25%. Loans can be taken from estates or from banking countries. If a country's treasury is negative at the end of the month, a loan is automatically taken. If no more loans can be taken, the country will declare bankruptcy.

Bankruptcy clears all loans and inflation but comes with severe penalties for 60 months, including a significant reduction in stability, building downgrades, and crippling effects on military morale, research, and economic capabilities.

## Stability

Stability reflects the internal peace of a country, ranging from **-100** to **+100**. It naturally trends towards 0. High stability provides bonuses to population promotion speed and estate satisfaction, while low stability increases the risk of rebellions and harms estate satisfaction.

## Prestige

Prestige represents a country's international standing, ranging from 0 to 100. High prestige offers bonuses to diplomatic reputation, market attraction, and cultural influence.

## Government Power

Government power, which varies by government type (e.g., Devotion for Theocracies, Horde Unity for Steppe Hordes), represents the efficiency of the government. It is spent on various actions and provides passive bonuses based on its level.

## References
[1] [Economy - Europa Universalis 5 Wiki](https://eu5.paradoxwikis.com/Economy)
