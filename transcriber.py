#!/usr/bin/env python3

import json
import time
import boto3
import os.path
import urllib
from botocore.exceptions import ClientError

sleep_time_main = 15 * 60
config_path = "/var/lib/transcriber/"
processed = os.path.join(config_path, "processed.json")
settings_path = os.path.join(config_path, "settings.json")

def read_settings():
    settings = {}
    with open(settings_path) as json_file:
        settings = json.load(json_file)
        json_file.close()
    return settings

def read_processed_files():
    processed_files = {}
    with open(processed) as json_file:
        processed_files = json.load(json_file)
        json_file.close()
    return processed_files

def write_processed_files(processed_files):
    with open(processed, 'w') as json_file:
        json.dump(processed_files, json_file)
        json_file.close()

def check_settings_file():
    if not os.path.exists(config_path):
        os.makedirs(config_path)
    if not os.path.isfile(settings_path):
        with open(settings_path, 'w') as json_file:
            json.dump({}, json_file)
            json_file.close()

def check_processed_files():
    if not os.path.isfile(processed):
        write_processed_files({})

def upload_file(filename):
    s3_client = boto3.client('s3')
    obj_name = filename
    path, obj_name = os.path.split(filename)
    try:
        response = s3_client.upload_file(filename, s3_bucket, obj_name)
    except ClientError as e:
        logging.error(e)
        return False
    return True

def start_transcribe_job(filename):
    transcribe = boto3.client('transcribe')

    job_name = filename.replace(" ", "_")
    
    uri = "https://s3-%s.amazonaws.com/%s/%s" % ("us-west-2", s3_bucket, filename)
    transcribe.start_transcription_job(
        TranscriptionJobName=job_name,
        Media={'MediaFileUri': uri},
        MediaFormat='wav',
        LanguageCode='en-US'
    )
    return job_name

def do_processing(filename):
    # send file
    upload_file(recordings_path + filename)
    print("upload complete")

    # create and send job to transcriber
    jobname = start_transcribe_job(filename)

    # write status
    processed_files = read_processed_files()
    processed_files[filename] = jobname
    write_processed_files(processed_files)


def start_jobs_for_new_files():
    processed_files = read_processed_files()

    # Determine the work to be done
    current_files = os.listdir(recordings_path)
    current_files = filter(lambda x: x.endswith('wav'), current_files)
    for f in current_files:
        if f not in processed_files:
            if (f != ".tmp.wav"):
                print("New file detected:", f)
                do_processing(f)

def save_transcript_json(transcriptURI, name):
    # print(json.dumps(transcriptURI))
    response = urllib.request.urlopen(transcriptURI)
    data = response.read()
    
    transcript_json = json.loads(data)

    transcript_path = os.path.join(recordings_path, "transcripts")

    transcript_path_json = os.path.join(transcript_path, name+".json")
    transcript_path_text = os.path.join(transcript_path, name+".txt")
    
    if not os.path.exists(transcript_path):
        os.makedirs(transcript_path)

    with open(transcript_path_json, 'w') as json_file:
        json.dump(transcript_json, json_file)
        json_file.close()
    print("Created transcript:", transcript_path_json)

    transcript_text = ""
    for text in transcript_json["results"]["transcripts"]:
        transcript_text += text["transcript"]

    with open(transcript_path_text, 'w') as text_file:
        text_file.write(transcript_text)
        text_file.close()

    print("Created transcript:", transcript_path_text)

def check_jobs_for_transcripts():
    transcribe = boto3.client('transcribe')

    processed_files = read_processed_files()
    for filename in processed_files:
        if (processed_files[filename] != "COMPLETED"):
            status = transcribe.get_transcription_job(TranscriptionJobName=processed_files[filename])
            if status['TranscriptionJob']['TranscriptionJobStatus'] in ['COMPLETED', 'FAILED']:
                uri = status['TranscriptionJob']['Transcript']['TranscriptFileUri']
                name, ext = os.path.splitext(filename)
                save_transcript_json(uri, name)
                processed_files[filename] = status['TranscriptionJob']['TranscriptionJobStatus']
                write_processed_files(processed_files)

while True:
    check_settings_file()
    settings = read_settings()
    # recordings_path = "/home/endako/Recordings/"
    # s3_bucket = "munka.recordings"

    # Scan for new files
    check_processed_files()
    start_jobs_for_new_files()

    # Check for updates on currently processing files
    check_jobs_for_transcripts()

    # Wait for the next polling cycle
    time.sleep(sleep_time_main)