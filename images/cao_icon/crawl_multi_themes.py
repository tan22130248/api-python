import asyncio
import os
import re
import sys
import urllib.request
from playwright.async_api import async_playwright

# Configuration
THEMES = {
    "hinh_khoi": "shapes",
    "trai_cay": "fruits",
    "dong_vat": "animals"
}
TARGET_DIR = os.getcwd()
MAX_PAGES = 3      # Number of pages to crawl per theme
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

async def crawl_theme(page, theme_folder, search_keyword):
    print("\n" + "=" * 60)
    print(f"CRAWLING THEME: '{theme_folder}' (Keyword: '{search_keyword}')")
    print("=" * 60)
    
    all_icons = []
    base_url = f"https://www.flaticon.com/search?word={search_keyword}"
    
    for page_num in range(1, MAX_PAGES + 1):
        if page_num == 1:
            url = base_url
        else:
            url = f"https://www.flaticon.com/search/{page_num}?word={search_keyword}"
            
        print(f"\n--- [Theme: {theme_folder}] Crawling Page {page_num}: {url} ---")
        
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
                        
                        if (pngUrl) {
                            items.push({
                                png_url: pngUrl,
                                name: name || 'Icon',
                                id: id || Math.random().toString(36).substring(7),
                                style: style || 'Other'
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
            
            if len(icons_data) < 20:
                print("Few icons found, likely reached the last page.")
                break
                
        except Exception as e:
            print(f"Error crawling page {page_num}: {e}")
            break
            
    # De-duplicate icons by ID
    unique_icons = {}
    for icon in all_icons:
        unique_icons[icon['id']] = icon
        
    return list(unique_icons.values())

async def main():
    print("=" * 60)
    print("Starting Multi-Theme Flaticon Scraper")
    print(f"Target directory: {TARGET_DIR}")
    print(f"Themes: {list(THEMES.keys())}")
    print(f"Pages per theme: {MAX_PAGES}")
    print("=" * 60)

    async with async_playwright() as p:
        # Launch browser in non-headless mode
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
        
        # Crawl all themes sequentially
        theme_icons = {}
        for theme_folder, search_keyword in THEMES.items():
            icons_list = await crawl_theme(page, theme_folder, search_keyword)
            theme_icons[theme_folder] = icons_list
            print(f"Theme '{theme_folder}' finished. Total unique icons: {len(icons_list)}")
            
        await browser.close()

    # Start downloading icons for each theme
    sem = asyncio.Semaphore(CONCURRENT_DOWNLOADS)
    total_downloaded = 0
    total_found = sum(len(icons) for icons in theme_icons.values())
    
    print("\n" + "=" * 60)
    print("STARTING DOWNLOADS FOR ALL THEMES")
    print("=" * 60)
    
    for theme_folder, icons_list in theme_icons.items():
        if not icons_list:
            continue
            
        print(f"\nDownloading icons for theme '{theme_folder}'...")
        tasks = []
        for icon in icons_list:
            png_url = icon['png_url']
            name = sanitize_filename(icon['name'])
            id_str = icon['id']
            style = sanitize_filename(icon['style'])
            
            # Destination path: target_dir / theme_folder / style_folder / filename.png
            dest_dir = os.path.join(TARGET_DIR, theme_folder, style)
            filename = f"{name}_{id_str}.png"
            dest_path = os.path.join(dest_dir, filename)
            
            tasks.append(download_image(sem, png_url, dest_path))
            
        results = await asyncio.gather(*tasks)
        downloaded_count = sum(1 for r in results if r)
        total_downloaded += downloaded_count
        print(f"Theme '{theme_folder}': Downloaded {downloaded_count} out of {len(icons_list)} icons.")

    print("\n" + "=" * 60)
    print(f"Completed! Downloaded {total_downloaded} out of {total_found} icons across all themes.")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
