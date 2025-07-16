import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException
from crafting_library import CRAFTING_RECIPES

# --- Configuration ---
GAME_URL = "https://neal.fun/infinite-craft/"

# --- Goals ---
GOALS = {
    "Agriculture": ["Plant", "Farm", "Tractor"],
    "Mechanical": ["Metal", "Engine", "Car", "Plane"],
    "Political": ["Human", "Village", "City", "Country"],
    "Infinite": ["Infinity"]
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
        # Sort elements by their text content
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
        clear_button = driver.find_element(By.ID, "clear-button")
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

# --- AI-Driven Combination Logic ---
def choose_next_combination(elements, crafted_combinations, known_recipes, goals):
    """
    AI-powered function to decide the next best combination to try.
    It prioritizes goals, then known recipes, and finally explores new combinations.
    """
    element_map = {el.text: el for el in elements if el.text}
    current_element_texts = set(element_map.keys())

    # 1. Prioritize Goals
    for category, goal_items in goals.items():
        for goal_item in goal_items:
            if goal_item not in current_element_texts:
                # Find a recipe to craft the goal item
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

    return None, None

# --- Main Automation Logic ---
def automate_infinite_craft():
    """Main function to automate Infinite Craft."""
    driver = setup_driver()
    if not driver:
        return

    if not navigate_to_game(driver, GAME_URL):
        return

    try:
        crafted_combinations = set()
        for combo_tuple in CRAFTING_RECIPES.keys():
            crafted_combinations.add(tuple(sorted(combo_tuple)))

        newly_discovered_items = set(['Water', 'Fire', 'Wind', 'Earth'])

        while True:
            elements = get_craftable_elements(driver)
            if not elements:
                print("No elements to craft with. Waiting...")
                time.sleep(5)
                driver.refresh()
                continue

            current_element_texts_before_craft = {el.text for el in elements if el.text}

            element1, element2 = choose_next_combination(elements, crafted_combinations, CRAFTING_RECIPES, GOALS)

            if not element1 or not element2:
                print("\nNo new combinations to try. Stopping.")
                break

            combination = tuple(sorted((element1.text, element2.text)))
            crafted_combinations.add(combination)

            print(f"\nAttempting combination: {element1.text} + {element2.text}")
            if perform_drag_and_drop(driver, element1, element2):
                time.sleep(1)

                updated_elements = get_craftable_elements(driver)
                current_element_texts_after_craft = {el.text for el in updated_elements if el.text}

                new_items = current_element_texts_after_craft - current_element_texts_before_craft
                if new_items:
                    for item in new_items:
                        if item not in newly_discovered_items:
                            newly_discovered_items.add(item)
                            print(f"*** NEW ITEM DISCOVERED: {item} *** Total unique items: {len(newly_discovered_items)}")
                else:
                    print("No new element detected from this combination.")

                clear_screen(driver)
                time.sleep(1)

            print(f"\nFinished one cycle. Total unique items discovered so far: {len(newly_discovered_items)}")
            print("AI is choosing the next combination...")
            time.sleep(2)

    except KeyboardInterrupt:
        print("\nAutomation stopped by user.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        if driver:
            print("Closing WebDriver.")
            driver.quit()

if __name__ == "__main__":
    automate_infinite_craft()