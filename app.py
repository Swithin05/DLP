from flask import Flask, request, make_response
import os
import main
from werkzeug.utils import secure_filename
import json
from flask_cors import CORS, cross_origin

app = Flask(__name__)
CORS(app)


@app.route('/')
def homepage():
    return 'Dlp service is working on endpoint dlp'


@app.route('/dlp', methods=['POST'])
@cross_origin(origin='http://localhost:8080')
def upload():
    """
    dzuuid – Unique identifier of the file being uploaded
    dzchunkindex – Which block number we are currently on
    dztotalfilesize – The entire file’s size
    dzchunksize – The max chunk size set on the frontend (note this may be larger than the actual chunck’s size)
    dztotalchunkcount – The number of chunks to expect
    dzchunkbyteoffset – The file offset we need to keep appending to the file being  uploaded
    """

    if request.method == 'POST':
        files = request.files.getlist('file')
        print(files)
        response_dict = {}
        response_list = []
        for file in files:
            print(file)
            path_to_save = '/tmp/dlp_service'
            save_path = os.path.join(path_to_save, secure_filename(file.filename))

            # if os.path.exists(save_path) and current_chunk == 0:
            if os.path.exists(save_path):
                os.remove(save_path)
                # 400 and 500s will tell dropzone that an error occurred and show an error
                # return make_response(('File already exists', 200))
            else:
                main.create_user_directory(path_to_save)

            try:
                with open(save_path, 'ab') as f:
                    f.write(file.stream.read())
            except OSError:

                app.logger.error('Could not write to file')
                return make_response(("Not sure why,"
                                      " but we couldn't write the file to disk", 500))

            response = main.processing(save_path, file.filename)

            response_list.append(response)
        response_dict['result'] = response_list

        return json.dumps(response_dict), 200


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=9000)
