import asyncio
import os
import re

from playwright.async_api import async_playwright


async def download_game_modals(url, output_folder='data'):
    os.makedirs(output_folder, exist_ok=True)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url, wait_until='networkidle')


        try:
            button = page.locator("button:has-text('Show all games')")
            await button.wait_for(timeout=5000)
            await button.scroll_into_view_if_needed()
            await button.click()
            print("✅ Clicked 'Show all games'")
            await page.wait_for_timeout(2000)
        except Exception as e:
            print(f"❌ Could not click 'Show all games': {e}")
            return


        row_selector = "tr.gamelist-row.approved"
        await page.locator(row_selector).first.wait_for(timeout=5000)
        total_rows = await page.locator(row_selector).count()
        print(f"✅ Found {total_rows} game rows")


        for i in range(total_rows):
            await page.goto(url, wait_until='networkidle')


            button = page.locator("button:has-text('Show all games')")
            await button.wait_for(timeout=5000)
            await button.click()
            await page.wait_for_timeout(1500)

            rows = page.locator(row_selector)
            row = rows.nth(i)
            await row.scroll_into_view_if_needed()

            try:
                box = await row.bounding_box()
                await page.mouse.click(box["x"] + 10, box["y"] + 10)
                print(f"➡️ Clicked row {i + 1}")
            except Exception as e:
                print(f"❌ Failed to click row {i + 1}: {e}")
                continue


            modal_selector = "div.ReactModal__Content"
            content_ready_selector = "div.boxscore-modal table"

            try:
                print("⏳ Waiting for modal content to load...")
                await page.wait_for_selector(modal_selector, timeout=7000, state='visible')
                await page.wait_for_selector(content_ready_selector, timeout=7000, state='visible')

                modal = page.locator(modal_selector)
                modal_html = await modal.inner_html()


                heading_locator = modal.locator("h2.text-uppercase.m-3")
                heading_text = await heading_locator.text_content()
                match = re.search(r'Game\s+(\w+-\d+)', heading_text or "")
                game_id = match.group(1) if match else f"game_{i + 1}"

                filename = os.path.join(output_folder, f"{game_id}.html")
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(modal_html)

                print(f"✅ Saved overlay for {game_id}")


                await page.keyboard.press("Escape")
                await page.wait_for_timeout(1000)

            except Exception as e:
                print(f"❌ Modal content error for row {i + 1}: {e}")
                continue

        await browser.close()


def run(url):
    folder_path = "data"
    try:
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)
    except FileNotFoundError:
        os.makedirs(folder_path, exist_ok=True)
    asyncio.run(download_game_modals(url, folder_path))
