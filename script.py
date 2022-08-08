from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from datetime import datetime, timedelta
import json 

def parse_time(time_text): 
    return datetime.strptime(time_text, "%I:%M %p")

class TimeElement(): 
    """
    Helper class for Elements that represent potential tee times from the booking page. 
    """
    def __init__(self, element): 
        self.element = element 
        self.time_text = element.get_attribute('text')
        self.time_datetime = parse_time(self.time_text)
    
    def __lt__(self, other): 
        """
        Define the less than operator by the datetime attribute for the TimeElement class 
        """
        return self.time_datetime < other.time_datetime



class TeeTimeBooker(): 
    """
    Main class for booking tee times on the portal, linked from the members website. 
    """
    main_login_url = main_login_url_config
    tee_time_url = tee_time_url_config
    booking_date_url = booking_date_url_config
    
    def __init__(self, username, password): 
        """
        Initalize a new booker with a username and password credential pair. Authenticate with the service to allow for upcoming requests. 
        """
        self.driver = webdriver.Chrome("chromedriver")
        self.driver.get(TeeTimeBooker.main_login_url)
        self.driver.find_element("id","lgUserName").send_keys(username)
        self.driver.find_element("id","lgPassword").send_keys(password)
        self.driver.find_element("id","lgLoginButton").click()
        self.driver.get(TeeTimeBooker.tee_time_url)

    def fetch_available_time_elements(self, desired_date): 
        """
        Find available tee times for a given datetime.date object. Returns the available time objects as a list of TimeElements, sorted.
        """
        self.driver.get(TeeTimeBooker.booking_date_url.format(date = desired_date.strftime("%m/%d/%Y")))
        rows = self.driver.find_elements(By.CLASS_NAME, "rwdTr.noRowColor.ftOdd") + self.driver.find_elements(By.CLASS_NAME, "rwdTr.noRowColor.ftEven")
        valid_time_elements = []
        for row in rows: 
            tagged_elements = row.find_elements(By.TAG_NAME,"a")
            for element in tagged_elements: 
                tee_time_data = json.loads(element.get_attribute('data-ftjson'))
                if 'newreq' in tee_time_data: 
                    valid_time_elements.append(TimeElement(element))
        self.valid_time_elements = sorted(valid_time_elements)

    def get_available_times(self): 
        """
        Method to get the available times in text format as a list from the valid_time_elements attribute set in the fetch_availalbe_time_elements method. 
        """
        try: 
            return [element.time_text for element in self.valid_time_elements]
        except AttributeError: 
            print("No times available - please call fetch available time elements first")

    
    def set_target_time_element(self, target_time, method = 'after'): 
        """
        Given a target time as text, find the closest available time element (based on the method provided) and set it to the object instance. 
        Methods available: 'after' 
        """
        target_datetime = parse_time(target_time)
        time_differences = [potential_time.time_datetime - target_datetime for potential_time in self.valid_time_elements]
        if method == 'after': 
            min_diff = min([diff for diff in time_differences if diff >= timedelta()])
            min_diff_index = time_differences.index(min_diff)
            target_time = self.valid_time_elements[min_diff_index]
        self.target_time_element = target_time 
        print("Target time set to {0}".format(target_time.time_text))

    def book_time(self, fill_tbd = False): 
        """
        Book the target time target_time_element if it's set. 
        """
        try: 
            self.target_time_element.element.click()
            if fill_tbd: 
                pass 
            self.driver.find_element(By.CLASS_NAME, "submit_request_button").click()
        except AttributeError: 
            print("No target time set. Set target time before attempting to book")






desired_date = datetime(2022,8,9).date()

booker = TeeTimeBooker(username, password)
booker.fetch_available_time_elements(desired_date)
booker.get_available_times()

booker.set_target_time_element("9:00 AM")
booker.book_time()

booker.valid_time_elements[0].click()

booker.driver.find_element("id","slot_player_row_1").find_element(By.CLASS_NAME,"ftS-playerNameInput").send_keys("test")


# do this to close the driver 
booker.driver.close()

(datetime.strptime("4:30 AM", "%I:%M %p") - datetime.strptime("5:30 AM", "%I:%M %p")) < (datetime.strptime("6:30 AM", "%I:%M %p") - datetime.strptime("5:30 AM", "%I:%M %p"))
abs(datetime.strptime("6:30 AM", "%I:%M %p") - datetime.strptime("5:30 AM", "%I:%M %p")) > timedelta(minutes=0)