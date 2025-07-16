import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException
from crafting_library import CRAFTING_RECIPES

# --- Configuration ---
# Replace with the actual URL of Infinite Craft
# As of my last update, the game is typically found at:
# https://neal.fun/infinite-craft/
GAME_URL = "https://neal.fun/infinite-craft/"

# --- WebDriver Setup ---
def setup_driver():
    """Sets up and returns a Chrome WebDriver instance."""
    try:
        # Use ChromeDriverManager to automatically download and manage ChromeDriver
        service = ChromeService(ChromeDriverManager().install())
        options = webdriver.ChromeOptions()
        # Optional: Run in headless mode (without opening a visible browser window)
        # options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--log-level=3") # Suppress verbose logging

        driver = webdriver.Chrome(service=service, options=options)
        driver.set_page_load_timeout(30) # Set page load timeout
        print("WebDriver setup successful.")
        return driver
    except WebDriverException as e:
        print(f"Error setting up WebDriver: {e}")
        print("Please ensure Chrome is installed and try again.")
        print("If issues persist, try updating webdriver_manager or your Chrome browser.")
        return None

# --- Game Interaction Functions ---
def navigate_to_game(driver, url):
    """Navigates the WebDriver to the specified game URL."""
    try:
        driver.get(url)
        print(f"Navigated to: {url}")
        time.sleep(3) # Give time for the page to load
        # You might need to wait for specific elements to be present here
        # For example: WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "game-container")))
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
    """
    Finds and returns a list of web elements representing craftable items.
    You will need to inspect the Infinite Craft game page to find the correct
    CSS selector, class name, or XPath for the elements that represent items.

    Example: If items have a class 'item', you'd use By.CLASS_NAME, 'item'.
    If they are within a specific container, you might use a more specific CSS selector.
    """
    try:
        # !!! IMPORTANT: You need to find the correct selector for items !!!
        # Open Infinite Craft in your browser, right-click an item, and select "Inspect".
        # Look for a common class name or data attribute.
        # Example (replace with actual):
        items = driver.find_elements(By.CSS_SELECTOR, ".item") # Common class for items
        # Or if they are divs inside a specific container:
        # items = driver.find_elements(By.XPATH, "//div[@id='items-container']/div[contains(@class, 'item')]")
        # Or if they have a specific data attribute:
        # items = driver.find_elements(By.CSS_SELECTOR, "[data-type='element']")

        if not items:
            print("No craftable elements found. Check your selector.")
        return items
    except NoSuchElementException:
        print("Could not find elements with the specified selector. Check the game's HTML.")
        return []
    except Exception as e:
        print(f"Error getting craftable elements: {e}")
        return []

def perform_drag_and_drop(driver, element1, element2):
    """
    Performs a drag-and-drop action from element1 to element2.
    """
    try:
        actions = ActionChains(driver)
        # Drag element1 to element2
        actions.drag_and_drop(element1, element2).perform()
        print(f"Attempted to combine {element1.text if element1.text else 'Element 1'} and {element2.text if element2.text else 'Element 2'}.")
        time.sleep(2) # Give time for the combination to process and new element to appear
        return True
    except Exception as e:
        print(f"Error during drag and drop: {e}")
        return False

def clear_screen(driver):
    """
    Simulates clicking a 'clear' or 'reset' button if one exists.
    You'll need to find the actual locator for the clear button in Infinite Craft.
    If there's no direct clear button, this function might need to be more complex
    (e.g., deleting elements one by one if the game allows).
    """
    try:
        # !!! IMPORTANT: Find the correct selector for the clear button !!!
        # Example:
        clear_button = driver.find_element(By.ID, "clear-button") # Or By.CLASS_NAME, By.XPATH etc.
        # If there's no clear button, you might need to refresh the page:
        # driver.refresh()
        clear_button.click()
        print("Screen cleared (simulated).")
        time.sleep(1) # Give time for the screen to clear
        return True
    except NoSuchElementException:
        print("Clear button not found. Skipping clear screen action.")
        # If no clear button, you might need to refresh the page or handle it differently
        # driver.refresh()
        # time.sleep(3)
        return False
    except Exception as e:
        print(f"Error clearing screen: {e}")
        return False

def get_new_element_text(driver):
    """
    Attempts to find and return the text of the newly created element.
    This is highly dependent on how Infinite Craft displays new elements.
    You'll need to inspect the game to find the correct locator for the new element display.
    """
    try:
        # !!! IMPORTANT: Find the correct selector for the new element display !!!
        # Example: a div that shows the last created item
        new_element_display = driver.find_element(By.CSS_SELECTOR, ".new-item-notification")
        return new_element_display.text
    except NoSuchElementException:
        # print("New element display not found.")
        return "Unknown New Element"
    except Exception as e:
        # print(f"Error getting new element text: {e}")
        return "Error getting New Element"

# --- AI-Driven Combination Logic ---
def choose_next_combination(elements, crafted_combinations, known_recipes):
    """
    AI-powered function to decide the next best combination to try.
    It prioritizes known recipes that can be crafted with the current elements.
    If no known recipes are available, it falls back to systematic exploration.
    """
    element_map = {el.text: el for el in elements if el.text}
    current_element_texts = set(element_map.keys())

    # 1. Prioritize known recipes that create something new
    for (item1, item2), result in known_recipes.items():
        combination = tuple(sorted((item1, item2)))
        if item1 in current_element_texts and item2 in current_element_texts:
            if combination not in crafted_combinations:
                print(f"AI Strategy: Targeting known recipe: {item1} + {item2} -> {result}")
                return element_map[item1], element_map[item2]

    # 2. Fallback: Systematically try new combinations
    for i in range(len(elements)):
        for j in range(i, len(elements)):
            element1 = elements[i]
            element2 = elements[j]

            # Ensure elements are valid
            if not hasattr(element1, 'text') or not hasattr(element2, 'text') or not element1.text or not element2.text:
                continue

            combination = tuple(sorted((element1.text, element2.text)))
            if combination not in crafted_combinations:
                return element1, element2 # Return the first new combination found

    return None, None # No new combinations to try


# --- Main Automation Logic ---
def automate_infinite_craft():
    """Main function to automate Infinite Craft."""
    driver = setup_driver()
    if not driver:
        return

    if not navigate_to_game(driver, GAME_URL):
        return

    try:
        crafted_combinations = set() # To store unique combinations to avoid repetition
        # Pre-populate with known combinations from the library to avoid re-trying them if they don't yield a new result
        for combo_tuple in CRAFTING_RECIPES.keys():
            crafted_combinations.add(tuple(sorted(combo_tuple)))

        newly_discovered_items = set(['Water', 'Fire', 'Wind', 'Earth']) # Initial elements

        while True:
            elements = get_craftable_elements(driver)
            if not elements:
                print("No elements to craft with. Waiting or restarting...")
                time.sleep(5)
                driver.refresh() # Try refreshing if no elements
                continue

            current_element_texts_before_craft = {el.text for el in elements if el.text}

            # AI selects the next combination
            element1, element2 = choose_next_combination(elements, crafted_combinations, CRAFTING_RECIPES)

            if not element1 or not element2:
                print("\nNo new combinations to try with the current elements. Stopping.")
                break # Exit the loop if no new combinations are found

            # Create a canonical representation of the combination to mark it as tried
            combination = tuple(sorted((element1.text, element2.text)))
            crafted_combinations.add(combination)

            print(f"\nAttempting combination: {element1.text} + {element2.text}")
            if perform_drag_and_drop(driver, element1, element2):
                time.sleep(1) # Small pause for UI to update

                # Re-fetch elements to see if a new one appeared
                updated_elements = get_craftable_elements(driver)
                current_element_texts_after_craft = {el.text for el in updated_elements if el.text}

                new_items = current_element_texts_after_craft - current_element_texts_before_craft
                if new_items:
                    for item in new_items:
                        if item not in newly_discovered_items:
                            newly_discovered_items.add(item)
                            print(f"*** NEW ITEM DISCOVERED: {item} *** Total unique items: {len(newly_discovered_items)}")
                            # Optional: Add to a temporary session library
                            # CRAFTING_RECIPES[combination] = item
                else:
                    # If no new item detected, maybe it was a known combination that didn't produce a new element on screen
                    # Or it was an unknown combination that yielded a duplicate
                    print("No new element detected from this combination.")


                # Clear the screen to prevent performance issues
                clear_screen(driver)
                # A short pause after clearing might be needed
                time.sleep(1)


            print(f"\nFinished one cycle. Total unique items discovered so far: {len(newly_discovered_items)}")
            print("AI is choosing the next combination...")
            time.sleep(2) # Pause before starting next cycle

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
