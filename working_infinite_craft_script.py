#!/usr/bin/env python3
"""
Working Infinite Craft Automation Script
========================================

This is a completely rewritten version that actually works for merging items.
Based on analysis of the game's HTML structure and JavaScript requirements.
"""

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

# Configuration
GAME_URL = "https://neal.fun/infinite-craft/"
GAME_STATE_FILE = "game_state.json"

def setup_driver():
    """Setup Chrome WebDriver with optimal settings for Infinite Craft."""
    try:
        service = ChromeService(ChromeDriverManager().install())
        options = webdriver.ChromeOptions()
        
        # Essential options for stability
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        driver = webdriver.Chrome(service=service, options=options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        driver.maximize_window()
        driver.implicitly_wait(3)
        
        print("✅ WebDriver setup successful")
        return driver
        
    except Exception as e:
        print(f"❌ WebDriver setup failed: {e}")
        return None

def get_elements(driver):
    """Get all draggable elements from the game."""
    try:
        # Wait for elements to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".item"))
        )
        
        # Get all .item elements
        elements = driver.find_elements(By.CSS_SELECTOR, ".item")
        
        # Filter to only visible, text-containing elements
        valid_elements = []
        for elem in elements:
            try:
                if elem.is_displayed() and elem.text.strip():
                    valid_elements.append(elem)
            except:
                continue
                
        print(f"Found {len(valid_elements)} valid elements")
        for i, elem in enumerate(valid_elements):
            print(f"  [{i}] {elem.text}")
            
        return valid_elements
        
    except Exception as e:
        print(f"❌ Error getting elements: {e}")
        return []

def perform_combination(driver, elem1, elem2):
    """
    Perform element combination using the method that actually works for Infinite Craft.
    
    After analysis, the game responds to proper HTML5 drag events.
    """
    try:
        print(f"\n🎯 Attempting: {elem1.text} + {elem2.text}")
        
        # Get initial element count for comparison
        initial_elements = driver.find_elements(By.CSS_SELECTOR, ".item")
        initial_texts = [e.text for e in initial_elements if e.text.strip()]
        initial_count = len(initial_texts)
        
        print(f"  Initial elements: {initial_count}")
        
        # Method 1: HTML5 Drag Events (most reliable for this game)
        js_drag_code = """
        function performInfiniteCraftDrag(source, target) {
            // Create proper drag events
            function createDragEvent(type, dataTransfer) {
                var event = new DragEvent(type, {
                    bubbles: true,
                    cancelable: true,
                    dataTransfer: dataTransfer || new DataTransfer()
                });
                return event;
            }
            
            // Start the drag sequence
            var dataTransfer = new DataTransfer();
            
            // Dispatch dragstart on source
            var dragStartEvent = createDragEvent('dragstart', dataTransfer);
            source.dispatchEvent(dragStartEvent);
            
            // Dispatch dragenter on target
            var dragEnterEvent = createDragEvent('dragenter', dataTransfer);
            target.dispatchEvent(dragEnterEvent);
            
            // Dispatch dragover on target
            var dragOverEvent = createDragEvent('dragover', dataTransfer);
            target.dispatchEvent(dragOverEvent);
            
            // Dispatch drop on target
            var dropEvent = createDragEvent('drop', dataTransfer);
            target.dispatchEvent(dropEvent);
            
            // Dispatch dragend on source
            var dragEndEvent = createDragEvent('dragend', dataTransfer);
            source.dispatchEvent(dragEndEvent);
            
            return true;
        }
        
        return performInfiniteCraftDrag(arguments[0], arguments[1]);
        """
        
        # Execute the drag operation
        result = driver.execute_script(js_drag_code, elem1, elem2)
        print(f"  ✅ Drag operation executed: {result}")
        
        # Wait for the game to process
        time.sleep(3)
        
        # Check for new elements
        new_elements = driver.find_elements(By.CSS_SELECTOR, ".item")
        new_texts = [e.text for e in new_elements if e.text.strip()]
        new_count = len(new_texts)
        
        print(f"  After combination: {new_count} elements")
        
        # Find new items
        new_items = [text for text in new_texts if text not in initial_texts]
        
        if new_items:
            for item in new_items:
                print(f"  🎉 NEW ITEM CREATED: {item}")
            return new_items[0]  # Return the first new item
        else:
            print(f"  ⚠️  No new items detected")
            return None
            
    except Exception as e:
        print(f"  ❌ Combination failed: {e}")
        return None

def main():
    """Main automation function."""
    print("🚀 Starting Working Infinite Craft Automation")
    print("=" * 50)
    
    driver = setup_driver()
    if not driver:
        return
    
    try:
        # Navigate to the game
        print("🌐 Navigating to Infinite Craft...")
        driver.get(GAME_URL)
        time.sleep(5)  # Wait for full load
        
        # Get initial elements
        elements = get_elements(driver)
        if len(elements) < 2:
            print("❌ Need at least 2 elements to start")
            return
        
        discovered_items = set()
        combinations_tried = set()
        
        print("\n🎮 Starting combination attempts...")
        
        # Try some basic combinations first
        basic_combinations = [
            (0, 1),  # First two elements
            (0, 2),  # First and third
            (1, 2),  # Second and third
            (0, 3),  # First and fourth (if exists)
        ]
        
        for i, (idx1, idx2) in enumerate(basic_combinations):
            if idx1 < len(elements) and idx2 < len(elements):
                elem1, elem2 = elements[idx1], elements[idx2]
                
                # Skip if already tried
                combo_key = tuple(sorted([elem1.text, elem2.text]))
                if combo_key in combinations_tried:
                    continue
                    
                combinations_tried.add(combo_key)
                
                # Attempt combination
                new_item = perform_combination(driver, elem1, elem2)
                
                if new_item:
                    discovered_items.add(new_item)
                    print(f"✅ Success! Discovered: {new_item}")
                    
                    # Refresh elements list to include new items
                    time.sleep(2)
                    elements = get_elements(driver)
                else:
                    print("❌ No new item created")
                
                # Small delay between attempts
                time.sleep(2)
        
        print(f"\n🎉 Automation completed!")
        print(f"📊 Total new items discovered: {len(discovered_items)}")
        for item in discovered_items:
            print(f"  • {item}")
            
    except KeyboardInterrupt:
        print("\n⏹️  Stopped by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
    finally:
        print("\n🔄 Closing browser...")
        driver.quit()
        print("✅ Done!")

if __name__ == "__main__":
    main()
