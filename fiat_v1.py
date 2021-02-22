from selenium import webdriver, common
from webdriver_manager.chrome import ChromeDriverManager
import time
from selenium.webdriver.common.by import By
from datetime import datetime
import urllib3
import os
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import WebDriverException

class Parser:
    def __init__(self, vin):
        self.vin = vin
        self.list_with_1 = list()
        self.list_with_2 = list()
        self.list_with_3 = list()
        self.res_list = list()
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--incognito")

        self.driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=chrome_options)
        self.data = {"data": True}

        self.cnt_1 = 1
        self.cnt_2 = 1
        self.cnt_3 = 1
        self.len_list_with_2 = int()
        self.len_list_with_3 = int()
        self.end_file = BaseException("Закончились пункты меню")
        self.session_expire = BaseException("ОБРЫВ СЕССИИ")

    def open_site(self):

        hostname = 'linkentry-euro.fiat.com/pages/home/'
        proxy_username = ""
        proxy_password = ""

        self.driver.get(f"https://{proxy_username}:{proxy_password}@{hostname}/")
        user = self.driver.find_element_by_xpath('//*[@id="ctl00_ContentPlaceHolder1_UsernameTextBox"]')
        user.send_keys(proxy_username)
        pw = self.driver.find_element_by_xpath('//*[@id="ctl00_ContentPlaceHolder1_PasswordTextBox"]')
        pw.send_keys(proxy_password)
        self.driver.find_element_by_xpath('//*[@id="LoginFullBox"]/div[3]').click()
        time.sleep(2)
        self.driver.find_element_by_css_selector('#ext-gen18').click()
        # # time.sleep(2)
        # self.driver.find_element_by_xpath('//*[@id="ext-gen18"]').click()
        # time.sleep(3)
        Link = self.driver.find_element_by_css_selector('#ext-gen174')
        # time.sleep(2)
        webdriver.ActionChains(self.driver).move_to_element(Link).perform()
        self.driver.find_element_by_css_selector('#ext-gen196').click()
        action = webdriver.ActionChains(self.driver)
        time.sleep(4)
        self.driver.get('http://aftersales.fiat.com/tempario/home.aspx?mercatoID=IT&languageID=ru-RU')
        time.sleep(2)
        vincode = self.driver.find_element_by_xpath('//*[@id="id_cerca_vin-inputEl"]')
        time.sleep(10)
        vincode.send_keys(f"{self.vin}", Keys.RETURN)
        time.sleep(3)

    def create_list(self, what_list):
        for row in self.driver.find_elements_by_css_selector("#gridview-1026-table"):
            for item in row.find_elements_by_tag_name("td"):
                if what_list == 'list_with_1':
                    self.list_with_1.append(item.text)
                elif what_list == 'list_with_2':
                    self.list_with_2.append(item.text)
                elif what_list == 'list_with_3':
                    self.list_with_3.append(item.text)
        time.sleep(10)

    def last_click(self):
        time.sleep(2)
        for item in self.driver.find_elements_by_tag_name("td"):
            if item.text != "":
                self.res_list.append(item.text)

    def step0(self):
        print(self.vin)
        time.sleep(2)

        if len(self.list_with_1) == 0:
            self.create_list("list_with_1")

        if self.cnt_1 > len(self.list_with_1) / 2:

            self.write_into_file(self.res_list)
            self.data["data"] = False
            raise ValueError
        if self.data["data"]:

            time.sleep(2)

            style = self.driver.find_element_by_xpath(
                f"/html/body/div[3]/div/div[2]/div[1]/div/div/div[1]/div/div/div[2]/div/table/tbody/tr[{self.cnt_1}]/td[2]").get_attribute('style')
            if 'color' in style:

                self.cnt_1 += 1

            self.driver.find_element_by_xpath(
                f'/html/body/div[3]/div/div[2]/div[1]/div/div/div[1]/div/div/div[2]/div/table/tbody/tr[{self.cnt_1}]/td[2]/div').click()
            self.data["data"] = False
            time.sleep(2)
            self.step1()


    def step1(self):

        if len(self.list_with_2) == 0:
            self.create_list("list_with_2")
        self.len_list_with_2 = len(self.list_with_2) / 2
        time.sleep(2)
        self.driver.find_element_by_xpath(
            f'/html/body/div[3]/div/div[2]/div[1]/div/div/div[1]/div/div/div[2]/div/table/tbody/tr[{self.cnt_2}]/td[2]/div').click()
        time.sleep(2)

        self.step2()

    def step2(self):

        self.list_with_3.clear()
        time.sleep(2)
        self.create_list("list_with_3")
        self.len_list_with_3 = int(len(self.list_with_3) / 2)
        for item in range(1, self.len_list_with_3 + 1):
            self.driver.find_element_by_xpath(
                f'/html/body/div[3]/div/div[2]/div[1]/div/div/div[1]/div/div/div[2]/div/table/tbody/tr[{item}]/td[2]/div').click()
            time.sleep(2)

            #  self.driver.find_element_by_css_selector('#button_sottogruppi-btnIconEl').click()
            self.last_click()
            self.driver.find_element_by_css_selector('#button_1_ssgruppi-btnIconEl').click()
            time.sleep(2)
        self.driver.find_element_by_css_selector('#button_sottogruppi-btnIconEl').click()
        self.cnt_2 += 1

        if self.cnt_2 >= int(self.len_list_with_2):
            self.driver.find_element_by_css_selector('#button_gruppi-btnIconEl').click()
            self.cnt_1 += 1
            self.data["data"] = True
            self.list_with_2.clear()
            self.cnt_2 = 1
            self.cnt_3 = 1
            self.step0()
        self.step1()

    def write_into_file(self, data_from_site):
        string = ''''''
        if not os.path.isfile("vin_result1.txt"):
            open("vin_result1.txt", "w", encoding='utf-8').close()
        with open("vin_result1.txt", "a", encoding='utf-8') as vin_result:
            vin_result.write(self.vin + "\n")

            code = 0
            work_name = 1
            normative = 2

            dlinna = len(data_from_site)
            try:
                while True:
                    string += data_from_site[code] + ";" + data_from_site[work_name] + ";" + data_from_site[
                        normative] + "\n"
                    code += 4
                    normative += 4
                    work_name += 4
                    dlinna -= 4
            except IndexError:
                vin_result.write(string)
                time.sleep(120)


    def main_work(self):
        try:
            self.open_site()
            time.sleep(2)
            self.step0()
            time.sleep(5)
        except ValueError:
            print("next model")

        except:
            self.driver.quit()
            self.res_list.clear()
            self.cnt_1 = 1
            self.cnt_2 = 1
            self.cnt_3 = 1
            self.list_with_1.clear()
            self.list_with_2.clear()
            self.list_with_3.clear()
            self.__init__(self.vin)
            self.main_work()

        finally:
            self.driver.quit()


print(f"start time is : {datetime.now()}")

with open('./vin.txt', 'r') as file_with_vincode:
    for line in file_with_vincode:
        child = Parser(f'{line}').main_work()
print("Программа заершена")
print("DONE!!!", datetime.now())
