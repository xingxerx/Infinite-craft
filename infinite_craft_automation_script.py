import time
import json
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

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
            "crafted_combinations": [list(combo) for combo in crafted_combinations]
        }, f)
    
    with open(CRAFTING_LIBRARY_FILE, "w") as f:
        # Convert tuple keys to strings for JSON compatibility
        string_keyed_recipes = {f"{k[0]},{k[1]}": v for k, v in crafting_recipes.items()}
        json.dump(string_keyed_recipes, f)
    print("Game state and crafting library saved.")

def load_game_state():
    """Loads the game state and crafting library from files."""
    discovered_items = set()
    crafted_combinations = set()
    crafting_recipes = {}
    
    try:
        with open(GAME_STATE_FILE, "r") as f:
            data = json.load(f)
            discovered_items = set(data.get("discovered_items", []))
            crafted_combinations = set(tuple(combo) for combo in data.get("crafted_combinations", []))
    except FileNotFoundError:
        print("No previous game state found. Starting fresh.")
    
    try:
        with open(CRAFTING_LIBRARY_FILE, "r") as f:
            string_keyed_recipes = json.load(f)
            # Convert string keys back to tuples
            crafting_recipes = {tuple(k.split(",")): v for k, v in string_keyed_recipes.items()}
    except FileNotFoundError:
        print("No previous crafting library found. Starting fresh.")
    
    return discovered_items, crafted_combinations, crafting_recipes

# --- Game Navigation ---
def navigate_to_game(driver, url):
    """Navigates to the game URL and waits for initial elements to load."""
    try:
        driver.get(url)
        print(f"Navigated to: {url}")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".item")))
        return True
    except TimeoutException:
        print(f"Page load timed out or initial elements not found for {url}")
        driver.quit()
        return False
    except Exception as e:
        print(f"Error navigating to game: {e}")
        driver.quit()
        return False

# --- Element Interaction ---
def get_craftable_elements(driver):
    """Gets all craftable elements currently visible on the screen."""
    try:
        # Wait for elements to be present
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".item"))
        )

        # Get all elements and filter out any that might be in the sidebar
        all_elements = driver.find_elements(By.CSS_SELECTOR, ".item")

        # Filter to only get draggable items (not in sidebar)
        craftable_elements = []
        for element in all_elements:
            try:
                # Check if element is visible and has text
                if element.is_displayed() and element.text.strip():
                    # Check if it's not in the sidebar (sidebar items usually have different classes)
                    parent_classes = element.find_element(By.XPATH, "..").get_attribute("class") or ""
                    if "sidebar" not in parent_classes.lower():
                        craftable_elements.append(element)
            except Exception:
                continue

        print(f"Found {len(craftable_elements)} craftable elements")
        return craftable_elements

    except TimeoutException:
        print("Timed out waiting for craftable elements.")
        return []
    except NoSuchElementException:
        print("No craftable elements found.")
        return []
    except Exception as e:
        print(f"Error getting craftable elements: {e}")
        return []

def search_for_element(driver, element_name):
    """Searches for a specific element by name."""
    try:
        elements = get_craftable_elements(driver)
        for element in elements:
            if element.text.strip() == element_name:
                return element
        return None
    except Exception as e:
        print(f"Error searching for element: {e}")
        return None

def perform_drag_and_drop(driver, element1, element2):
    """Performs a drag-and-drop operation between two elements with improved reliability."""
    try:
        # Ensure elements are visible and interactable
        driver.execute_script("arguments[0].scrollIntoView(true);", element1)
        driver.execute_script("arguments[0].scrollIntoView(true);", element2)

        # Wait for elements to be stable
        time.sleep(0.2)

        # Try multiple drag-and-drop methods for better reliability
        actions = ActionChains(driver)

        # Method 1: Standard drag and drop
        try:
            actions.drag_and_drop(element1, element2).perform()
            print(f"Attempted to combine {element1.text} and {element2.text} (Method 1: drag_and_drop)")
        except Exception as e1:
            print(f"Method 1 failed: {e1}")

            # Method 2: Click and hold, move to target, release
            try:
                actions = ActionChains(driver)
                actions.click_and_hold(element1).move_to_element(element2).release().perform()
                print(f"Attempted to combine {element1.text} and {element2.text} (Method 2: click_and_hold)")
            except Exception as e2:
                print(f"Method 2 failed: {e2}")

                # Method 3: Manual coordinate-based drag
                try:
                    actions = ActionChains(driver)
                    source_location = element1.location
                    target_location = element2.location

                    actions.move_to_element(element1).click_and_hold()
                    actions.move_by_offset(
                        target_location['x'] - source_location['x'],
                        target_location['y'] - source_location['y']
                    ).release().perform()
                    print(f"Attempted to combine {element1.text} and {element2.text} (Method 3: coordinate-based)")
                except Exception as e3:
                    print(f"Method 3 failed: {e3}")
                    return False

        # Wait longer for the animation and new element creation
        time.sleep(1.5)
        return True

    except Exception as e:
        print(f"Error during drag and drop: {e}")
        return False

def clear_screen(driver):
    """Clears the screen by removing all items except the basic four."""
    try:
        # Find the reset button or clear mechanism
        reset_button = driver.find_element(By.CSS_SELECTOR, ".reset")
        if reset_button:
            reset_button.click()
            time.sleep(2)  # Wait for the screen to clear
            return True
        else:
            # Alternative: manually remove items
            items = driver.find_elements(By.CSS_SELECTOR, ".item")
            basic_items = ["🔥 Fire", "💧 Water", "🌍 Earth", "🌬️ Wind"]
            for item in items:
                if item.text not in basic_items:
                    # Try to remove the item (this might vary based on the game's UI)
                    try:
                        item.click()  # Or some other removal action
                    except:
                        pass
            return True
    except NoSuchElementException:
        print("Reset button not found. Screen might already be clear.")
        return False
    except Exception as e:
        print(f"Error clearing screen: {e}")
        return False

def get_new_element_text(driver, previous_elements):
    """Detects and returns the text of any new element that appeared."""
    try:
        # Wait longer for new element to appear and animations to complete
        time.sleep(2)

        # Try multiple methods to detect new elements

        # Method 1: Check for new elements in the main area
        current_elements = get_craftable_elements(driver)
        current_texts = [elem.text for elem in current_elements]

        for text in current_texts:
            if text not in previous_elements:
                print(f"New element detected in main area: {text}")
                return text

        # Method 2: Check for discovery notification or popup
        try:
            # Look for discovery notification (common pattern in these games)
            discovery_selectors = [
                ".discovery",
                ".new-item",
                ".notification",
                "[class*='discover']",
                "[class*='new']"
            ]

            for selector in discovery_selectors:
                try:
                    discovery_element = driver.find_element(By.CSS_SELECTOR, selector)
                    if discovery_element.is_displayed() and discovery_element.text.strip():
                        discovered_text = discovery_element.text.strip()
                        print(f"New element detected via discovery notification: {discovered_text}")
                        return discovered_text
                except NoSuchElementException:
                    continue

        except Exception as discovery_error:
            print(f"Discovery notification check failed: {discovery_error}")

        # Method 3: Check sidebar for new items (if they appear there)
        try:
            sidebar_items = driver.find_elements(By.CSS_SELECTOR, ".sidebar .item, .items .item")
            sidebar_texts = [item.text.strip() for item in sidebar_items if item.text.strip()]

            for text in sidebar_texts:
                if text not in previous_elements:
                    print(f"New element detected in sidebar: {text}")
                    return text

        except Exception as sidebar_error:
            print(f"Sidebar check failed: {sidebar_error}")

        print("No new element detected")
        return None

    except Exception as e:
        print(f"Error getting new element text: {e}")
        return None

# --- AI Strategy ---
def choose_next_combination(elements, crafted_combinations, crafting_recipes, goals):
    """AI strategy to choose the next combination to try."""
    element_texts = [elem.text for elem in elements]
    element_map = {elem.text: elem for elem in elements}
    
    # 1. Prioritize combinations that lead to goal items
    for category, goal_items in goals.items():
        for goal_item in goal_items:
            for item1 in element_texts:
                for item2 in element_texts:
                    if item1 != item2:
                        combination = tuple(sorted((item1, item2)))
                        if combination in crafting_recipes and crafting_recipes[combination] == goal_item:
                            if combination not in crafted_combinations:
                                print(f"AI Strategy: Targeting goal '{goal_item}' from category '{category}'")
                                return element_map[item1], element_map[item2]

    # 2. Try known successful recipes that we haven't attempted yet
    for combination, result in crafting_recipes.items():
        item1, item2 = combination
        if item1 in element_texts and item2 in element_texts:
            if combination not in crafted_combinations:
                print(f"AI Strategy: Targeting known recipe: {item1} + {item2} -> {result}")
                return element_map[item1], element_map[item2]

    # 3. Try new combinations we haven't attempted
    for i in range(len(element_texts)):
        for j in range(i, len(element_texts)):
            item1_text = element_texts[i]
            item2_text = element_texts[j]

            combination = tuple(sorted((item1_text, item2_text)))
            if combination not in crafted_combinations:
                print(f"AI Strategy: Trying new combination: {item1_text} + {item2_text}")
                return element_map[item1_text], element_map[item2_text]

    # 4. If all else fails, try a random combination
    print("AI Strategy: Trying a random combination.")
    element1 = random.choice(elements)
    element2 = random.choice(elements)
    return element1, element2

# --- Main Automation Loop ---
def main():
    """Main automation function."""
    driver = setup_driver()
    if not driver:
        print("Failed to set up WebDriver. Exiting.")
        return

    try:
        if not navigate_to_game(driver, GAME_URL):
            return

        # Load previous game state
        discovered_items, crafted_combinations, crafting_recipes = load_game_state()
        
        total_reward = 0
        newly_discovered_items = set()

        print("Starting automation loop...")
        while True:
            elements = get_craftable_elements(driver)
            previous_element_texts = [elem.text for elem in elements]

            if not elements:
                print("No elements to craft with. Refreshing...")
                driver.refresh()
                time.sleep(5)
                continue

            element1, element2 = choose_next_combination(elements, crafted_combinations, crafting_recipes, GOALS)

            if not element1 or not element2:
                print("No new combinations to try. All known combinations have been attempted.")
                break

            combination = tuple(sorted((element1.text, element2.text)))

            print(f"Attempting combination: {element1.text} + {element2.text}")
            if perform_drag_and_drop(driver, element1, element2):
                crafted_combinations.add(combination)

                # Wait a moment for the new element to be created
                time.sleep(1)

                new_item_text = get_new_element_text(driver, previous_element_texts)
                if new_item_text and new_item_text not in discovered_items:
                    discovered_items.add(new_item_text)
                    newly_discovered_items.add(new_item_text)
                    crafting_recipes[combination] = new_item_text
                    total_reward += REWARDS["new_item"]
                    print(f"*** NEW ITEM DISCOVERED: {new_item_text} (Reward: {REWARDS['new_item']}) ***")

                    # Check if the new item is a goal item
                    for category, goal_items in GOALS.items():
                        if new_item_text in goal_items:
                            total_reward += REWARDS["goal_item"]
                            print(f"*** GOAL ACHIEVED: '{new_item_text}' in category '{category}' "
                                  f"(Reward: {REWARDS['goal_item']}) ***")
                elif new_item_text:
                    print(f"Combination created: {new_item_text} (already known)")
                else:
                    print("No new element detected from this combination.")

                # Save progress periodically
                save_game_state(discovered_items, crafted_combinations, crafting_recipes)

                # Brief pause before next action
                time.sleep(1)

            print(f"Finished one cycle. Total unique items: {len(newly_discovered_items)}. "
                  f"Total reward: {total_reward}")
            print("AI is choosing the next combination...")
            time.sleep(2)

    except KeyboardInterrupt:
        print("Automation stopped by user.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        if driver:
            save_game_state(discovered_items, crafted_combinations, crafting_recipes)
            print("Closing WebDriver.")
            driver.quit()

if __name__ == "__main__":
    main()
