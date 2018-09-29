import cv2
import time
from io import BytesIO
import PIL.Image as image
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

origin_bg_path = '../pic/bg.jpg'
origin_fbg_path = '../pic/fbg.jpg'
merge_bg_path = '../pic/merged.jpg'
merge_fbg_path = '../pic/fmerged.jpg'

cut_image_path = '../pic/cut.jpg'
bin_bg_path = '../pic/bin_bg.jpg'
opencv_bg_path = '../pic/opencv_bg.jpg'


def simulate():
    browser = webdriver.Chrome(executable_path="C:\Program Files (x86)\Google\Chrome\Application\chromedriver")
    browser.implicitly_wait(5)
    wait = WebDriverWait(browser, 10)
    browser.get("http://www.geetest.com/type/")
    browser.find_elements_by_xpath("//div[@class='products-content']/ul/li")[1].click()
    button = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "geetest_radar_tip")))
    browser.find_elements_by_class_name("geetest_radar_tip")[1].click() if len(
        browser.find_elements_by_class_name("geetest_radar_tip")) > 1 else browser.find_element_by_class_name(
        "geetest_radar_tip").click()
    time.sleep(2)
    return cut_gt_window_image(browser)


# 直接页面截取图片/不太行/居然这才行
def cut_gt_window_image(browser):
    image_div = browser.find_element_by_class_name("geetest_window")
    location = image_div.location
    size = image_div.size
    top, bottom, left, right = location['y'], location['y'] + size['height'], location['x'], location['x'] + size[
        'width']
    screen_shot = browser.get_screenshot_as_png()
    screen_shot = image.open(BytesIO(screen_shot))
    captcha = screen_shot.crop((left, top, right, bottom))
    captcha = captcha.convert('RGB')
    captcha.save(cut_image_path)
    return browser


def get_x_point(bin_img_path=''):
    img = image.open(bin_img_path).load()
    for x_cur in range(60, 260):
        for y_cur in range(0, 160):
            if img[x_cur, y_cur] == 0:
                if judge_position(img, x_cur, y_cur):
                    return x_cur
                else:
                    continue


def judge_position(img, x_cur, y_cur):
    return True


# 二值化
def get_bin_image(img_path='', save_path='', t_h=160, t_l=60):
    img = image.open(img_path)
    img = img.convert('L')
    table = []
    for i in range(256):
        if i in range(t_l, t_h):
            table.append(0)
        else:
            table.append(1)
    binary = img.point(table, '1')
    binary.save(save_path)


# 模拟滑动
def btn_slide(t_browser, x_offset=0):
    slider = t_browser.find_element_by_class_name("geetest_slider_button")
    ActionChains(t_browser).click_and_hold(slider).perform()
    ActionChains(t_browser).move_by_offset(x_offset, yoffset=0).perform()
    ActionChains(t_browser).release().perform()
    time.sleep(2)
    t_browser.close()


# 混乱图片还原
def merge_img(img_path='', target=''):
    im = image.open(img_path)
    to_image = image.new('RGB', (260, 160))
    dx = 12
    dy = 80
    x = 0
    img_map = {1: 18, 2: 17, 3: 15, 4: 16, 5: 22, 6: 21, 7: 14, 8: 13, 9: 10, 10: 9, 11: 19, 12: 20, 13: 2, 14: 1,
               15: 6, 16: 5, 17: 26, 18: 25, 19: 23, 20: 24, 21: 7, 22: 8, 23: 3, 24: 4, 25: 11, 26: 12}
    while x <= 300:
        y = 0
        while y <= 80:
            from_img = im.crop((x, y, x + dx, y + dy))
            second_line = img_map[(x / 12) if ((x / 12) % 2) else (x / 12 + 2)] - 1
            loc = ((img_map[x / 12 + 1] - 1) * 10 if y else second_line * 10, abs(y - dy))
            to_image.paste(from_img, loc)
            y += dy
        x += dx
    to_image = to_image.convert('L')
    to_image.save(target)
    return to_image


# opencv处理图片
def opencv_show(img_path=''):
    img_gray = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
    gradX = cv2.Sobel(img_gray, ddepth=cv2.CV_32F, dx=1, dy=0, ksize=-1)
    gradY = cv2.Sobel(img_gray, ddepth=cv2.CV_32F, dx=0, dy=1, ksize=-1)
    img_gradient = cv2.subtract(gradX, gradY)
    img_gradient = cv2.convertScaleAbs(img_gradient)

    blurred = cv2.blur(img_gradient, (9, 9))
    (_, thresh) = cv2.threshold(blurred, 90, 255, cv2.THRESH_BINARY)

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (25, 25))
    closed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
    closed = cv2.erode(closed, None, iterations=4)
    closed = cv2.dilate(closed, None, iterations=4)
    cv2.imwrite(opencv_bg_path, closed)


t_browser = simulate()
get_bin_image(cut_image_path, bin_bg_path)
opencv_show(cut_image_path)
# x = get_x_point(bin_bg_path)
# btn_slide(t_browser, x)

# bg = merge_img(origin_bg_path, merge_bg_path)
# fbg = merge_img(origin_fbg_path, merge_fbg_path)
# bg.paste('#000000', (x, 0, x + 1, 160))
# bg.save('../pic/lll.jpg')
