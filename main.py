import os
import dataredact


def processing(path, filename):
    if filename.endswith('.pdf'):
        input_text, output_text = dataredact.redact_pdf_files(path)
        # input_text = input_text.decode('utf-8')
        output_text = output_text.decode('utf-8')
        return {filename + ' Original': input_text, filename + ' Redacted': output_text}

    for image_extension in ['jpg', 'png', 'jpeg', 'bmp', 'svg']:
        if filename.lower().endswith(image_extension):
            create_user_directory('/tmp/dlp_service/redacted')
            input_binary, output_binary = dataredact.redact_images(path, '/tmp/dlp_service/redacted/' + filename)
            return {'Original Image': input_binary, 'Redacted Image': output_binary, 'mjmetype': 'image/'+image_extension}

    if filename.lower().endswith('.docx'):
        input_text, output_text = dataredact.redact_docx_files(path)
        output_text = output_text.decode('utf-8')
        return {filename+' Original': input_text, filename+' Redacted': output_text}

    if filename.lower().endswith('.txt'):
        input_text, output_text = dataredact.redact_text_files(path)
        output_text = output_text.decode('utf-8')
        return {filename + ' Original': input_text, filename + ' Redacted': output_text}


def create_user_directory(directory):
    """
    This method creates specific user directory in tmp folder
    """

    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
    except OSError:
        print('Directory already exists')
