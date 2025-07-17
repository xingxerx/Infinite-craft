#!/usr/bin/env python3
"""
Test script for Infinite Craft drag-and-drop functionality
=========================================================

This script tests the improved drag-and-drop functionality to ensure
items can be successfully merged in the Infinite Craft game.

Usage: python test_drag_drop.py
"""

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def setup_test_driver():
    """Sets up a Chrome WebDriver for testing."""
    try:
        service = ChromeService(ChromeDriverManager().install())
        options = webdriver.ChromeOptions()
        
        # Basic options for testing
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--log-level=3")
        options.add_argument("--disable-blink-features=AutomationControlled")
        
        driver = webdriver.Chrome(service=service, options=options)
        driver.maximize_window()
        driver.set_page_load_timeout(30)
        driver.implicitly_wait(3)
        
        print("✅ Test WebDriver setup successful.")
        return driver
        
    except WebDriverException as e:
        print(f"❌ Error setting up test WebDriver: {e}")
        return None


def test_basic_navigation(driver):
    """Test basic navigation to the game."""
    try:
        print("🌐 Navigating to Infinite Craft...")
        driver.get("https://neal.fun/infinite-craft/")
        
        # Wait for initial elements
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".item"))
        )
        
        print("✅ Successfully navigated to game and found initial elements.")
        return True
        
    except TimeoutException:
        print("❌ Timeout waiting for game elements to load.")
        return False
    except Exception as e:
        print(f"❌ Navigation error: {e}")
        return False


def get_test_elements(driver):
    """Get elements for testing drag-and-drop."""
    try:
        print("🔍 Looking for draggable elements...")
        
        # Wait for elements to be present
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".item"))
        )
        
        # Get all visible elements
        elements = driver.find_elements(By.CSS_SELECTOR, ".item")
        draggable_elements = []
        
        for element in elements:
            try:
                if element.is_displayed() and element.text.strip():
                    draggable_elements.append(element)
                    print(f"  Found element: {element.text}")
            except Exception:
                continue
        
        print(f"✅ Found {len(draggable_elements)} draggable elements.")
        return draggable_elements
        
    except Exception as e:
        print(f"❌ Error getting test elements: {e}")
        return []


def test_drag_and_drop_methods(driver, element1, element2):
    """Test different drag-and-drop methods."""
    print(f"\n🧪 Testing drag-and-drop: {element1.text} + {element2.text}")
    
    # Get initial element count
    initial_elements = driver.find_elements(By.CSS_SELECTOR, ".item")
    initial_count = len(initial_elements)
    initial_texts = [elem.text for elem in initial_elements if elem.text.strip()]
    
    print(f"Initial element count: {initial_count}")
    print(f"Initial elements: {initial_texts}")
    
    # Method 1: Standard drag_and_drop
    try:
        print("  Method 1: Standard drag_and_drop")
        actions = ActionChains(driver)
        actions.drag_and_drop(element1, element2).perform()
        
        # Wait for result
        time.sleep(3)
        
        # Check for changes
        new_elements = driver.find_elements(By.CSS_SELECTOR, ".item")
        new_count = len(new_elements)
        new_texts = [elem.text for elem in new_elements if elem.text.strip()]
        
        print(f"  After drag-drop: {new_count} elements")
        print(f"  New elements: {new_texts}")
        
        # Check for new items
        for text in new_texts:
            if text not in initial_texts:
                print(f"  ✅ NEW ITEM CREATED: {text}")
                return True
                
        print("  ⚠️  No new item detected with Method 1")
        
    except Exception as e:
        print(f"  ❌ Method 1 failed: {e}")
    
    # Method 2: Click and hold approach
    try:
        print("  Method 2: Click and hold")
        actions = ActionChains(driver)
        actions.click_and_hold(element1).move_to_element(element2).release().perform()
        
        time.sleep(3)
        
        # Check for changes again
        newer_elements = driver.find_elements(By.CSS_SELECTOR, ".item")
        newer_texts = [elem.text for elem in newer_elements if elem.text.strip()]
        
        for text in newer_texts:
            if text not in initial_texts:
                print(f"  ✅ NEW ITEM CREATED: {text}")
                return True
                
        print("  ⚠️  No new item detected with Method 2")
        
    except Exception as e:
        print(f"  ❌ Method 2 failed: {e}")
    
    return False


def main():
    """Main test function."""
    print("🚀 Starting Infinite Craft Drag-and-Drop Test")
    print("=" * 50)
    
    driver = setup_test_driver()
    if not driver:
        print("❌ Failed to setup driver. Exiting.")
        return
    
    try:
        # Test navigation
        if not test_basic_navigation(driver):
            print("❌ Navigation test failed. Exiting.")
            return
        
        # Get elements for testing
        elements = get_test_elements(driver)
        if len(elements) < 2:
            print("❌ Need at least 2 elements for testing. Exiting.")
            return
        
        # Test with the first two elements (usually Fire, Water, Earth, Wind)
        element1 = elements[0]
        element2 = elements[1]
        
        # Test drag-and-drop
        success = test_drag_and_drop_methods(driver, element1, element2)
        
        if success:
            print("\n✅ DRAG-AND-DROP TEST PASSED!")
            print("The improved functionality successfully creates new items.")
        else:
            print("\n❌ DRAG-AND-DROP TEST FAILED!")
            print("No new items were created. May need further debugging.")
        
        # Wait a bit to see the result
        print("\nWaiting 5 seconds to observe the result...")
        time.sleep(5)
        
    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted by user.")
    except Exception as e:
        print(f"\n❌ Unexpected error during test: {e}")
    finally:
        print("\n🔄 Closing test driver...")
        driver.quit()
        print("✅ Test completed.")


if __name__ == "__main__":
    main()
