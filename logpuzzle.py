#!/usr/bin/env python2
"""
Logpuzzle exercise

Copyright 2010 Google Inc.
Licensed under the Apache License, Version 2.0
http://www.apache.org/licenses/LICENSE-2.0

Google's Python Class
http://code.google.com/edu/languages/google-python-class/

Given an apache logfile, find the puzzle urls and download the images.

Here's what a puzzle url looks like:
10.254.254.28 - - [06/Aug/2007:00:13:48 -0700] "GET /~foo/puzzle-bar-aaab.jpg
HTTP/1.0" 302 528 "-" "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US;
rv:1.8.1.6) Gecko/20070725 Firefox/2.0.0.6"

"""
__author__ = "Janelle Kuhns with help from Janell Hyuck and stackoverflow: https://stackoverflow.com/questions/5967500/how-to-correctly-sort-a-string-with-a-number-inside"

import os
import re
import sys
import urllib
import argparse


def read_urls(filename):
    """Returns a list of the puzzle urls from the given log file,
    extracting the hostname from the filename itself.
    Screens out duplicate urls and returns the urls sorted into
    increasing order."""

    url_list = []
    # get a list of puzzle urls
    url_list = get_url_list(filename)
    # extract hostname from filename
    hostname = extract_hostname_from_filename(filename)
    # combine hostname and url in url_list
    combined_url_list = combine_hostname_and_filename(hostname, url_list)
    # screen out duplicate urls
    combined_url_list = list(set(combined_url_list))
    #sort urls in increasing order
    sorted_url_list = sort_url_list(combined_url_list)
    return sorted_url_list

def get_url_list(filename):
    """ Return the list of urls that have the word puzzle in them """
    puzzle_url_list = []
    with open(filename, 'r') as url_file:
        for line in url_file:
            match_url = re.search('/puzzle/', line)
            if match_url:
                extracted_url = extract_url_from_log_entry(line)
                puzzle_url_list.append(extracted_url)
    return puzzle_url_list


def extract_url_from_log_entry(line):
    #finds each line that contains "puzzle"
    extracted_url = re.findall('GET (\\S*) HTTP', line)
    return extracted_url[0]

def extract_hostname_from_filename(filename):
    #extracts the hostname from each file
    hostname = re.findall('_(\\S*)', filename)
    return hostname[0]


def combine_hostname_and_filename(hostname, url_list):
    #concatenates the hostname and filename
    combined_url_list = []
    for path in url_list:
        combined_url_list.append("http://" + hostname + path)
    return combined_url_list


def sort_url_list(combined_url_list):
    #find and sort all filenames between -8 and -4 indexes
    combined_url_list.sort( key = lambda combined_url_list: combined_url_list[-8:-4])
    return combined_url_list


def download_images(img_urls, dest_dir):
    """Given the urls already in the correct order, downloads
    each image into the given directory.
    Gives the images local filenames img0, img1, and so on.
    Creates an index.html in the directory
    with an img tag to show each local image file.
    Creates the directory if necessary.
    """
    # check for dir and if not, make one
    check_for_directory_or_make_one(dest_dir)

    # download images into a directory
    # give images local filenames ie., img0, img1, etc
    download_images_to_directory(img_urls, dest_dir) 

    # create an index.html file in the directory with img tag to show each image file
    create_html_file(img_urls, dest_dir)


def check_for_directory_or_make_one(dest_dir):
    if os.path.isdir(dest_dir):
        return
    else:
        os.mkdir(dest_dir)
        return

def download_images_to_directory(img_urls, dest_dir):
    counter = 0
    for img_url in img_urls:
        #"./destdir/img0.jpg" - What I want end result to look like
        #"./ + destdir + img + counter"
        path_to_img_url = "./" + dest_dir + "/img" + str(counter) + ".jpg"
        urllib.urlretrieve(img_url, path_to_img_url)
        counter += 1
        print("Image is downloading: " + img_url)

def create_html_file(img_urls, dest_dir):
    for root, dirs, files in os.walk(dest_dir):
        image_tags = []
        for image_file in img_urls:
            image_tags.append('<img src="{0}">'.format(image_file))
        
    with open(dest_dir + "/index.html", 'w') as index_html:
        index_html.write("<html><body>{0}</body></html>".format(''.join(image_tags)))




def sort_numbers_in_files(file_string):
    return int(file_string) if file_string.isdigit() else file_string


def sorted_numbers_key(file_list):
    '''
    alist.sort(key=natural_keys) sorts in human order
    http://nedbatchelder.com/blog/200712/human_sorting.html
    (See Toothy's implementation in the comments)
    '''
    return [ sort_numbers_in_files(c) for c in re.split(r'(\d+)', file_list) ]



def sort_these_files(file_list):
    file_list.sort(key = sorted_numbers_key)
    #sort_files = re.findall('img(\\d*)[.jpg]', [file for file in file_list])
    return file_list
    

def create_parser():
    """Create an argument parser object"""
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--todir',
                        help='destination direction for downloaded images')
    parser.add_argument('logfile', help='apache logfile to extract urls from')

    return parser


def main(args):
    """Parse args, scan for urls, get images from urls"""
    parser = create_parser()

    if not args:
        parser.print_usage()
        sys.exit(1)

    parsed_args = parser.parse_args(args)

    img_urls = read_urls(parsed_args.logfile)

    if parsed_args.todir:
        download_images(img_urls, parsed_args.todir)
    else:
        print('\n'.join(img_urls))


if __name__ == '__main__':
    main(sys.argv[1:])
