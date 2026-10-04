# nyc_prospector.py
import asyncio
import csv
import re
from playwright.async_api import async_playwright

async def run_nyc_lead_generator():
    print("[*] Initializing Playwright engine for NYC Target Discovery...")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox"]
        )
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        # Target: NYC Tech / Seed-Series A Companies actively building web apps
        target_url = "https://www.builtinnyc.com/jobs/dev-engineering/front-end"
        print(f"[*] Navigating to target index: {target_url}")
        
        try:
            await page.goto(target_url, timeout=60000)
            await page.wait_for_selector("body", timeout=10000)
        except Exception as e:
            print(f"[!] Navigation error or timeout: {e}")
            await browser.close()
            return

        print("[*] Extracting target company listings and location indicators...")
        leads = []
        
        # Parse job cards or company directory cards for high-intent matches
        cards = await page.locator(".job-card, article, div.company-tile").all()
        
        if not cards:
            # Fallback generic parsing for raw text nodes if selectors shift
            print("[*] Using fallback content node extraction...")
            body_text = await page.inner_text("body")
            print(f"[*] Scraped page text length: {len(body_text)} characters.")
        
        for card in cards[:25]: # Grab top high-intent leads
            try:
                text = await card.inner_text()
                lines = [l.strip() for l in text.split("\n") if l.strip()]
                
                company_name = lines[0] if len(lines) > 0 else "Unknown"
                role_title = lines[1] if len(lines) > 1 else "Frontend / React"
                
                # Filter strictly for NYC or Hybrid NYC footprints
                if any(loc in text for loc in ["New York", "NYC", "Manhattan", "Brooklyn"]):
                    leads.append({
                        "Company": company_name,
                        "RoleOrContext": role_title,
                        "Location": "New York, NY",
                        "Actionable": "High-Intent Outreach & Coffee Meetup Target"
                    })
            except Exception:
                continue

        await browser.close()

        # Deduplicate results
        unique_leads = {v['Company']: v for v in leads}.values()

        filename = "nyc_react_leads.csv"
        print(f"[*] Saving {len(unique_leads)} targeted NYC leads to {filename}...")
        
        with open(filename, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["Company", "RoleOrContext", "Location", "Actionable"])
            writer.writeheader()
            writer.writerows(unique_leads)
            
        print("[+] Discovery complete. Ready for instant outreach & in-person coffee pitching in Manhattan.")

if __name__ == "__main__":
    asyncio.run(run_nyc_lead_generator())
