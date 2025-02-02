# Bitcoin Trading Evolution Simulator 🧠💰

A genetic algorithm-powered simulation where neural network traders evolve to maximize profits in Bitcoin markets.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Features 🌟

- **Evolutionary Strategy**: Genetic algorithm with:
  - Tournament selection 🏆
  - Adaptive mutation rates 🧬
  - Neural network architecture evolution 🧠
- **Market Realism**:
  - Cyclical date encoding 📅
  - Fear & Greed Index integration 😨💰
  - Historical price dynamics 📈
- **Visual Intelligence**:
  - Real-time performance dashboards 📊
  - Trading action heatmaps 🔥
  - Strategy diversity radar charts 🌐
- **Enterprise-Grade**:
  - Multi-generation persistence 💾
  - Configurable hyperparameters ⚙️
  - Non-blocking visualization 🖥️

## Installation 🛠️

**Requirements**:
- Python 3.8+
- ```bash
  pip install numpy pandas matplotlib plotly



## Usage 🚀
### New Simulation:
python3 main.py new -d simulation/bitcoin_normalized.csv -s 2018-02-01 -e 2022-02-01 -sd simulation -p 200 -sr 0.15 -si 10

### New Simulation:
python main.py load simulations
## Run the Script

#### 1 New Simulation:
example 
python3 main.py new -d simulation/bitcoin_normalized.csv -s 2018-02-01 -e 2022-02-01 -sd simulation -p 200 -sr 0.15 -si 10

#### 2 Load started Simulation:
python3 main.py load SIMULATION_FOLDER