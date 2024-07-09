# Whisper Finance x Onchain Summer Hackathon

Video Demo - [Demo video](https://vimeo.com/972667734?share=copy) <br />
Live Link - [Whisper Finance dapp](https://whisper-finance.vercel.app/) <br />
Pitch Deck - [Figma slides](https://www.figma.com/proto/8orfECSFwjVy1BYec0Sg79/Whisper-Finance?node-id=1-102&t=suSp8ZtLLfbwbPIb-1&scaling=contain&content-scaling=fixed&page-id=0%3A1) <br/>

## ✨ Description

[Whisper Finance](https://whisper-finance.vercel.app/) is an algorithmic trading protocol for Base. It brings professional-grade quant finance trading algorithms and tools to retail on Base. It trades on most popular Base DEXes, but currently just on Kwenta protocol. We employed active yield vaults where users can pool in their USDC, ETH into the vault pools, and earn real yield from our algorithmic strategies which are connected to these vaults and running 24/7 under close monitoring.

## Inspiration
97% of traders are not profitable, the market is so efficient that the only way you can be profitable is if you find your edge, that's why all the hedge funds and wall street employ quantitative methods so they can beat the market and they are so secretive about their alpha. We thought about coming up with our own edge with automation and coming up with quantitative methods to build strategies that would otherwise have been impossible to implement without automation to build out our edge and then allow retail to enjoy the profits from the institutional quantitative trading methods from our platform.

## What it does
Whisper Finance enables Kwenta Protocol based investment vaults that trade on Base using custom made algorithmic trading strategies.

We deployed our strategies using Kwenta Protocols vaults, allowing our strategies to be investable to any DeFi user with a profit-sharing fee model.

The DeFi user can invest in the strategies on our vaults using a familiar yield farming user interface directly from their wallet depositing USDC.


## How we built it

We wrote our trading strategies using `Python` and backtested them with the `Backtesting.py` library with some historical data. We also used trading and data analysis libraries like `pandas-ta`, `pandas` etc.

We wrote our bots then connected it to our Kwenta protocol based vaults that trade on the Kwenta Protocol DEX. We are currently running three different strategies on our vaults at the moment: 

1. The Kwenta Tiger Vault - which trades the supply and demand zone strategy which trades the SOL-USD perpetual pair. Users deposit USDC into this vault.

2. The Synthetix Dragon Vault - which trades the bollinger band + EMA strategy for the ETHUSDT perpetual pair. Users deposit can deposit USDC or ETH into this vault. If users deposit ETH into the vault our bot borrows USDC on their behalf and trades with it, in a bull market they earn as their ETH appreciates in value and earn from from the vault's profits as well.

3. The Double Boost Vault - which trades a funding rate based strategy on any pair we input, this strategy is very flexible as we can aim to improve it to even perform funding rate arbitrage betweenjj different pairs funding rates. Users deposit USDC into this vault.

## Where we deployed to/contract details

We created and deployed our different vaults on the Base Chain.

1. Kwenta Tiger Vault - 

2. Synthetix Dragon - 

3. Double Boost - 

## Installation

To install this project:

### Prerequisites

- [Conda](https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html) must be installed.

### Steps

1. **Clone the Repository**

   Clone the project repository from GitHub:

   ```
   git clone  https://github.com/degencodebeast/Whisper-Finance
   ```

2. **Navigate to the Project Directory**

    Change into the project directory:

     ```
   cd backend/src/trading_strategies
     ```
3. **Create the Conda Environment**

    Create a new Conda environment using the environment.yml file:
    ``` 
    conda env create -f environment.yml
    ```
    This will create a new Conda environment with all the dependencies specified in the `environment.yml` file.
4. **Activate the Conda Environment**

    Activate the newly created environment:
    ```
    conda activate your_environment_name
    ```
    Replace your_environment_name with the name of the environment specified in the environment.yml file.
5. **Run the Bot**

    You can run any of the bots as needed. For example:
    ```
    python supply_demand_bot.py
    ```
6. **Run the Backtest**

    You can also run any of the backtests as needed. You can change directory into the backtests directory and run a backtest like so:
    ```
    cd ../backtests
     
    python supply_demand_bt.py

    ```