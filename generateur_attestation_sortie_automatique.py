#!/usr/bin/env python3
#-*- coding: utf8 -*-

import time
import base64
import urllib.request
from datetime import datetime, timedelta

from selenium import webdriver
import selenium


def get_file_content_chrome(browser, uri):
    """ Use selenium [browser] to download blob [uri].

    - Source https://stackoverflow.com/a/47425305/
    """
    result = browser.execute_async_script("""
        var uri = arguments[0];
        var callback = arguments[1];
        var toBase64 = function(buffer){for(var r,n=new Uint8Array(buffer),t=n.length,a=new Uint8Array(4*Math.ceil(t/3)),i=new Uint8Array(64),o=0,c=0;64>c;++c)i[c]="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/".charCodeAt(c);for(c=0;t-t%3>c;c+=3,o+=4)r=n[c]<<16|n[c+1]<<8|n[c+2],a[o]=i[r>>18],a[o+1]=i[r>>12&63],a[o+2]=i[r>>6&63],a[o+3]=i[63&r];return t%3===1?(r=n[t-1],a[o]=i[r>>2],a[o+1]=i[r<<4&63],a[o+2]=61,a[o+3]=61):t%3===2&&(r=(n[t-2]<<8)+n[t-1],a[o]=i[r>>10],a[o+1]=i[r>>4&63],a[o+2]=i[r<<2&63],a[o+3]=61),new TextDecoder("ascii").decode(a)};
        var xhr = new XMLHttpRequest();
        xhr.responseType = 'arraybuffer';
        xhr.onload = function(){ callback(toBase64(xhr.response)) };
        xhr.onerror = function(){ callback(xhr.status) };
        xhr.open('GET', uri);
        xhr.send();
    """, uri)
    if type(result) == int :
        raise Exception("Request failed with status %s" % result)
    return base64.b64decode(result)

# bytes = get_file_content_chrome(browser, "blob:https://developer.mozilla.org/7f9557f4-d8c8-4353-9752-5a49e85058f5")

def download_attestation(details, headless=True, delta=None, number=None):
    """ Fill the form on https://media.interieur.gouv.fr/deplacement-covid-19/ with details, and save the PDF attestation."""
    download_name = None
    try:
        firefoxOptions = webdriver.FirefoxOptions()
        if headless:
            firefoxOptions.headless = True

        # disable cache, see https://stackoverflow.com/a/47093059/
        profile = webdriver.FirefoxProfile()
        profile.set_preference("browser.cache.disk.enable", False)
        profile.set_preference("browser.cache.memory.enable", False)
        profile.set_preference("browser.cache.offline.enable", False)
        profile.set_preference("network.http.use-cache", False)

        browser = webdriver.Firefox(profile, options=firefoxOptions)
        browser.delete_all_cookies()

        URL = "https://media.interieur.gouv.fr/deplacement-covid-19/"
        browser.get(URL)
        browser.get(URL)
        browser.get(URL)
        browser.get(URL)

        # keep this check, to be sure that the downloaded webpage was the correct one, update if needed!
        page_source = browser.page_source
        page_source_100 = '<html class="fontawesome-i2svg-active fontawesome-i2svg-complete" lang="fr"><head><meta charset="UTF'
        assert page_source[:100] == page_source_100

        def click_update_alert():
            # click on '#update-alert'
            try:
                print("Clicking on '#update-alert'...")
                update_alert = browser.find_element_by_id("update-alert")
                # time.sleep(120*60)
                try:
                    update_alert.click()
                except:
                    print("Failed to click '#update-alert'...")
            except selenium.common.exceptions.NoSuchElementException:
                print("Failed to locate '#update-alert'...")

        click_update_alert()

        # Now, let's fill with details from the input dictionnary details (see below for example)
        # - field-firstname
        # - field-lastname
        # - field-birthday
        # - field-placeofbirth
        # - field-address
        # - field-city
        # - field-zipcode
        # - field-datesortie : may be missing
        # - field-heuresortie : may be missing

        # automatically add current date/time if not present
        now = datetime.now()
        if delta is not None:
            print(f"Using delta = {delta}")
            now = now + delta
        if 'datesortie' not in details:
            details['datesortie'] = f"{now:%Y-%m-%d}"
        if 'heuresortie' not in details:
            details['heuresortie'] = f"{now:%H:%M}"

        # fill #field-XXX with YYY, read from the input dictionnary
        for fieldname, value in details.items():
            hidden_value = '*' * len(value)
            print(f"Filling the form '{fieldname}' with value '{hidden_value}'...")
            input_field = browser.find_element_by_id(f"field-{fieldname}")
            input_field.clear()
            input_field.send_keys(value)
        # this check is useful, to be sure that we don't try to generate a PDF
        # if an input field was not correctly filled
        for fieldname, value in details.items():
            print(f"Checking value of the form '{fieldname}'...")
            input_field = browser.find_element_by_id(f"field-{fieldname}")
            its_new_value = input_field.get_attribute("value")
            if its_new_value != value:
                print(f"Error: the form '{fieldname}' has value '{its_new_value}' != '{value}'.")

        click_update_alert()

        # click on '#checkbox-achats'
        print("Clicking on '#checkbox-achats'...")
        checkbox_achats = browser.find_element_by_id("checkbox-achats")
        checkbox_achats.click()

        click_update_alert()

        # click on '#generate-btn'
        print("Clicking on 'generate-btn'...")
        generate_btn = browser.find_element_by_id("generate-btn")
        # TODO how to configure the path of the file to save?
        generate_btn.click()

        # now wait 3 seconds (probably not mandatory...)
        print("Now sleeping 3 seconds...")
        time.sleep(3)

        # check that there is a new <a href="..." download="..."> link
        # <a href="blob:https://media.interieur.gouv.fr/712fc9d2-6967-4e63-b9c3-870175b6258f" download="attestation-2020-10-31_12-40.pdf"></a>
        all_a_links = browser.find_elements_by_css_selector("a")
        # window.document.getElementsByTagName("a")
        for link in all_a_links:
            try:
                href = link.get_attribute("href")
                download = link.get_attribute("download")
                if download:
                    print(f"Found a new <a href='...'> link! with href = {href}")
                    print(f"  and it has a download = {download}")
                    print("Downloading the file and save it!")
                    # 1st try...
                    bytes_download = get_file_content_chrome(browser, href)
                    if number is not None:
                        download_name = download.replace(".pdf", f"_{number}.pdf")
                    else:
                        download_name = download
                    with open(download_name, "wb") as download_file:
                        download_file.write(bytes_download)
                    print(f"The PDF file {download_name} is now saved!")
                    ## 2nd try... this was NOT working
                    # download_name = download.replace(".pdf", "_2.pdf")
                    #urllib.request.urlretrieve(href, download_name)
            except:
                pass
    # let's close the browser and finish
    finally:
        try:
            browser.close()
        except:
            pass
    return download_name


def send_attestations():
    now = datetime.now()
    today = f"{now:%Y-%m-%d}"
    # TODO write this without needing IPython
    # !ls -larth *pdf
    # !echo CP attestation-$(date '+%Y-%m-%d')_*.pdf ${Szam}attestations/$(date '+%Y-%m-%d')/
    # !CP attestation-$(date '+%Y-%m-%d')_*.pdf ${Szam}attestations/$(date '+%Y-%m-%d')/


import json
import sys

if __name__ == '__main__':
    args = sys.argv
    # TODO use a real command line argument parser
    not_headless = False
    if "DEBUG" in args:
        not_headless = True
        args = [arg for arg in args if arg != "DEBUG"]
    if "--not-headless" in args:
        not_headless = True
        args = [arg for arg in args if arg != "--not-headless"]

    filename = args[1] if len(args) > 1 else "details_lilian.json"
    with open(filename, "r") as f:
        details = json.load(f)

    for number, delta in enumerate([
        timedelta(),
        timedelta(hours=1),
        timedelta(hours=2),
        timedelta(hours=3),
    ]):
        download_attestation(details, headless=not not_headless, delta=delta, number=number)
    # TODO write this without needing IPython
    # send_attestations()
