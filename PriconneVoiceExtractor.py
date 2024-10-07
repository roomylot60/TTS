# import
import os
import json
import requests
from pprint import pprint
from bs4 import BeautifulSoup


def download_file(url, path):
    try:
        response = requests.get(url)
        with open(path, 'wb') as file:
            file.write(response.content)
    except Exception as e:
        print(e)


def main(character_name, output_folder, max_voice=None, max_story=None, min_storyid=None, max_storyid=None, replace_player=None, leave_newline=False, folder_storyid=False):
    # Voice・Caption
    voices = []

    # Story URL
    story_url = 'https://redive.estertion.win/story/data/'

    # Voice URL
    voice_url = 'https://redive.estertion.win/sound/story_vo/'

    # キャラクター名 (ALL と指定すると全て取得する)
    character_name = character_name.rstrip()

    # 出力フォルダ
    output_folder = output_folder.rstrip() + '/'

    # ボイスの最大取得数 (未指定なら無制限)
    voice_maxcount = max_voice

    # ストーリーの最大取得数 (未指定なら無制限)
    story_maxcount = max_story

    # 取得を開始する Story ID
    min_storyid = min_storyid

    # 取得を開始する Story ID
    max_storyid = max_storyid

    # キャプション内の {player} を置換する (未指定なら置換しない)
    replace_player = replace_player

    # キャプション内の改行を残す (未指定なら False)
    leave_newline = leave_newline

    # 小分けのフォルダ名を Story ID にする (未指定なら False)
    folder_storyid = folder_storyid
    
    print()
    print('Character Name: ' + character_name)
    print('Output Folder: ' + output_folder)
    print()

    # ストーリーリストを取得
    stories_list_html = requests.get(voice_url)
    stories_list = BeautifulSoup(stories_list_html.text, 'html.parser')

    # Story ID ごとに実行
    story_count = 0
    for stories_list_link in stories_list.select('pre a'):

        # Story ID
        story_id = stories_list_link.get_text(strip=True).replace('/', '')

        # ../ はパス
        if story_id == '..':
            continue

        # 取得を開始する Story ID になるまでスキップ
        if (min_storyid is not None and int(story_id) < int(min_storyid)):
            continue

        # 取得を終了する Story ID を超えた場合
        if (max_storyid is not None and int(story_id) > int(max_storyid)):
            print()
            print('Notice: 取得を終了する Story ID を超えました。取得を終了します。', end='\n\n')
            break

        # カウントする
        story_count += 1

        # ストーリーの最大取得数を超えた場合
        if (story_maxcount is not None and story_count >= story_maxcount):
            print()
            print('Notice: ストーリーの最大取得数を超えました。取得を終了します。', end='\n\n')
            break

        # ボイスの最大取得数を超えた場合
        if (voice_maxcount is not None and len(voices) >= voice_maxcount):
            print()
            print('Notice: ボイスの最大取得数を超えました。取得を終了します。', end='\n\n')
            break
    
        print('Story ID: ' + story_id)
        print()

        # ストーリーを取得
        try:
            stories = requests.get(story_url + story_id + '.json').json()
        except Exception:
            print('Notice: ストーリーが見つかりません。スキップします。', end='\n\n')
            continue

        # アイテムごとに実行
        for story in stories:
            if story['name'] == 'bust':
                voices.append({
                    'story_id': story_id,
                    'character': '',
                    'voice': '',
                    'caption': '',
                })

            if story['name'] == 'vo':
                if voices[-1]['voice'] == '':
                    voices[-1]['voice'] = story['args'][0] + '.m4a'

            if story['name'] == 'print':
                voices[-1]['character'] = story['args'][0]
                voices[-1]['caption'] += story['args'][1]
                voices[-1]['caption'] = voices[-1]['caption'].replace(' ', '')
                if replace_player is not None:
                    voices[-1]['caption'] = voices[-1]['caption'].replace('{player}', replace_player)
                if not leave_newline:
                    voices[-1]['caption'] = voices[-1]['caption'].replace('\n', '　')

            if story['name'] == 'touch':
                if len(voices) > 0:
                    if character_name == voices[-1]['character'] or character_name.upper() == 'ALL':
                        if voices[-1]['voice'] != '':
                            print('Character: ' + voices[-1]['character'])
                            print('Voice: ' + voices[-1]['voice'])
                            print('Caption: ' + voices[-1]['caption'])

                            if folder_storyid:
                                subfolder = story_id
                            else:
                                subfolder = voices[-1]['character']
                            os.makedirs(output_folder + subfolder, exist_ok=True)

                            url = voice_url + story_id + '/' + voices[-1]['voice']
                            download_file(url, output_folder + subfolder + '/' + voices[-1]['voice'])

                            with open(output_folder + subfolder + '/' + voices[-1]['voice'].replace('.m4a', '.txt'), mode='w', encoding='utf-8') as file:
                                file.write(voices[-1]['caption'])

                            if voice_maxcount is not None and len(voices) >= voice_maxcount:
                                break

                            print()
                        else:
                            print('Character: ' + voices[-1]['character'])
                            print('Caption: ' + voices[-1]['caption'])
                            print('Notice: ボイスがストーリー内に見つかりません。スキップします。')
                            del voices[-1]
                    else:
                        del voices[-1]

    print()
    print('Extracted Voices: ')
    print('Character: ' + character_name + ' Count: ' + str(len(voices)), end='\n\n')

    for voice in voices:
        print('Story ID: ' + voice['story_id'])
        print('Voice: ' + voice['voice'])
        print('Caption: ' + voice['caption'])
        print()

    print('Extracted. Finish.')
    print()


# Example: Jupyter Notebook에서 사용
character_name = "ALL"
output_folder = "./output"
max_voice = 10  # 최대 10개의 보이스 다운로드
max_story = 10  # 최대 5개의 스토리 다운로드
min_storyid = None
max_storyid = None
replace_player = "Hero"
leave_newline = False
folder_storyid = False

main(character_name, output_folder, max_voice, max_story, min_storyid, max_storyid, replace_player, leave_newline, folder_storyid)