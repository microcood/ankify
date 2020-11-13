import tarfile
import re
import shelve
import requests
import shutil
import tempfile
from urllib.request import urlopen
from io import BytesIO
from xml.etree import ElementTree
from os import makedirs

NS = '{http://www.tei-c.org/ns/1.0}'
DICT_API = 'https://freedict.org/freedict-database.xml'
LANG_RELEASE = lambda x: "dictionary[@name='deu-{}']/release".format(x)
ENTRY = './/{}entry'.format(NS)
ORTH = './{}form/{}orth'.format(NS, NS)
QUOTE = './/{}quote'.format(NS)

def create_dictionary(language):
    api = ElementTree.parse(urlopen(DICT_API))
    dict_url = None
    for release in api.getroot().findall(LANG_RELEASE(language)):
        if release.attrib['URL'].endswith('src.tar.xz'):
            dict_url = release.attrib['URL']
            break
    if not dict_url:
        return
    with urlopen(dict_url) as response:
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            shutil.copyfileobj(response, tmp_file)
    archive = tarfile.open(tmp_file.name)
    for file_info in archive:
        if file_info.name.endswith('.tei'):
            file_stream = archive.extractfile(file_info)
            xml_file = ElementTree.parse(file_stream)
            entries = xml_file.findall(ENTRY)

            makedirs('dicts', exist_ok=True)
            d = shelve.open('dicts/deu-{}'.format(language))
            for entry in entries:
                    key = entry.find(ORTH).text
                    # remove everything in brackets
                    key = re.sub(r'\(.*\)\s', '', key).lower()
                    value = ', '.join(a.text for a in entry.findall(QUOTE))
                    d[key] = value
            d.close()

create_dictionary('rus')
create_dictionary('eng')


