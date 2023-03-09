import boto3
import time
import urllib
import json
import os 
import nltk
from nltk import sent_tokenize

transcribe_client =  boto3.client('transcribe',
                    aws_access_key_id = 'Write Key_ID',
                    aws_secret_access_key = 'Secerety Key',
                    region_name ='mentionregion')

s3_client = boto3.client('s3',
                    aws_access_key_id = 'Write Key_ID',
                    aws_secret_access_key = 'Secerety Key',
                    region_name ='region')
translate = boto3.client('translate',
                        aws_access_key_id = 'Write Key_ID',
                         aws_secret_access_key = 'Secerety Key',
                         region_name ='mentionregion')

def transcribe_file(job_name, file_uri, transcribe_client):
    transcribe_client.start_transcription_job(
        TranscriptionJobName=job_name,
        Media={'MediaFileUri': file_uri},
        MediaFormat='mp4',
        OutputBucketName='bucketname',
        OutputKey='videos/outputtext/',
        LanguageCode='hi-IN'
        )

    max_tries = 60
    while max_tries > 0:
        max_tries -= 1
        job = transcribe_client.get_transcription_job(TranscriptionJobName=job_name)
        job_status = job['TranscriptionJob']['TranscriptionJobStatus']
        if job_status in ['COMPLETED', 'FAILED']:
            print(f"Job {job_name} is {job_status}.")
            if job_status == 'COMPLETED':
                response = urllib.request.urlopen(job['TranscriptionJob']['Transcript']['TranscriptFileUri'])
                data = json.loads(response.read())
                text = data['results']['transcripts'][0]['transcript']
                print("========== below is output of speech-to-text ========================")
                print(text)
                print("=====================================================================")
                final_document_array = ""
                for sent in sent_tokenize(text):
                    # print(sent)
                    if(sent!=''):

                        translated=translate_text(sent)
                        print(translated)
                        final_document_array+=translated
                        final_document_array+='\n\n'
                        print("=================================================================")
                        # script_emotion(translated)
                print("=====================================================================")
            return text
            # breaks
        else:
            print(f"Waiting for {job_name}. Current status is {job_status}.")
        time.sleep(10)

def translate_text(para):
    result = translate.translate_text(
        Text=para,
        SourceLanguageCode='hi',
        TargetLanguageCode='en'
    )
    return result['TranslatedText']

def script_emotion(script):
    '''from transformers import pipeline
    emotion = pipeline('sentiment-analysis', model='arpanghoshal/EmoRoBERTa')       # method 1
    full_emotion= emotion(script)'''
    
    # from transformers import pipeline                                   # method 2
    classifier = pipeline("text-classification", model="j-hartmann/emotion-english-distilroberta-base", top_k=None)
    full_emotion=classifier(script)
    return full_emotion
def main():
    
    file_uri = 'videoS3 uripath'
    # filename, extension =os.path.splitext(file_path)
    text=transcribe_file('PM114_.mp4', file_uri, transcribe_client)


if __name__ == '__main__':

     main()
 
