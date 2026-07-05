import asyncio
import os
import re
import sys
import urllib.request
from playwright.async_api import async_playwright

# Configuration
SEARCH_WORD = "pond"
BASE_URL = f"https://www.flaticon.com/search?word={SEARCH_WORD}"
TARGET_DIR = os.getcwd()
GROUP_BY = "style"  # Options: "style" (default), "pack", or "none"
MAX_PAGES = 5      # Default page limit to prevent infinite loops and security blocks
CONCURRENT_DOWNLOADS = 5

def sanitize_filename(name):
    # Remove any characters not allowed in folder/file names on Windows
    return re.sub(r'[\\/*?:"<>|]', "", name).strip()

async def download_image(sem, url, dest_path):
    async with sem:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        }
        req = urllib.request.Request(url, headers=headers)
        try:
            # Create parent directories if they don't exist
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
            
            # Download file
            loop = asyncio.get_event_loop()
            def _download():
                with urllib.request.urlopen(req, timeout=15) as response:
                    return response.read()
            
            content = await loop.run_in_executor(None, _download)
            with open(dest_path, "wb") as f:
                f.write(content)
            print(f"Downloaded: {os.path.basename(dest_path)}")
            return True
        except Exception as e:
            print(f"Failed to download {url}: {e}")
            return False

async def main():
    print("=" * 60)
    print(f"Starting Flaticon Scraper for word: '{SEARCH_WORD}'")
    print(f"Saving files in: {TARGET_DIR}")
    print(f"Grouping method: {GROUP_BY}")
    print(f"Max Pages to crawl: {MAX_PAGES}")
    print("=" * 60)

    all_icons = []
    
    async with async_playwright() as p:
        # Launch browser in non-headless mode to avoid bot detection
        try:
            print("Launching Chrome...")
            browser = await p.chromium.launch(headless=False, channel="chrome")
        except Exception as e:
            print(f"Failed to launch Chrome channel ({e}). Falling back to Chromium headless=False...")
            browser = await p.chromium.launch(headless=False)
            
        context = await browser.new_context(
            viewport={"width": 1280, "height": 800}
        )
        page = await context.new_page()
        
        for page_num in range(1, MAX_PAGES + 1):
            if page_num == 1:
                url = BASE_URL
            else:
                url = f"https://www.flaticon.com/search/{page_num}?word={SEARCH_WORD}"
            print(f"\n--- Crawling Page {page_num}: {url} ---")
            
            try:
                await page.goto(url, timeout=60000)
                # Wait for content to load and let JavaScript run
                await page.wait_for_timeout(5000)
                
                title = await page.title()
                if "security filter" in title.lower() or "permission" in title.lower():
                    print("Error: Blocked by security filter.")
                    break
                
                # Check for icons on the page
                icons_data = await page.evaluate("""
                    () => {
                        const items = [];
                        const elements = document.querySelectorAll('li.icon--item');
                        elements.forEach(el => {
                            const pngUrl = el.getAttribute('data-png');
                            const name = el.getAttribute('data-name');
                            const id = el.getAttribute('data-id');
                            const style = el.getAttribute('data-style_name');
                            const pack = el.getAttribute('data-pack_name');
                            
                            if (pngUrl) {
                                items.push({
                                    png_url: pngUrl,
                                    name: name || 'Icon',
                                    id: id || Math.random().toString(36).substring(7),
                                    style: style || 'Other',
                                    pack: pack || 'Other'
                                });
                            }
                        });
                        return items;
                    }
                """)
                
                if not icons_data:
                    print("No icons found on this page. Stopping.")
                    break
                    
                print(f"Found {len(icons_data)} icons on Page {page_num}.")
                all_icons.extend(icons_data)
                
                # If we received less than a full page of icons (usually ~50-100), we might have reached the end
                if len(icons_data) < 20:
                    print("Few icons found, likely reached the last page.")
                    break
                    
            except Exception as e:
                print(f"Error crawling page {page_num}: {e}")
                break
                
        await browser.close()
        
    if not all_icons:
        print("\nNo icons were successfully found or crawled.")
        return

    # De-duplicate icons by ID
    unique_icons = {}
    for icon in all_icons:
        unique_icons[icon['id']] = icon
    
    icons_list = list(unique_icons.values())
    print(f"\nTotal unique icons found across all pages: {len(icons_list)}")
    
    # Download icons
    print("\nStarting downloads...")
    sem = asyncio.Semaphore(CONCURRENT_DOWNLOADS)
    tasks = []
    
    for icon in icons_list:
        png_url = icon['png_url']
        name = sanitize_filename(icon['name'])
        id_str = icon['id']
        style = sanitize_filename(icon['style'])
        pack = sanitize_filename(icon['pack'])
        
        # Determine target path
        if GROUP_BY == "style":
            dir_name = style
        elif GROUP_BY == "pack":
            dir_name = pack
        else:
            dir_name = ""
            
        group_dir = os.path.join(TARGET_DIR, dir_name)
        filename = f"{name}_{id_str}.png"
        dest_path = os.path.join(group_dir, filename)
        
        tasks.append(download_image(sem, png_url, dest_path))
        
    results = await asyncio.gather(*tasks)
    downloaded_count = sum(1 for r in results if r)
    
    print("\n" + "=" * 60)
    print(f"Completed! Downloaded {downloaded_count} out of {len(icons_list)} icons.")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
