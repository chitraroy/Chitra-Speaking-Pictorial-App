from chalice import Chalice, Response
from chalicelib import storage_service
from chalicelib import recognition_service
from chalicelib import translation_service

#importing polly_service
from chalicelib import polly_service


import base64
import json
import shutil


#####
# chalice app configuration
#####
app = Chalice(app_name='Capabilities')
app.debug = True

#####
# services initialization
#####
storage_location = 'contentcen301148774.aws.ai'
storage_service = storage_service.StorageService(storage_location)
recognition_service = recognition_service.RecognitionService(storage_service)
translation_service = translation_service.TranslationService()

# defined an object of PollyService class
polly_service = polly_service.PollyService()


#####
# RESTful endpoints
#####
@app.route('/')
def index():
    # load index.html manually
    
    # return {"text": "Hello"}
    f = open("../Website/index.html")
    template = f.read()
    f.close()
    return Response(template, status_code=200, headers={"Content-Type":  "text/html"})

@app.route('/images', methods = ['POST'], cors = True)
def upload_image():
    """processes file upload and saves file to storage service"""
    request_data = json.loads(app.current_request.raw_body)
    file_name = request_data['filename']
    file_bytes = base64.b64decode(request_data['filebytes'])

    image_info = storage_service.upload_file(file_bytes, file_name)

    return image_info


@app.route('/images/{image_id}/translate-text', methods = ['POST'], cors = True)
def translate_image_text(image_id):
    """detects then translates text in the specified image"""
    request_data = json.loads(app.current_request.raw_body)
    from_lang = request_data['fromLang']
    to_lang = request_data['toLang']
    
    MIN_CONFIDENCE = 80.0

    text_lines = recognition_service.detect_text(image_id)
    print("--------- text_lines -----")
    print(text_lines)

    translated_lines = []
    for line in text_lines:
        # check confidence
        if float(line['confidence']) >= MIN_CONFIDENCE:
            translated_line = translation_service.translate_text(line['text'], from_lang, to_lang)
            
            # getting the translated text audio
            audio_file = polly_service.read_out_translate_text(translated_line['translatedText'], output_format="mp3")
            
            # copy file to web directory
            audio_info = storage_service.upload_mp3(audio_file["filePath"], audio_file["fileName"])
            
            
            translated_lines.append({
                'text': line['text'],
                'translation': translated_line,
                'boundingBox': line['boundingBox'],
                'audioFile': audio_file,
                'audio_info': audio_info
            })
            
            

    return translated_lines