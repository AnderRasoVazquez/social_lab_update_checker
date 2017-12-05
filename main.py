import requests
import time
from typing import Dict, List
from bs4 import BeautifulSoup
from subprocess import call
from getpass import getpass

print("### SOCIAL LAB UPDATE CHECKER ###")
print("This program will check for friend requests and messages updates.")
print()

URL: str = 'http://es.sociallab.es/profile/show/?id=6'  # home page doesn't work
USERNAME: str = input("Enter Social Lab username: ")
PASS: str = getpass("Enter Social Lab password: ")
MINUTES: int = int(input("Enter update interval [minutes]: "))
WAIT_TIME: int = 60 * MINUTES


def lists_are_different(list_one: List[int], list_two: List[int]) -> bool:
    """
    Return true if lists are equal
    :param list_one:
    :param list_two:
    """
    different: bool = False
    try:
        for i in range(len(list_one)):
            if list_one[i] != list_two[i]:
                different = True
                break
    except IndexError:
        different = True
    return different


def get_payload(token: str) -> Dict[str, str]:
    """
    Return a dict with login data.
    :param token:
    :return:
    """
    return {
        'signin[username]': USERNAME,
        'signin[password]': PASS,
        'signin[_csrf_token]': token
    }


def get_menu_info(html: BeautifulSoup, href: str) -> str:
    """
    Get text of requested href.
    :param html:
    :param href:
    :return:
    """
    return html.find('a', {'href': href}).find('div', {'class': 'float_r'}).text


def parse_result(result: str) -> List[int]:
    """
    From (3/0) to [3, 0]
    :param result:
    """
    for character in ['(', ')']:
        result = result.replace(character, '')
    return [int(x) for x in result.split('/')]


def main() -> None:
    """
    Main function.
    """
    prev_friends: List[int] = None
    prev_messages: List[int] = None

    while True:
        session = requests.session()
        page: requests.models.Response = session.get(URL)
        html_login: BeautifulSoup = BeautifulSoup(page.text, 'html.parser')
        token: str = html_login.find('input', {'id': 'signin__csrf_token'}).get('value')
        payload_login = get_payload(token)
        home_page: requests.models.Response = session.post(URL, data=payload_login)
        html: BeautifulSoup = BeautifulSoup(home_page.text, 'html.parser')

        friend_requests_info = parse_result(get_menu_info(html, '/profile/requests'))
        messages_info = parse_result(get_menu_info(html, '/profile/messages'))

        print(time.strftime("%Y/%m/%d %H:%M:%S"), "Checking...")

        if not prev_friends and not prev_messages:
            prev_friends = list(friend_requests_info)
            prev_messages = list(messages_info)
        else:
            change_in_friends = lists_are_different(prev_friends, friend_requests_info)
            change_in_messages = lists_are_different(prev_messages, messages_info)
            if change_in_friends or change_in_messages:
                call(['notify-send', 'Social Lab',
                      'You have updates!', '-i', 'terminal', '-t', str(1000*60*60)])
                input("Press ENTER to continue")
                prev_friends = list(friend_requests_info)
                prev_messages = list(messages_info)
                print(time.strftime("%Y/%m/%d %H:%M:%S"), "Checking...")

        time.sleep(WAIT_TIME)


if __name__ == "__main__":
    main()
