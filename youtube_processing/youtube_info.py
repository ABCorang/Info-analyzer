# %%
from youtube_transcript_api import YouTubeTranscriptApi
from typing import List


def get_transcript_from_video_id(video_id: str, language: str) -> List[dict]:
    transcripts = YouTubeTranscriptApi.get_transcript(video_id, languages=[language])
    return transcripts

def retrive_text_from_list(transcirpts_list: List[dict]) -> str:
    text = ''
    for sciript in transcirpts_list:
        text += sciript['text']
    return f'Content: {text}'

def convert_format(transcripts: List) -> List[str]:
    formatted_transcripts = []
    for transcript in transcripts:
        hours = int(transcript['start'] // 3600)
        minutes = int((transcript['start'] % 3600) // 60)
        seconds = int(transcript['start'] % 60)
        formatted_transcripts.append(f'{hours}時間{minutes}分{seconds}秒\n{transcript["text"]}\n\n')

    return formatted_transcripts
