import time
import json
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException

# --- Configuration ---
GAME_URL = "https://neal.fun/infinite-craft/"
GAME_STATE_FILE = "game_state.json"
CRAFTING_LIBRARY_FILE = "crafting_library.json"

# --- Goals and Rewards ---
GOALS = {
    "Agriculture": ["Plant", "Farm", "Tractor"],
    "Mechanical": ["Metal", "Engine", "Car", "Plane"],
    "Political": ["Human", "Village", "City", "Country"],
    "Infinite": ["Infinity"]
}
REWARDS = {
    "new_item": 1,
    "goal_item": 10
}

# --- WebDriver Setup ---
def setup_driver():
    """Sets up and returns a Chrome WebDriver instance."""
    try:
        service = ChromeService(ChromeDriverManager().install())
        options = webdriver.ChromeOptions()
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--log-level=3")
        driver = webdriver.Chrome(service=service, options=options)
        driver.set_page_load_timeout(30)
        print("WebDriver setup successful.")
        return driver
    except WebDriverException as e:
        print(f"Error setting up WebDriver: {e}")
        return None

# --- Game State and Library Functions ---
def save_game_state(discovered_items, crafted_combinations, crafting_recipes):
    """Saves the game state and crafting library to files."""
    with open(GAME_STATE_FILE, "w") as f:
        json.dump({
            "discovered_items": list(discovered_items),
            "crafted_combinations": [list(c) for c in crafted_combinations]
        }, f)
    with open(CRAFTING_LIBRARY_FILE, "w") as f:
        # Convert tuple keys to strings for JSON compatibility
        string_keyed_recipes = {f"{k[0]},{k[1]}": v for k, v in crafting_recipes.items()}
        json.dump(string_keyed_recipes, f)
    print("Game state and crafting library saved.")

def load_game_state():
    """Loads the game state and crafting library from files."""
    try:
        with open(GAME_STATE_FILE, "r") as f:
            state = json.load(f)
            discovered_items = set(state["discovered_items"])
            crafted_combinations = set(tuple(c) for c in state["crafted_combinations"])
    except FileNotFoundError:
        discovered_items = set(['Water', 'Fire', 'Wind', 'Earth'])
        crafted_combinations = set()

    try:
        with open(CRAFTING_LIBRARY_FILE, "r") as f:
            string_keyed_recipes = json.load(f)
            crafting_recipes = {tuple(k.split(',')): v for k, v in string_keyed_recipes.items()}
    except FileNotFoundError:
        crafting_recipes = {}

    return discovered_items, crafted_combinations, crafting_recipes

# --- Game Interaction Functions ---
def navigate_to_game(driver, url):
    """Navigates the WebDriver to the specified game URL."""
    try:
        driver.get(url)
        print(f"Navigated to: {url}")
        time.sleep(3)
        return True
    except TimeoutException:
        print(f"Page load timed out for {url}")
        driver.quit()
        return False
    except Exception as e:
        print(f"Error navigating to game: {e}")
        driver.quit()
        return False
    return True

def get_craftable_elements(driver):
    """Finds and returns a list of web elements representing craftable items, sorted alphabetically."""
    try:
        items = driver.find_elements(By.CSS_SELECTOR, ".item")
        if not items:
            print("No craftable elements found. Check your selector.")
        return sorted(items, key=lambda x: x.text)
    except NoSuchElementException:
        print("Could not find elements with the specified selector.")
        return []
    except Exception as e:
        print(f"Error getting craftable elements: {e}")
        return []

def search_element(driver, element_text):
    """Searches for an element with the given text."""
    try:
        elements = get_craftable_elements(driver)
        for element in elements:
            if element.text == element_text:
                return element
        return None
    except Exception as e:
        print(f"Error searching for element: {e}")
        return None

def perform_drag_and_drop(driver, element1, element2):
    """Performs a drag-and-drop action from element1 to element2."""
    try:
        actions = ActionChains(driver)
        actions.drag_and_drop(element1, element2).perform()
        print(f"Attempted to combine {element1.text} and {element2.text}.")
        time.sleep(2)
        return True
    except Exception as e:
        print(f"Error during drag and drop: {e}")
        return False

def clear_screen(driver):
    """Clears the screen of crafted items."""
    try:
        clear_button = driver.find_element(By.XPATH, "//div[contains(text(), 'Clear')]")
        clear_button.click()
        print("Screen cleared.")
        time.sleep(1)
        return True
    except NoSuchElementException:
        print("Clear button not found.")
        return False
    except Exception as e:
        print(f"Error clearing screen: {e}")
        return False

def get_new_element_text(driver):
    """Attempts to find and return the text of the newly created element."""
    try:
        new_element_display = driver.find_element(By.CSS_SELECTOR, ".instance-discovered-text")
        return new_element_display.text
    except NoSuchElementException:
        return None
    except Exception as e:
        return None

# --- AI-Driven Combination Logic ---
def choose_next_combination(elements, crafted_combinations, known_recipes, goals):
    """Decides the next best combination to try, prioritizing goals and known recipes."""
    element_map = {el.text: el for el in elements if el.text}
    current_element_texts = set(element_map.keys())

    # 1. Prioritize Goals
    for category, goal_items in goals.items():
        for goal_item in goal_items:
            if goal_item not in current_element_texts:
                for (item1, item2), result in known_recipes.items():
                    if result == goal_item:
                        if item1 in current_element_texts and item2 in current_element_texts:
                            combination = tuple(sorted((item1, item2)))
                            if combination not in crafted_combinations:
                                print(f"AI Strategy: Targeting goal '{goal_item}' from category '{category}'")
                                return element_map[item1], element_map[item2]

    # 2. Prioritize known recipes that create something new
    for (item1, item2), result in known_recipes.items():
        combination = tuple(sorted((item1, item2)))
        if item1 in current_element_texts and item2 in current_element_texts:
            if combination not in crafted_combinations:
                print(f"AI Strategy: Targeting known recipe: {item1} + {item2} -> {result}")
                return element_map[item1], element_map[item2]

    # 3. Fallback: Systematically try new combinations
    for i in range(len(elements)):
        for j in range(i, len(elements)):
            element1 = elements[i]
            element2 = elements[j]

            if not hasattr(element1, 'text') or not hasattr(element2, 'text') or not element1.text or not element2.text:
                continue

            combination = tuple(sorted((element1.text, element2.text)))
            if combination not in crafted_combinations:
                return element1, element2

    # 4. If all else fails, try a random combination
    print("AI Strategy: Trying a random combination.")
    element1 = random.choice(elements)
    element2 = random.choice(elements)
    return element1, element2

# --- Main Automation Logic ---
def automate_infinite_craft():
    """Main function to automate Infinite Craft."""
    driver = setup_driver()
    if not driver:
        return

    if not navigate_to_game(driver, GAME_URL):
        return

    newly_discovered_items, crafted_combinations, crafting_recipes = load_game_state()
    total_reward = 0

    try:
        while True:
            elements = get_craftable_elements(driver)
            if not elements:
                print("No elements to craft with. Refreshing...")
                driver.refresh()
                continue

            element1, element2 = choose_next_combination(elements, crafted_combinations, crafting_recipes, GOALS)

            if not element1 or not element2:
                print("\nNo new combinations to try. Stopping.")
                break

            combination = tuple(sorted((element1.text, element2.text)))
            crafted_combinations.add(combination)

            print(f"\nAttempting combination: {element1.text} + {element2.text}")
            if perform_drag_and_drop(driver, element1, element2):
                time.sleep(1)

                new_item_text = get_new_element_text(driver)
                if new_item_text and new_item_text not in newly_discovered_items:
                    newly_discovered_items.add(new_item_text)
                    crafting_recipes[combination] = new_item_text
                    total_reward += REWARDS["new_item"]
                    print(f"*** NEW ITEM DISCOVERED: {new_item_text} (Reward: {REWARDS['new_item']}) ***")

                    # Check if the new item is a goal item
                    for category, goal_items in GOALS.items():
                        if new_item_text in goal_items:
                            total_reward += REWARDS["goal_item"]
                            print(f"*** GOAL ACHIEVED: '{new_item_text}' in category '{category}' (Reward: {REWARDS['goal_item']}) ***")
                else:
                    print("No new element detected from this combination.")

                clear_screen(driver)
                time.sleep(1)

            print(f"\nFinished one cycle. Total unique items: {len(newly_discovered_items)}. Total reward: {total_reward}")
            print("AI is choosing the next combination...")
            time.sleep(2)

    except KeyboardInterrupt:
        print("\nAutomation stopped by user.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        if driver:
            save_game_state(newly_discovered_items, crafted_combinations, crafting_recipes)
            print("Closing WebDriver.")
            driver.quit()

if __name__ == "__main__":
    automate_infinite_craft()