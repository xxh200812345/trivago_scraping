from webdriver_manager.chrome import ChromeDriverManager

path = ChromeDriverManager().install()
print(f"✅ 实际下载的 ChromeDriver 路径是：{path}")
