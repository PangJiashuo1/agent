from playwright.async_api import async_playwright
import asyncio





# OpenClaw 规范 Skill
def skill(func):
    async def wrapper(*args, **kwargs):
        return await func(*args, **kwargs)

    return wrapper


class TaobaoUISkill:
    def __init__(self):
        self.skill_id = "taobao_ui_automation"
        self.name = "淘宝UI自动化"
        self.description = "登录 → 搜索Tshirt → 价格<1000 → 加入购物车"

    @skill
    async def run(self):
        result = {
            "status": "success",
            "message": "",
            "steps": []
        }
        async with async_playwright() as p:
            browser = await p.chromium.launch(channel="msedge", headless=False)  # 打开edge浏览器
            page = await browser.new_page()
            try:
                # 进入电商网站
                await page.goto("https://automationexercise.com")  # 绕不开淘宝反爬人机验证，所以用公开电商网站代替
                result["steps"].append("打开网站")

                # 自动填充账号密码
                # await page.locator("#header a[href='/login']").click()
                # await page.fill("[data-qa='login-email']", "******")
                # await page.fill("[data-qa='login-password']", "*******")
                # await page.click("[data-qa='login-button']")
                # result["steps"].append("登录完成")

                # 提示用户手动登录
                await page.get_by_text("Login").click()
                result["steps"].append("请手动登录。")
                # await page.wait_for_timeout(1000)
                # 检查登录是否成功
                while True:
                    if not await page.get_by_text("Logout").is_visible():
                        await asyncio.sleep(2)  # 暂停2秒，避免过多请求
                    else:
                        break  # 检测到 Logout，退出循环

                result["steps"].append("登录成功")

                # 点击商品页
                await page.locator("#header a[href='/products']").click()
                result["steps"].append("进入商品页")

                # 点击搜索框，搜索Tshirt
                await page.fill("#search_product", "Tshirt")
                await page.click("#submit_search")
                await page.wait_for_timeout(2000)
                result["steps"].append("搜索Tshirt完成")

                # 获取每一个商品盒子
                goods = page.locator(".single-products")
                count = await goods.count()
                added = False
                # 遍历每一个商品价格
                for i in range(count):
                    price_text = await goods.nth(i).locator(".productinfo.text-center h2").inner_text()
                    price = float(price_text.replace("Rs.", "").strip())
                    if price < 1000:
                        await goods.nth(i).hover()
                        await goods.nth(i).locator("a.add-to-cart").first.click()
                        await page.wait_for_timeout(1000)
                        await page.get_by_text("Continue Shopping").click()
                        result["steps"].append(f"价格{price}商品已加入购物车")
                        added = True

                if added:
                    result["message"] = "已成功将价格低于1000的商品加入购物车"
                else:
                    result["status"] = "failed"
                    result["message"] = "未找到符合条件的商品"

                # 点击Cart
                await page.locator("#header a[href='/view_cart']").click()


            except Exception as e:
                result["status"] = "failed"
                result["message"] = f"执行异常：{str(e)}"

            print("请手动关闭浏览器窗口，按任意键继续...")
            input()  # 等待用户按任意键

            return result
