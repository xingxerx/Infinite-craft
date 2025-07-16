# Infinite Craft Automation Script

This project is an automation script for the web game [Infinite Craft](https://neal.fun/infinite-craft/). It uses Selenium to simulate user interactions and a simple AI to decide which elements to combine.

## Features

*   **Automated Crafting**: The script automatically combines elements to discover new ones.
*   **AI-Driven Logic**: A simple AI decides the next combination to try, prioritizing known recipes and then exploring new ones.
*   **Goal-Oriented**: The AI can be given a set of goals to achieve, such as crafting specific items.
*   **Smart Memory**: The script remembers all combinations it has tried to avoid repetition.
*   **Alphabetical Ordering**: The list of available elements is sorted alphabetically for easy tracking.
*   **Search Functionality**: The script can search for specific elements.

## How It Works

The script uses the Selenium library to control a web browser and interact with the game. It finds the craftable elements on the page, and then uses a set of rules to decide which two elements to combine. The script prioritizes goals, then known recipes, and finally explores new combinations.

## Getting Started

### Prerequisites

*   Python 3.6 or higher
*   Google Chrome

### Installation

1.  Clone the repository:

    ```
    git clone https://github.com/xingxerx/Infinite-craft.git
    ```

2.  Install the required packages:

    ```
    pip install -r requirements.txt
    ```

### Usage

1.  Run the script:

    ```
    python "Infinite Craft Automation Script (Conceptual).py"
    ```

2.  The script will open a new Chrome window and navigate to the game. It will then start combining elements automatically.

## Configuration

*   **Goals**: You can add new goals to the `GOALS` dictionary in the script. The AI will prioritize crafting the items in these goals.
*   **Crafting Recipes**: You can add new recipes to the `CRAFTING_RECIPES` dictionary in `crafting_library.py`.

## Disclaimer

This script is for educational purposes only. The use of automation scripts may be against the terms of service of the game.
