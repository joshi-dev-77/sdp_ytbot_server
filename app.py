from transformers import AutoModelForQuestionAnswering, AutoTokenizer, pipeline
from flask import Flask, request, jsonify
from flask_cors import CORS
from youtube_transcript_api import YouTubeTranscriptApi
from pytube import YouTube

global captions_string
captions_string = ""
app = Flask(__name__)
CORS(app)


@app.route('/process_video', methods=['POST'])
def process_video():
    global captions_string  # Declare the variable as global
    
    try:
        # Access video ID from the request
        data = request.json
        video_id = data.get('video_id')

        # Validate video ID (you might want to check if it's a valid ID)
        if video_id is None:
            raise ValueError('Video ID is missing in the request.')

        def get_youtube_captions(video_url):
            try:
                # Get YouTube video
                yt = YouTube(video_url)

                # Get available captions
                captions = YouTubeTranscriptApi.get_transcript(yt.video_id)

                # Store captions in a string
                captions_text = ""

                # Concatenate captions into a single string
                for caption in captions:
                    captions_text += f"{caption['text']} "

                return captions_text.strip()

            except Exception as e:
                print(f"An error occurred: {e}")
                return None

        youtube_url = video_id
        # Example usage for captions
        captions_string = get_youtube_captions(youtube_url)

        response_data = {'message': 'Captions retrieved successfully'}
        return jsonify(response_data)

    except Exception as e:
        return jsonify({'error': str(e)})
    

@app.route('/process_output', methods=['POST'])
def process_output():
    try:
        data = request.json
        question = data.get('question')
        
        if question is None:
            raise ValueError('Question is not mentioned in the request.')
        
        model_name = "deepset/roberta-base-squad2"

        # Get predictions
        nlp = pipeline('question-answering', model=model_name, tokenizer=model_name)
        QA_input = {
            'question': question,
            'context': captions_string
        }
        res = nlp(QA_input)
        reply = res['answer']
        
        response_answer = {'answer': f'{reply}'}
        return jsonify(response_answer)
    
    except Exception as e:
        return jsonify({'error': str(e)})