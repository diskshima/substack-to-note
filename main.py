import argparse
import csv
import html
import os
import pytz
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote
from datetime import datetime
from lxml import etree

DC_NAMESPACE = 'http://purl.org/dc/elements/1.1/'
EXCERPT_NAMESPACE = 'http://wordpress.org/export/1.2/excerpt/'
CONTENT_NAMESPACE = 'http://purl.org/rss/1.0/modules/content/'
WFW_NAMESPACE = 'http://wellformedweb.org/CommentAPI/'
WP_NAMESPACE = 'http://wordpress.org/export/1.2/'

DC = '{%s}' % DC_NAMESPACE
EXCERPT = '{%s}' % EXCERPT_NAMESPACE
CONTENT = '{%s}' % CONTENT_NAMESPACE
WFW = '{%s}' % WFW_NAMESPACE
WP = '{%s}' % WP_NAMESPACE

def to_wp_date(dt: datetime) -> str:
    return dt.strftime('%Y-%m-%d %H:%M:%S')

def to_pubDate_format(dt: datetime) -> str:
    return dt.strftime('%a, %d %b %Y %H:%M:%S %z')

def main(in_dir: str, out_dir: str):
    posts_csv = os.path.join(in_dir, 'posts.csv')

    with open(posts_csv, 'r') as file:
        reader = csv.DictReader(file)
        posts = list(reader)

    wxr_root = etree.Element('rss', version='2.0', nsmap={
        'excerpt': EXCERPT_NAMESPACE,
        'content': CONTENT_NAMESPACE,
        'wfw': WFW_NAMESPACE,
        'dc': DC_NAMESPACE,
        'wp': WP_NAMESPACE,
    })

    channel = etree.SubElement(wxr_root, 'channel')

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
            escaped_content = html.escape(content)

            item = etree.SubElement(channel, 'item')
            etree.SubElement(item, 'title').text = title
            etree.SubElement(item, 'link').text = f"https://example.com/posts/{post_id}"
            etree.SubElement(item, DC + 'creator').text = ''
            etree.SubElement(item, 'guid', isPermaLink='false').text = post_id
            etree.SubElement(item, 'description')
            etree.SubElement(item, CONTENT + 'encoded').text = etree.CDATA(escaped_content)
            etree.SubElement(item, EXCERPT + 'encoded')
            etree.SubElement(item, 'pubDate').text = to_pubDate_format(post_date_ja)
            etree.SubElement(item, WP + 'post_date').text = etree.CDATA(to_wp_date(post_date_ja))
            etree.SubElement(item, WP + 'post_date_gmt').text = etree.CDATA(to_wp_date(post_date))
            etree.SubElement(item, WP + 'post_modified').text = etree.CDATA(to_wp_date(post_date_ja))
            etree.SubElement(item, WP + 'post_modified_gmt').text = etree.CDATA(to_wp_date(post_date))
            etree.SubElement(item, WP + 'comment_status').text = etree.CDATA('open')
            etree.SubElement(item, WP + 'ping_status').text = etree.CDATA('open')
            etree.SubElement(item, WP + 'post_name').text = etree.CDATA(quote(post_id))
            etree.SubElement(item, WP + 'status').text = etree.CDATA('publish')
            etree.SubElement(item, WP + 'post_parent').text = '0'
            etree.SubElement(item, WP + 'menu_order').text = '0'
            etree.SubElement(item, WP + 'post_type').text = etree.CDATA('post')
            etree.SubElement(item, WP + 'post_password').text = etree.CDATA('')
            etree.SubElement(item, WP + 'is_sticky').text = '0'

    wxr_string = etree.tostring(wxr_root, pretty_print=True, xml_declaration=True, encoding='UTF-8')

    output_xml = os.path.join(out_dir, 'wordpress_export.xml')
    with open(output_xml, 'wb') as file:
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
