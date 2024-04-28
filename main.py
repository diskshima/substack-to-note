import argparse
import csv
import os
import requests
import pytz
from urllib.parse import quote
from datetime import datetime
from bs4 import BeautifulSoup
from xml.etree import ElementTree as ET
from xml.dom import minidom

def to_wp_date(dt: datetime) -> str:
    return dt.strftime('%Y-%m-%d %H:%M:%S')


def to_pubDate_format(dt: datetime) -> str:
    return dt.strftime('%a, %d %b %Y %H:%M:%S %z')


def cdata(text=''):
    element = ET.Element('![CDATA[')
    element.text = text
    return element


def main(in_dir: str, out_dir: str):
    posts_csv = os.path.join(in_dir, 'posts.csv')

    with open(posts_csv, 'r') as file:
        reader = csv.DictReader(file)
        posts = list(reader)

    wxr_root = ET.Element('rss', {'version': '2.0'})
    wxr_root.set('xmlns:excerpt', 'http://wordpress.org/export/1.2/excerpt/')
    wxr_root.set('xmlns:content', 'http://purl.org/rss/1.0/modules/content/')
    wxr_root.set('xmlns:wfw', 'http://wellformedweb.org/CommentAPI/')
    wxr_root.set('xmlns:dc', 'http://purl.org/dc/elements/1.1/')
    wxr_root.set('xmlns:wp', 'http://wordpress.org/export/1.2/')

    channel = ET.SubElement(wxr_root, 'channel')

    for post in posts:
        post_id = post['post_id']
        title = post['title']
        post_date = datetime.fromisoformat(post['post_date'])
        post_date_ja = post_date.astimezone(pytz.timezone('Asia/Tokyo'))

        html_file = os.path.join(in_dir, f"posts/{post_id}.html")

        if os.path.exists(html_file):
            with open(html_file, 'r') as file:
                html_content = file.read()

            # Parse the HTML content
            soup = BeautifulSoup(html_content, 'html.parser')

            images_dir = os.path.join(out_dir, f"images/{post_id}")
            os.makedirs(images_dir, exist_ok=True)

            for img in soup.find_all('img'):
                img_url = img['src']
                img_filename = os.path.basename(img_url)
                img_path = os.path.join(images_dir, img_filename)

                response = requests.get(img_url)
                with open(img_path, 'wb') as file:
                    file.write(response.content)

                # img['src'] = img_path

            content = str(soup)

            # Create the item element for the post
            item = ET.SubElement(channel, 'item')
            ET.SubElement(item, 'title').text = title
            ET.SubElement(item, 'link').text = f"https://example.com/posts/{post_id}"
            ET.SubElement(item, 'dc:creator').text = ''
            ET.SubElement(item, 'guid', {'isPermaLink': 'false'}).text = post_id
            ET.SubElement(item, 'description')
            subEl = ET.SubElement(item, 'content:encoded')
            subEl.append(cdata(content))
            ET.SubElement(item, 'excerpt:encoded')
            ET.SubElement(item, 'pubDate').text = to_pubDate_format(post_date_ja)
            ET.SubElement(item, 'wp:post_date').text = cdata(to_wp_date(post_date_ja))
            ET.SubElement(item, 'wp:post_date_gmt').text = cdata(to_wp_date(post_date))
            ET.SubElement(item, 'wp:post_modified').text = cdata(to_wp_date(post_date_ja))
            ET.SubElement(item, 'wp:post_modified_gmt').text = cdata(to_wp_date(post_date))
            ET.SubElement(item, 'wp:comment_status').text = cdata('open')
            ET.SubElement(item, 'wp:ping_status').text = cdata('open')
            ET.SubElement(item, 'wp:post_name').text = cdata(quote(post_id))
            ET.SubElement(item, 'wp:status').text = 'publish'
            ET.SubElement(item, 'wp:post_parent').text = '0'
            ET.SubElement(item, 'wp:menu_order').text = '0'
            ET.SubElement(item, 'wp:post_type').text = cdata('post')
            ET.SubElement(item, 'wp:post_password').text = cdata('')
            ET.SubElement(item, 'wp:is_sticky').text = '0'


    wxr_string = minidom.parseString(ET.tostring(wxr_root)).toprettyxml(indent='  ')

    output_xml = os.path.join(out_dir, 'wordpress_export.xml')
    with open(output_xml, 'w') as file:
        file.write(wxr_string)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
                        prog='substack_to_note',
                        description='Convert Substack export to WordPress WXR format'
    )

    parser.add_argument('-i', '--in-dir', help='Input directory containing Substack export files')
    parser.add_argument('-o', '--out-dir', help='Output directory for WordPress WXR file and images')

    args = parser.parse_args()
    main(args.in_dir, args.out_dir)
