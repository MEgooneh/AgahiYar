from playwright.async_api import Playwright, async_playwright, expect

import time
import asyncio

import json


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        await page.goto("https://divar.ir/v/AZZ30Oud")
        await page.locator('.kt-row').screenshot(path=f'images/{425}/{5252}.png')

        # post.category
        values_locator = page.locator('.kt-breadcrumbs__link')
        values = await values_locator.evaluate_all("list => list.map(element => element.textContent)")
        category = '/'.join(values[:-1])
        #print("Category : " , category)
        # post.fields
        title_locator = page.locator('.kt-base-row__title')
        value_locator = page.locator('.kt-unexpandable-row__value')
        titles = await title_locator.evaluate_all("list => list.map(element => element.textContent)")
        values = await value_locator.evaluate_all("list => list.map(element => element.textContent)")
        data = dict(zip(titles, values))
        json_data = json.dumps(data, ensure_ascii=False)
        fields = json_data
        print("fields : " , fields)
        element_locator = page.locator('.kt-description-row__text--primary')
        element_text = await element_locator.text_content()
        print("ddescription: " , element_text)



asyncio.run(main())
