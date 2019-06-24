import argparse
import datetime
import time
import glob
import pickle
from collections import OrderedDict
from scraping_common import *
from selenium.webdriver.common.action_chains import ActionChains


def get_scrape_url(sport):
    scrape_urls = {'MLB':'https://www.fantasyalarm.com/mlb/projections',
        'NFL':'https://www.fantasyalarm.com/nfl/projections',
        'NBA':'https://www.fantasyalarm.com/nba/projections',
        'PGA':'https://www.fantasyalarm.com/pga/projections'}
    return scrape_urls[sport]


def extract_slate_sport(driver, sport, source):
    """Selects the function specified for sport.
    """
    scrape_functions = {
        'MLB':globals()['extract_slate_MLB'],
        'NFL':globals()['extract_slate_NFL'],
        'NBA':globals()['extract_slate_NBA'],
        'PGA':globals()['extract_slate_PGA']
    }

    # Testing
    res = ''
    data = ''
    if sport == 'PGA':
        res = scrape_functions[sport](driver, source)
        data = create_data_for_database(res, sport)
    else:
        res = scrape_functions[sport](driver, source)
        data = create_data_for_database(res, sport)
    pass


def check_cookies_exists(filename):
    """Check if a cookies.pkl file is already on folder.
    Returns True if so.
    """
    os.chdir(os.path.dirname(os.path.realpath(__file__)))
    if os.path.isfile(filename):
        return True
    return False


def load_cookies(driver, filename):
    """Loads cookies from file and adds it to WebDriver.
    """
    cookies = pickle.load(open(filename, 'rb'))
    for cookie in cookies:
        driver.add_cookie(cookie)
    print('Cookies Loaded.')

def save_cookies(driver, filename):
    """Saves the webdriver cookies to a file.
    """
    pickle.dump(driver.get_cookies(), open(filename, 'wb'))
    print('Cookies Saved.')


def create_data_for_database(data, sport):
    """Create the format to save on database.
    """
    DB_data = dict()

    DB_data['sports_type'] = sport
    #DB_data['slate_title'] = slate_title
    DB_data['time'] = datetime.datetime.now()
    DB_data['projection_data'] = data

    return DB_data


def login_fantasy_alarm(driver, sport):
    """Makes login to fantasy sports.
    """
    email = 'johnscotthayse@gmail.com'
    passwd = 'fantasyfun2019'

    wait = WebDriverWait(driver, 10)
    driver.get(get_scrape_url(sport))

    try:
        skip_button = driver.find_element_by_xpath(
            '//a[contains(@class, "introjs-button introjs-skipbutton")]')
        ActionChains(driver).move_to_element(skip_button).click().perform()
        time.sleep(0.5)
        print('Clicked')
    except NoSuchElementException:
        print("Error skip button.")

    try:
        login_dropdown_button = wait.until(
            EC.presence_of_element_located((By.XPATH,
            '//a[contains(@class, " dropdown-toggle")]'))
        )
        ActionChains(driver).move_to_element(login_dropdown_button)\
            .click().perform()
        time.sleep(0.5)
    except NoSuchElementException:
        print("Error skip button.")
    
    try:
        email_textfield = driver.find_element_by_xpath(
            '//input[contains(@name, "email")]')
        ActionChains(driver).move_to_element(email_textfield).click().send_keys(email)\
            .perform()
        time.sleep(0.5)
    except NoSuchElementException:
        print('Error inserting email')

    try:
        passwd_textfield = driver.find_element_by_xpath(
            '//input[contains(@name, "password")]')
        ActionChains(driver).move_to_element(passwd_textfield).click().send_keys(passwd)\
            .perform()
        time.sleep(0.5)
    except NoSuchElementException:
        print('Error inserting email')
    
    try:
        login_button = driver.find_element_by_xpath(
            '//button[contains(@class, "btn btn-block blue uppercase") and '\
                'contains(@type, "submit")]')
        ActionChains(driver).move_to_element(login_button).click().perform()
        time.sleep(10)
    except NoSuchElementException:
        print('Error login.')
    print('Logged in.')


def open_fantasy_alarm(driver, sport):
    """Makes login into fantasyalarm.com if a cookie file doesn't exist on
    the same folder.
    """
    cookie_existing = check_cookies_exists('driver_cookies.pkl')

    if(cookie_existing):
        driver.get(get_scrape_url(sport))
        load_cookies(driver, 'driver_cookies.pkl')
    else:
        login_fantasy_alarm(driver, args['sport'])
        save_cookies(driver, 'driver_cookies.pkl')


def extract_slate_NFL(driver, source, slate):
    """Extracts the slates list from sport.
    """
    wait = WebDriverWait(driver, 10)
    actions = ActionChains(driver)

    if source == 'FanDuel':
        driver.get('https://www.fantasyalarm.com/nfl/projections/daily'\
            '/hitters/FD/{}'.format(slate))
    if source == 'DraftKings':
        driver.get('https://www.fantasyalarm.com/nfl/projections/daily'\
            '/hitters/DK/{}'.format(slate))
    
    try:
        csv_button = wait.until(
            EC.presence_of_element_located((By.XPATH, 
            "//span[contains(text(), 'CSV')]/parent::a"))
        )
        actions.move_to_element(csv_button).click().perform()
        time.sleep(3)
    except NoSuchElementException:
        print('Download button not found.')
    except Exception as e:
        print('Not downloaded due to:\n{}'.format(e))
        
    slate_data = extract_csv_data()

    return slate_data
        

def extract_slate_NBA(driver, source, slate):
    """Extracts the slates list from sport.
    """
    wait = WebDriverWait(driver, 10)
    actions = ActionChains(driver)

    if source == 'FanDuel':
        driver.get('https://www.fantasyalarm.com/nba/projections/daily'\
            '/hitters/FD/{}'.format(slate))
    if source == 'DraftKings':
        driver.get('https://www.fantasyalarm.com/nba/projections/daily'\
            '/hitters/DK/{}'.format(slate))
    
    try:
        csv_button = wait.until(
            EC.presence_of_element_located((By.XPATH, 
            "//span[contains(text(), 'CSV')]/parent::a"))
        )
        actions.move_to_element(csv_button).click().perform()
        time.sleep(3)
    except NoSuchElementException:
        print('Download button not found.')
    except Exception as e:
        print('Not downloaded due to:\n{}'.format(e))
        
    slate_data = extract_csv_data()

    return slate_data


def extract_slate_MLB(driver, source):
    """Extracts the slates list from sport.
    """
    wait = WebDriverWait(driver, 10)
    slates_data = dict()
    current_url = ''
    if source == 'FanDuel':
        driver.get('https://www.fantasyalarm.com/mlb/projections/daily'\
            '/hitters/FD/')
        current_url = driver.current_url
    if source == 'DraftKings':
        driver.get('https://www.fantasyalarm.com/mlb/projections/daily'\
            '/hitters/DK/')
        current_url = driver.current_url
    time.sleep(2)
    slates = extract_slates_names(driver)

    for slate in slates:
        driver.get(current_url+slate)
        try:
            csv_button = wait.until(
                EC.presence_of_element_located((By.XPATH, 
                "//span[contains(text(), 'CSV')]/parent::a"))
            )
            ActionChains(driver).move_to_element(csv_button).click().perform()
            time.sleep(3)
        except NoSuchElementException:
            print('Download button not found.')
        except Exception as e:
            print('Not downloaded due to:\n{}'.format(e))
        
        slate_data = extract_csv_data()
        slates_data[slate] = slate_data

    return slates_data


def extract_slate_PGA(driver, source):
    """Extracts the slates list from sport.
    """
    wait = WebDriverWait(driver, 10)

    if source == 'FanDuel':
        driver.get('https://www.fantasyalarm.com/pga/projections/daily/FD/')
    
    if source == 'DraftKings':
        driver.get('https://www.fantasyalarm.com/pga/projections/daily/DK/')

    try:
        csv_button = wait.until(
            EC.presence_of_element_located((By.XPATH, 
            "//span[contains(text(), 'CSV')]/parent::a"))
        )
        ActionChains(driver).move_to_element(csv_button).click().perform()
        time.sleep(2)
    except NoSuchElementException:
        print('Download button not found.')
    except Exception as e:
        print('Not downloaded due to:\n{}'.format(e))
    
    # Extracts data from file and deletes it
    slate_data = extract_csv_data()
    return slate_data


def extract_slates_names(driver):
    """Looks for the slate on the current sport and returns a list with their names.
    """
    names = list()

    try:
        slates_div = driver.find_element_by_xpath('//div[contains(text(), "Slates")]')
    except NoSuchElementException:
        print('Error locating slates div.')

    try:
        names = [name.text.strip(' \n').split(' ')[0] for name in slates_div\
            .find_elements_by_xpath('./parent::div//following-sibling::a')]
    except Exception as e:
        print('Error extracting slates names: \n{}'.format(e))
    return names


def extract_csv_data():
    """Opens downloaded file, loads its content to Python object 
    and delete it.
    """
    data = list()
    os.chdir(os.path.dirname(os.path.realpath(__file__)))
    for file in glob.glob("*.csv"):
        with open(file, mode='r', encoding='utf8') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            for raw in csv_reader:
                data.append(raw)
        os.remove(file)
    return data



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=
        'Module that extracts slates list and projection data.')
    parser.add_argument('-s', '--sport', metavar='S', type=str,
        help='Determines the sport to extract data from.')
    args = vars(parser.parse_args())
    
    driver = get_geckodriver()
    driver.set_window_position(0, 0)
    driver.set_window_size(1920, 1080)

    try:
        open_fantasy_alarm(driver, args['sport'])
        extract_slate_sport(driver, args['sport'], 'FanDuel')
    except Exception as e:
        print('Stopped due to: \n{}'.format(e))
    finally:
        driver.close()