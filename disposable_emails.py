# -*- coding: utf-8 -*-
"""
Created on Sat Feb  3 19:10:37 2018

@author: Steffan
"""

import json
import random
import uuid
import os
import inflect
import names
import requests

def fetch_domains():
    request = requests.get('https://app.getnada.com/api/v1/domains')
    if request.status_code == 'ok':
        domains = json.loads(request.content)
        fh = open('domains.txt', 'w')
        fh.write(domains)
        fh.close()
        print('\nPossible domains:')
        print(domains)
    else:
        print('Could not fetch a list of domains!')


def create_address():
    if not os.path.exists('domains.txt'):
        fetch_domains()

    domains = []
    fh = open('domains.txt', 'r')
    for line in fh:
        domains.append(line.strip())

    try:
        # Use the line below if you don't want to install the names package
        #username = uuid.uuid4().hex[0:10]
        username = names.get_full_name().replace(' ', '.').lower()
        domain = random.choice(domains)
        address = '{}@{}'.format(username, domain)
        print('Generated email address: {}'.format(address))
        fh = open('used_addresses.txt', 'a')
        fh.write('\n{}'.format(address))
        fh.close()
    except:
        raise ValueError('Could not generate an address')

    return address


def fetch_email(address, number=1):
    base_url = 'https://app.getnada.com/api/v1/'
    inbox_url = 'inboxes/{}'.format(address)
    email_url = 'messages/'

    request = requests.get('{}{}'.format(base_url, inbox_url))
    if not request.status_code == 200:
        request.close()
        raise ValueError('Inboxes request status code is {}'.format(request.status_code))

    inbox_json = json.loads(request.content)
    request.close()

    emails = []
    for num in range(min(len(inbox_json), number)):
        uid = inbox_json[num]['uid']
        request = requests.get('{}{}{}'.format(base_url, email_url, uid))
        if not request.status_code == 200:
            request.close()
            raise ValueError('Email request status code is {}'.format(request.status_code))

        email_json = json.loads(request.content)
        request.close()

        emails.append({'subject':email_json['s'], 'body':email_json['text']})

    print('\nPrinting a total of {} emails\n'.format(len(emails)))

    for ind, email in enumerate(emails):
        print('****************************************************')
        print('{} email:'.format(inflect.engine().ordinal(ind+1)))
        print('Subject: {}'.format(email['subject']))
        print('Body:\n{}'.format(email['body'].strip()))
        print('****************************************************\n')

    return emails


def main():
    choice = input('Do you want to create [C] a new email address, read [R] '
                   'email from an existing one or fetch a list of possible '
                   'email domains [D]?: ')
    print('')
    if choice == 'C':
        create_address()
    elif choice == 'R':
        address = input('Please type the address that you want to check email '
                        'on. If left empty, the address that was most recently'
                        ' created will be checked:\n')
        print('')
        if address == '':
            try:
                fh = open('used_addresses.txt', 'r')
                address = fh.readlines()[-1]
                fh.close()
            except:
                raise ValueError('Couldn\'t parse an email address')

        print('Will check emails at {}\n'.format(address))
        number = input('How many emails do you want to check? Leave empty to '
                       'check only the most recent email: ')
        print('')
        if number == '':
            number = 1
        else:
            number = int(number)

        fetch_email(address, number)
    elif choice == 'D':
        fetch_domains()


if __name__ == '__main__':
    main()
