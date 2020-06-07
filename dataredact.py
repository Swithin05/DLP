"""Sample app that uses the Data Loss Prevent API to redact the contents of
an image file."""

from __future__ import print_function
import os
import docx2txt
import google.cloud.dlp
from pdfminer3.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer3.converter import TextConverter
from pdfminer3.layout import LAParams
from pdfminer3.pdfpage import PDFPage
from io import StringIO
import mimetypes
import base64
from flask import send_file
#import config


os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "credentials.json"
# Instantiate a client.
dlp = google.cloud.dlp.DlpServiceClient()
project_id = 'tagit-235806'


def redact_images(filename, output_filename):
    # [START dlp_redact_image]
    """Uses the Data Loss Prevention API to redact protected data in an image file.
        Args:
            filename: The path to the file to inspect.
            output_filename: The path to which the redacted image will be written.

        Returns:
            redacted image file.
        """

    image_redaction_configs = [
        {
            "redaction_color": {
                "blue": 0.1,
                "green": 0.1,
                "red": 0.8
            }
        }
    ]

    info_types = [
        {
            "name": "ALL_BASIC"
        }
    ]

    # Construct the configuration dictionary. Keys which are None may
    # optionally be omitted entirely.
    inspect_config = {
        'min_likelihood': 'LIKELY',
        'info_types': info_types,
    }

    # If mime_type is not specified, guess it from the filename.
    mime_guess = mimetypes.MimeTypes().guess_type(filename)
    mime_type = mime_guess[0] or 'application/octet-stream'
    # print(mime_type)
    # Select the content type index from the list of supported types.
    supported_content_types = {
        None: 0,  # "Unspecified"
        'image/jpeg': 1,
        'image/bmp': 2,
        'image/x-ms-bmp': 2,
        'image/png': 3,
        'image/svg': 4,
        'text/plain': 5,
    }
    content_type_index = supported_content_types.get(mime_type, 0)

    # Construct the byte_item, containing the file's byte data.
    print(filename)
    with open(filename, mode='rb') as f:
        byte_item = {'type': content_type_index, 'data': f.read()}

    print(byte_item)
    # Convert the project id into a full resource id.
    parent = dlp.project_path(project_id)

    # Call the API.
    response = dlp.redact_image(
        parent, inspect_config=inspect_config,
        image_redaction_configs=image_redaction_configs,
        byte_item=byte_item)

    # Write out the results.
    with open(output_filename, mode='wb') as f:
        f.write(response.redacted_image)
    print("Wrote {byte_count} to {filename}".format(
        byte_count=len(response.redacted_image), filename=output_filename))

    encoded_output_string = base64.b64encode(response.redacted_image)
    encoded_input_string = base64.b64encode(byte_item['data'])

    return encoded_input_string.decode('utf-8'), encoded_output_string.decode('utf-8')


def redact_text_files(filename):
    with open(filename, 'rb') as txt_file:
        text = txt_file.read()

    byte_item = {'data': text}

    # print(byte_item)

    # Convert the project id into a full resource id.
    parent = dlp.project_path(project_id)

    deidentify_config = {
        "info_type_transformations": {
            "transformations": [
                {
                    "primitive_transformation": {
                        "replace_config": {
                            "new_value": {
                                "string_value": "#########"
                            }
                        }
                    }
                }
            ]
        }
    }

    inspect_config = {
        "info_types": [
            {
                "name": "ALL_BASIC"
            }
        ]
    }

    item = {
        "byte_item": byte_item
    }
    response = dlp.deidentify_content(parent, inspect_config=inspect_config, deidentify_config=deidentify_config,
                                      item=item)

    original = text.decode('utf-8')
    return original, response.item.byte_item.data


def redact_pdf_files(filename):
    """Uses the Data Loss Prevention API to redact protected data in an .pdf file.
        Args:
            project: The Google Cloud project id to use as a parent resource.
            filename: The path to the file to inspect.
            output_filename: The path to which the redacted image will be written.

        Returns:
            text file; the response from the API is printed to the output_file.
        """

    rsrcmgr = PDFResourceManager()
    retstr = StringIO()
    codec = 'utf-8'  # 'utf16','utf-8'
    laparams = LAParams()
    device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
    fp = open(filename, 'rb')
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    password = ""
    maxpages = 0
    caching = True
    pagenos = set()
    for page in PDFPage.get_pages(
            fp,
            pagenos,
            maxpages=maxpages,
            password=password,
            caching=caching,
            check_extractable=True):
        interpreter.process_page(page)
    fp.close()
    device.close()
    txt_file = retstr.getvalue()
    retstr.close()
    # app.logger.info("End of PDF-MINER")
    # print(txt_file)
    txt_file = txt_file.encode("utf8")
    byte_item = {'data': txt_file}
    parent = dlp.project_path(project_id)
    deidentify_config = {
        "info_type_transformations": {
            "transformations": [
                {
                    "primitive_transformation": {
                        "replace_config": {
                            "new_value": {
                                "string_value": "#########"
                            }
                        }
                    }
                }
            ]
        }
    }

    inspect_config = {
        "info_types": [
            {
                "name": "ALL_BASIC"
            }
        ]
    }

    item = {
        "byte_item": byte_item
    }
    response = dlp.deidentify_content(parent, inspect_config=inspect_config, deidentify_config=deidentify_config,
                                      item=item)
    original = txt_file.decode('utf-8')
    return original, response.item.byte_item.data


def redact_docx_files(filename):
    """Uses the Data Loss Prevention API to redact protected data in an .docx file.
    Args:
        project: The Google Cloud project id to use as a parent resource.
        filename: The path to the file to inspect.
        output_filename: The path to which the redacted image will be written.

    Returns:
        text file; the response from the API is printed to the output_file.
    """
    text = docx2txt.process(filename)
    text = text.encode("utf8")

    byte_item = {'data': text}

    print(byte_item)

    # Convert the project id into a full resource id.
    parent = dlp.project_path(project_id)

    deidentify_config = {
        "info_type_transformations": {
            "transformations": [
                {
                    "primitive_transformation": {
                        "replace_config": {
                            "new_value": {
                                "string_value": "#########"
                            }
                        }
                    }
                }
            ]
        }
    }

    inspect_config = {
        "info_types": [
            {
                "name": "ALL_BASIC"
            }
        ]
    }

    item = {
        "byte_item": byte_item
    }
    response = dlp.deidentify_content(parent, inspect_config=inspect_config, deidentify_config=deidentify_config,
                                      item=item)

    original = text.decode('utf-8')
    return original, response.item.byte_item.data


