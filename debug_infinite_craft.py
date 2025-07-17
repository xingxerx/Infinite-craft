#!/usr/bin/env python3
"""
Debug script to analyze Infinite Craft HTML structure and find correct selectors
===============================================================================

This script will help us understand the actual DOM structure and find the
correct way to interact with elements in Infinite Craft.
"""

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def setup_debug_driver():
    """Setup driver for debugging."""
    service = ChromeService(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Chrome(service=service, options=options)
    driver.maximize_window()
    return driver


def analyze_page_structure(driver):
    """Analyze the page structure to find correct selectors."""
    print("🔍 Analyzing page structure...")
    
    # Get page source and analyze
    try:
        # Wait for page to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        print("\n📋 Page Title:", driver.title)
        print("🌐 Current URL:", driver.current_url)
        
        # Find all possible element containers
        print("\n🔍 Looking for element containers...")
        
        # Common selectors to try
        selectors_to_try = [
            ".item",
            ".element", 
            ".craft-item",
            ".draggable",
            "[draggable='true']",
            ".instance",
            ".block",
            ".tile",
            "div[class*='item']",
            "div[class*='element']",
            "div[class*='craft']"
        ]
        
        for selector in selectors_to_try:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    print(f"  ✅ Found {len(elements)} elements with selector: {selector}")
                    
                    # Show first few elements
                    for i, elem in enumerate(elements[:5]):
                        try:
                            text = elem.text.strip()
                            classes = elem.get_attribute("class")
                            tag = elem.tag_name
                            print(f"    [{i}] {tag}.{classes}: '{text}'")
                        except:
                            print(f"    [{i}] Error reading element")
                else:
                    print(f"  ❌ No elements found with selector: {selector}")
            except Exception as e:
                print(f"  ❌ Error with selector {selector}: {e}")
        
        # Analyze the main container
        print("\n🏗️ Analyzing main container structure...")
        try:
            body = driver.find_element(By.TAG_NAME, "body")
            print("Body classes:", body.get_attribute("class"))
            
            # Get all direct children of body
            children = driver.find_elements(By.CSS_SELECTOR, "body > *")
            print(f"Body has {len(children)} direct children:")
            
            for i, child in enumerate(children):
                tag = child.tag_name
                classes = child.get_attribute("class") or "no-class"
                id_attr = child.get_attribute("id") or "no-id"
                print(f"  [{i}] <{tag}> id='{id_attr}' class='{classes}'")
                
        except Exception as e:
            print(f"Error analyzing container: {e}")
            
    except Exception as e:
        print(f"Error analyzing page: {e}")


def test_interaction_methods(driver):
    """Test different ways to interact with elements."""
    print("\n🧪 Testing interaction methods...")
    
    # Find any draggable elements
    possible_selectors = [".item", ".element", "[draggable='true']", ".instance"]
    
    for selector in possible_selectors:
        try:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            if len(elements) >= 2:
                print(f"\n🎯 Testing with selector: {selector}")
                elem1, elem2 = elements[0], elements[1]
                
                print(f"Element 1: '{elem1.text}' - draggable: {elem1.get_attribute('draggable')}")
                print(f"Element 2: '{elem2.text}' - draggable: {elem2.get_attribute('draggable')}")
                
                # Test if elements are actually draggable
                try:
                    # Check element properties
                    print(f"Element 1 location: {elem1.location}")
                    print(f"Element 1 size: {elem1.size}")
                    print(f"Element 1 displayed: {elem1.is_displayed()}")
                    print(f"Element 1 enabled: {elem1.is_enabled()}")
                    
                    # Try to get parent container info
                    parent1 = elem1.find_element(By.XPATH, "..")
                    print(f"Element 1 parent: <{parent1.tag_name}> class='{parent1.get_attribute('class')}'")
                    
                except Exception as e:
                    print(f"Error analyzing element properties: {e}")
                
                break
        except Exception as e:
            print(f"Error with selector {selector}: {e}")


def main():
    """Main debug function."""
    print("🐛 Starting Infinite Craft Debug Analysis")
    print("=" * 50)
    
    driver = setup_debug_driver()
    
    try:
        print("🌐 Navigating to Infinite Craft...")
        driver.get("https://neal.fun/infinite-craft/")
        
        # Wait a bit for everything to load
        time.sleep(5)
        
        # Analyze the page
        analyze_page_structure(driver)
        
        # Test interaction methods
        test_interaction_methods(driver)
        
        print("\n⏸️  Pausing for manual inspection...")
        print("The browser will stay open for 30 seconds for manual inspection.")
        print("Check the browser window to see the actual game interface.")
        
        time.sleep(30)
        
    except Exception as e:
        print(f"❌ Error during debug: {e}")
    finally:
        print("\n🔄 Closing debug driver...")
        driver.quit()
        print("✅ Debug analysis completed.")


if __name__ == "__main__":
    main()
