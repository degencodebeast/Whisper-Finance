# Enigma Protocol x Bonkathon

Video Demo - [Demo video](https://www.loom.com/share/38af2c5c8a8e46c29e16e316099dcee1) <br />
Live Link - [Whisper Finance dapp]() <br />
Pitch Deck - [Figma slides]() <br/>

## ✨ Description

[Whisper Finance]() is an algorithmic trading protocol for solana. It brings professional-grade quant finance trading algorithms and tools to retail on Solana. It trades on most popular solana DEXes, but currently just on Drift protocol. We employed active yield vaults where users can pool in their USDC, BONK into the vault pools, and earn real yield from our algorithmic strategies which are connected to these vaults and running 24/7 under close monitoring.

## Inspiration
97% of traders are not profitable, the market is so efficient that the only way you can be profitable is if you find your edge, that's why all the hedge funds and wall street employ quantitative methods so they can beat the market and they are so secretive about their alpha. We thought about coming up with our own edge with automation and coming up with quantitative methods to build strategies that would otherwise have been impossible to implement without automation to build out our edge and then allow retail to enjoy the profits from the institutional quantitative trading methods from our platform.

## What it does
Whisper Finance enables Drift Protocol based investment vaults that trade on Solana using custom made algorithmic trading strategies.

We deployed our strategies using Drift Protocols vaults, allowing our strategies to be investable to any DeFi user with a profit-sharing fee model.

The DeFi user can invest in the strategies on our vaults using a familiar yield farming user interface directly from their wallet depositing USDC or BONK.


## How we built it

We wrote our trading strategies using `Python` and backtested them with the `Backtesting.py` library with some historical data. We also used trading and data analysis libraries like `pandas-ta`, `pandas` etc.

We wrote our bots then connected it to our Drift protocol based vaults that trade on the Drift Protocol DEX. We are currently running three different strategies on our vaults at the moment: 

1. The Drifting Tiger Vault - which trades the supply and demand zone strategy which trades the SOL-USD perpetual pair. Users deposit USDC into this vault.

2. The Bonking Dragon Vault - which trades the bollinger band + EMA strategy for the 1MBONK perpetual pair. Users deposit can deposit BONK or USDC into this vault. If users deposit BONK into the vault our bot borrows USDC on their behalf and trades with it, in a bull market they earn as their BONK appreciates in value and earn from from the vault's profits as well.

3. The Double Boost Vault - which trades a funding rate based strategy on any pair we input, this strategy is very flexible as we can aim to improve it to even perform funding rate arbitrage between different pairs funding rates. Users deposit USDC into this vault.

## Where we deployed to/contract details

We created and deployed our different vaults on the Solana Devnet Chain.

1. Drifting Tiger Vault - HrAuKuC8KuhqRcdmUu3WhSrNFv4HaV6XtqCdashhVH1A

2. Bonking Dragon - 5QAPFbeAHtgb8LkbDBMSyaAmwtQRufWceQLLaxdSse6M

3. Double Boost - 4K1s2DtLXrYXVMYShDdLLWTLezpyTBKpTFz2DEpt8QkF

## Installation

To install this project:

### Prerequisites

- [Conda](https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html) must be installed.

### Steps

1. **Clone the Repository**

   Clone the project repository from GitHub:

   ```
   git clone https://github.com/enigma-xyz/enigma_protocol
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