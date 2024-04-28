import argparse
import csv
import os
import requests
from bs4 import BeautifulSoup
from xml.etree import ElementTree as ET
from xml.dom import minidom

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
        post_date = post['post_date']

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
            ET.SubElement(item, 'pubDate').text = post_date
            ET.SubElement(item, 'dc:creator').text = 'Author Name'
            ET.SubElement(item, 'guid', {'isPermaLink': 'false'}).text = post_id
            ET.SubElement(item, 'description')
            ET.SubElement(item, 'content:encoded').text = content
            ET.SubElement(item, 'wp:post_date').text = post_date
            ET.SubElement(item, 'wp:post_name').text = post_id
            ET.SubElement(item, 'wp:status').text = 'publish'
            ET.SubElement(item, 'wp:post_type').text = 'post'

    wxr_string = minidom.parseString(ET.tostring(wxr_root)).toprettyxml(indent='  ')

    output_xml = os.path.join(out_dir, 'wordpress_export.xml')
    with open(output_xml, 'w') as file:
        file.write(wxr_string)


parser = argparse.ArgumentParser(
                    prog='substack_to_note',
                    description='Convert Substack export to WordPress WXR format'
)

parser.add_argument('-i', '--in-dir', help='Input directory containing Substack export files')
parser.add_argument('-o', '--out-dir', help='Output directory for WordPress WXR file and images')

args = parser.parse_args()
main(args.in_dir, args.out_dir)

