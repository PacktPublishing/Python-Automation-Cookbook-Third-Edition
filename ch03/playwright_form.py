import argparse
from playwright.sync_api import sync_playwright


def main(headless):

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        page = browser.new_page()
        page.goto('https://httpbin.org/forms/post')
        page.locator("input[name='custname']").clear()
        page.locator("input[name='custname']").type("Sean  O'Connell")

        # Select the size
        page.locator("input[name='size'][value='medium']").check()

        # Select the toppings
        page.get_by_role('checkbox', name='Bacon').check()
        page.get_by_role('checkbox', name='Extra Cheese').check()
        # page.locator("input[name='topping'][value='bacon']").check()
        # page.locator("input[name='topping'][value='cheese']").check()

        # Submit the order
        page.get_by_role("button", name="Submit").click()

        if headless:
            print("Running in headless mode, not waiting to see the result.")
            page.screenshot(path="playwright.png")

        else:
            # Not headless mode, waiting to allow to see the changes
            page.wait_for_timeout(5000)
        browser.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    # Add a headless argument
    parser.add_argument('--headless', action='store_true', help='Run browser in headless mode')
    args = parser.parse_args()

    main(args.headless)
