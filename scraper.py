import asyncio
import os
import re
from playwright.async_api import async_playwright

MAX_CONCURRENT_TASKS = 20


async def block_assets(route):
    if route.request.resource_type in ["image", "stylesheet", "font"]:
        await route.abort()
    else:
        await route.continue_()


async def scrape_game(context, url, row_index, output_folder):
    page = await context.new_page()
    try:
        await page.goto(url, wait_until='domcontentloaded')
        await page.locator("button:has-text('Show all games')").click()
        await page.wait_for_timeout(1500)

        row = page.locator("tr.gamelist-row.approved").nth(row_index)
        await row.scroll_into_view_if_needed()
        box = await row.bounding_box()
        if not box:
            raise Exception("Row bounding box not found")

        await page.mouse.click(box["x"] + 10, box["y"] + 10)

        modal_selector = "div.ReactModal__Content"
        content_ready_selector = "div.boxscore-modal table"

        await page.wait_for_selector(modal_selector, timeout=5000)
        await page.wait_for_selector(content_ready_selector, timeout=5000)

        modal = page.locator(modal_selector)
        modal_html = await modal.inner_html()

        heading = await modal.locator("h2.text-uppercase.m-3").text_content()
        match = re.search(r'Game\s+(\w+-\d+)', heading or "")
        game_id = match.group(1) if match else f"game_{row_index + 1}"

        filepath = os.path.join(output_folder, f"{game_id}.html")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(modal_html)

    except Exception as e:
        print(f"[Row {row_index}] Error: {e}")
    finally:
        await page.close()


async def download_game_modals_optimized(url, output_folder='data'):
    os.makedirs(output_folder, exist_ok=True)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        await context.route("**/*", block_assets)

        page = await context.new_page()
        await page.goto(url, wait_until='domcontentloaded')
        await page.locator("button:has-text('Show all games')").click()
        await page.wait_for_timeout(1500)

        rows = page.locator("tr.gamelist-row.approved")
        row_count = await rows.count()

        sem = asyncio.Semaphore(MAX_CONCURRENT_TASKS)

        async def bounded_scrape(i):
            async with sem:
                await scrape_game(context, url, i, output_folder)

        tasks = [bounded_scrape(i) for i in range(row_count)]
        await asyncio.gather(*tasks)

        await context.close()
        await browser.close()


def run(url):
    output_folder = "data"
    os.makedirs(output_folder, exist_ok=True)
    for file in os.listdir(output_folder):
        os.remove(os.path.join(output_folder, file))

    asyncio.run(download_game_modals_optimized(url, output_folder))
