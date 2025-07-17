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
    """Sets up and returns a Chrome WebDriver instance with optimized settings."""
    try:
        service = ChromeService(ChromeDriverManager().install())
        options = webdriver.ChromeOptions()

        # Basic stability options
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--log-level=3")

        # Additional options for better automation reliability
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-plugins")
        options.add_argument("--disable-images")  # Faster loading
        options.add_argument("--disable-javascript-harmony-shipping")
        options.add_argument("--disable-background-timer-throttling")
        options.add_argument("--disable-backgrounding-occluded-windows")
        options.add_argument("--disable-renderer-backgrounding")

        # Set user agent to avoid detection
        options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

        # Experimental options for better performance
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)

        driver = webdriver.Chrome(service=service, options=options)

        # Execute script to remove webdriver property
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        # Set timeouts
        driver.set_page_load_timeout(30)
        driver.implicitly_wait(5)

        # Maximize window for better element interaction
        driver.maximize_window()

        print("WebDriver setup successful with enhanced options.")
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
    """
    Performs drag-and-drop operation using the correct method for Infinite Craft.

    Based on analysis, Infinite Craft elements are not draggable by default,
    so we need to use JavaScript-based drag simulation or mouse events.
    """
    try:
        print(f"🎯 Attempting to combine {element1.text} and {element2.text}")

        # Ensure elements are visible
        driver.execute_script("arguments[0].scrollIntoView(true);", element1)
        driver.execute_script("arguments[0].scrollIntoView(true);", element2)
        time.sleep(0.3)

        # Method 1: JavaScript-based drag simulation (most reliable for this game)
        try:
            print("  📝 Using JavaScript drag simulation...")

            # JavaScript code to simulate HTML5 drag and drop
            js_drag_drop = """
            function simulateDragDrop(sourceNode, destinationNode) {
                var EVENT_TYPES = {
                    DRAG_END: 'dragend',
                    DRAG_ENTER: 'dragenter',
                    DRAG_EXIT: 'dragexit',
                    DRAG_LEAVE: 'dragleave',
                    DRAG_OVER: 'dragover',
                    DRAG_START: 'dragstart',
                    DROP: 'drop'
                };

                function createCustomEvent(type) {
                    var event = new CustomEvent("CustomEvent");
                    event.initCustomEvent(type, true, true, null);
                    event.dataTransfer = {
                        data: {},
                        setData: function(type, val) {
                            this.data[type] = val;
                        },
                        getData: function(type) {
                            return this.data[type];
                        }
                    };
                    return event;
                }

                function dispatchEvent(node, type, event) {
                    if (node.dispatchEvent) {
                        return node.dispatchEvent(event);
                    }
                    if (node.fireEvent) {
                        return node.fireEvent("on" + type, event);
                    }
                }

                var event = createCustomEvent(EVENT_TYPES.DRAG_START);
                dispatchEvent(sourceNode, EVENT_TYPES.DRAG_START, event);

                var dropEvent = createCustomEvent(EVENT_TYPES.DROP);
                dropEvent.dataTransfer = event.dataTransfer;
                dispatchEvent(destinationNode, EVENT_TYPES.DROP, dropEvent);

                var dragEndEvent = createCustomEvent(EVENT_TYPES.DRAG_END);
                dragEndEvent.dataTransfer = event.dataTransfer;
                dispatchEvent(sourceNode, EVENT_TYPES.DRAG_END, dragEndEvent);
            }

            simulateDragDrop(arguments[0], arguments[1]);
            """

            driver.execute_script(js_drag_drop, element1, element2)
            print("  ✅ JavaScript drag simulation completed")

        except Exception as js_error:
            print(f"  ❌ JavaScript method failed: {js_error}")

            # Method 2: Mouse event simulation
            try:
                print("  🖱️  Using mouse event simulation...")

                actions = ActionChains(driver)

                # Get element centers
                elem1_rect = driver.execute_script("""
                    var rect = arguments[0].getBoundingClientRect();
                    return {x: rect.left + rect.width/2, y: rect.top + rect.height/2};
                """, element1)

                elem2_rect = driver.execute_script("""
                    var rect = arguments[0].getBoundingClientRect();
                    return {x: rect.left + rect.width/2, y: rect.top + rect.height/2};
                """, element2)

                # Simulate mouse drag
                actions.move_to_element(element1)
                actions.click_and_hold()
                actions.move_by_offset(
                    elem2_rect['x'] - elem1_rect['x'],
                    elem2_rect['y'] - elem1_rect['y']
                )
                actions.release()
                actions.perform()

                print("  ✅ Mouse event simulation completed")

            except Exception as mouse_error:
                print(f"  ❌ Mouse event method failed: {mouse_error}")

                # Method 3: Direct element interaction (click-based)
                try:
                    print("  👆 Using click-based interaction...")

                    # Some games respond to clicking elements in sequence
                    element1.click()
                    time.sleep(0.2)
                    element2.click()

                    print("  ✅ Click-based interaction completed")

                except Exception as click_error:
                    print(f"  ❌ Click-based method failed: {click_error}")
                    return False

        # Wait for the game to process the combination
        print("  ⏳ Waiting for game to process combination...")
        time.sleep(2)

        return True

    except Exception as e:
        print(f"❌ Critical error during drag and drop: {e}")
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
