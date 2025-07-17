#!/usr/bin/env python3
"""
Manual Test Script for Infinite Craft
=====================================

This script opens the game and allows manual testing to understand
exactly how the drag-and-drop should work.
"""

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def setup_manual_driver():
    """Setup driver for manual testing."""
    service = ChromeService(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    
    # Minimal options to avoid detection
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    driver = webdriver.Chrome(service=service, options=options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    return driver

def analyze_game_behavior(driver):
    """Analyze how the game actually works."""
    print("🔍 Analyzing game behavior...")
    
    try:
        # Wait for elements
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".item"))
        )
        
        # Get elements
        elements = driver.find_elements(By.CSS_SELECTOR, ".item")
        print(f"Found {len(elements)} elements")
        
        for i, elem in enumerate(elements):
            print(f"  [{i}] {elem.text} - Location: {elem.location}")
        
        # Test if we can detect the canvas or drop area
        canvas_selectors = [
            "canvas",
            ".canvas",
            ".drop-area",
            ".craft-area",
            ".workspace",
            "#canvas"
        ]
        
        for selector in canvas_selectors:
            try:
                canvas = driver.find_element(By.CSS_SELECTOR, selector)
                print(f"Found canvas/drop area: {selector}")
                print(f"  Size: {canvas.size}")
                print(f"  Location: {canvas.location}")
            except:
                continue
        
        # Check for any JavaScript events or listeners
        js_check = """
        // Check if elements have event listeners
        var items = document.querySelectorAll('.item');
        var info = [];
        items.forEach(function(item, index) {
            info.push({
                index: index,
                text: item.textContent,
                draggable: item.draggable,
                hasMouseDown: item.onmousedown !== null,
                hasDragStart: item.ondragstart !== null,
                classList: Array.from(item.classList)
            });
        });
        return info;
        """
        
        element_info = driver.execute_script(js_check)
        print("\n📋 Element Analysis:")
        for info in element_info:
            print(f"  {info['text']}: draggable={info['draggable']}, classes={info['classList']}")
        
    except Exception as e:
        print(f"❌ Analysis error: {e}")

def test_simple_interaction(driver):
    """Test simple interactions to see what works."""
    print("\n🧪 Testing simple interactions...")
    
    try:
        elements = driver.find_elements(By.CSS_SELECTOR, ".item")
        if len(elements) >= 2:
            elem1, elem2 = elements[0], elements[1]
            
            print(f"Testing with: {elem1.text} and {elem2.text}")
            
            # Test 1: Simple click
            print("  Test 1: Clicking elements...")
            elem1.click()
            time.sleep(1)
            elem2.click()
            time.sleep(2)
            
            # Check for changes
            new_elements = driver.find_elements(By.CSS_SELECTOR, ".item")
            print(f"  After clicks: {len(new_elements)} elements")
            
            # Test 2: Try to drag to center of screen
            print("  Test 2: Dragging to center...")
            
            # Get viewport center
            viewport_center = driver.execute_script("""
                return {
                    x: window.innerWidth / 2,
                    y: window.innerHeight / 2
                };
            """)
            
            from selenium.webdriver.common.action_chains import ActionChains
            actions = ActionChains(driver)
            
            # Try dragging first element to center
            actions.drag_and_drop_by_offset(elem1, 
                                          viewport_center['x'] - elem1.location['x'],
                                          viewport_center['y'] - elem1.location['y']).perform()
            time.sleep(2)
            
            # Check for changes again
            newer_elements = driver.find_elements(By.CSS_SELECTOR, ".item")
            print(f"  After drag to center: {len(newer_elements)} elements")
            
    except Exception as e:
        print(f"❌ Interaction test error: {e}")

def main():
    """Main function for manual testing."""
    print("🔧 Manual Test Script for Infinite Craft")
    print("=" * 40)
    
    driver = setup_manual_driver()
    
    try:
        print("🌐 Opening Infinite Craft...")
        driver.get("https://neal.fun/infinite-craft/")
        
        # Wait for page to load
        time.sleep(5)
        
        # Analyze the game
        analyze_game_behavior(driver)
        
        # Test interactions
        test_simple_interaction(driver)
        
        print("\n⏸️  Manual inspection time...")
        print("The browser will stay open for 60 seconds.")
        print("Try manually dragging elements to see how it works!")
        print("Watch the browser console for any errors or events.")
        
        # Keep browser open for manual testing
        time.sleep(60)
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        print("\n🔄 Closing browser...")
        driver.quit()
        print("✅ Manual test completed!")

if __name__ == "__main__":
    main()
