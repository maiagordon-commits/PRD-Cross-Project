#!/usr/bin/env python3
"""Export Google Slides–compatible files: fixed PPTX, PNG slides, and PDF."""

import os
import subprocess
import sys
import zipfile

import img2pdf

DOCS_DIR = "/workspace/docs"
EXPORT_DIR = "/workspace/exports"
BRANCH = "cursor/timeline-google-sheet-30e7"
REPO = "maiagordon-commits/PRD-Cross-Project"


def run_generators():
    subprocess.run([sys.executable, "/workspace/create_actual_vs_planned_chart.py"], check=True)
    subprocess.run([sys.executable, "/workspace/create_open_api_milestone_slide.py", "--google-compatible"], check=True)
    subprocess.run([sys.executable, "/workspace/create_cumulative_migration_slide.py", "--google-compatible"], check=True)


def screenshot_html_deck(page, html_path, prefix, slide_count):
    """Capture each slide from an HTML deck via JS navigation."""
    file_url = f"file://{html_path}"
    page.goto(file_url, wait_until="networkidle")
    page.set_viewport_size({"width": 1280, "height": 720})
    paths = []
    os.makedirs(EXPORT_DIR, exist_ok=True)
    for i in range(slide_count):
        page.evaluate(f"typeof go === 'function' && go({i})")
        page.wait_for_timeout(350)
        out = os.path.join(EXPORT_DIR, f"{prefix}_slide_{i + 1}.png")
        page.locator(".slide.active").screenshot(path=out)
        paths.append(out)
        print(f"  PNG: {out}")
    return paths


def pngs_to_pdf(png_paths, pdf_path):
    with open(pdf_path, "wb") as f:
        f.write(img2pdf.convert(png_paths))
    print(f"  PDF: {pdf_path}")


def zip_files(files, zip_path):
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in files:
            zf.write(f, os.path.basename(f))
    print(f"  ZIP: {zip_path}")


def main():
    os.makedirs(EXPORT_DIR, exist_ok=True)
    print("Generating Google-compatible PPTX (no internal hyperlinks)...")
    run_generators()

    from playwright.sync_api import sync_playwright

    print("\nCapturing HTML slides as PNG...")
    all_pngs = []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        all_pngs.extend(screenshot_html_deck(
            page, f"{DOCS_DIR}/open-api-milestone.html", "open_api", 3))
        all_pngs.extend(screenshot_html_deck(
            page, f"{DOCS_DIR}/migration-cumulative.html", "migration", 5))
        browser.close()

    print("\nBuilding PDFs...")
    open_api_pngs = [p for p in all_pngs if "open_api" in p]
    migration_pngs = [p for p in all_pngs if "migration" in p]
    pngs_to_pdf(open_api_pngs, f"{EXPORT_DIR}/open_api_milestone_slides.pdf")
    pngs_to_pdf(migration_pngs, f"{EXPORT_DIR}/migration_cumulative_slides.pdf")
    zip_files(all_pngs, f"{EXPORT_DIR}/all_slides_png.zip")

    print("\nDone. Files ready in exports/")
    print(f"\nBrowser links (no import):")
    print(f"  https://htmlpreview.github.io/?https://github.com/{REPO}/raw/{BRANCH}/docs/index.html")


if __name__ == "__main__":
    main()
