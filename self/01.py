import requests
from lxml import html
import time
import json

keywords = ['month']
genres = ['DM0000']
flag = {'하락':-1, '상승':1}


def fmake_file(keyword, genre):
    output_file_name = f'melon_chart_{keyword}_{genre}_{time.strftime("%y%m%d_%H%M%S")}.txt'
    output_file = open(output_file_name, 'w', encoding='utf-8')
    output_file.write(f'순위\t가수\t제목\t변동\t좋아요\t발매일\t장르\t댓글수\t곡정보url\t팬수\n')
    output_file.close()
    return output_file_name

def fwrite_contents(rank, singer, title, change, like, release_date, song_genre, n_of_comment, song_url,n_of_fan, output_file_name):
    output_file = open(output_file_name, 'a', encoding='utf-8')
    output_file.write(f'{rank}\t{singer}\t{title}\t{change}\t{like}\t{release_date}\t{song_genre}\t{n_of_comment}\t{song_url}\t{n_of_fan}\n')
    output_file.close()

def fcrawl_contents(keyword, genre, output_file_name):
    url = f'https://www.melon.com/chart/{keyword}/index.htm?classCd={genre}'
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Safari/537.36'}
    html_req = requests.get(url, headers=headers)
    tree = html.fromstring(html_req.content)
    bodies1 = tree.xpath("//tr[@id='lst50']")
    bodies2 = tree.xpath("//tr[@id='lst100']")
    bodies = bodies1 + bodies2
    results = []
    for body in bodies:
        # 곡 제목
        title = body.xpath(".//div[@class='wrap_song_info']/div[@class='ellipsis rank01']/span/a/text()")
        title = title[0].strip().replace('\n', ' ').replace('\t', ' ').replace('\r', ' ')

        # 가수
        singer = body.xpath(".//div[@class='wrap_song_info']/div[@class='ellipsis rank02']/span/a/text()")[0]

        # 순위
        rank = body.xpath(".//span[@class='rank ']/text()")[0]

        # 곡 순위 변동
        song_num = body.xpath(".//a[@class='btn button_icons type03 song_info']/@href")[0].split('(\'')[1][:-3]
        song_url = f'https://www.melon.com/song/detail.htm?songId={song_num}'
        change_tmp = body.xpath(".//td")[2].xpath(".//div/span/@title")[0].split()
        if change_tmp[1] == '진입':
            change = 100 - int(rank)
        elif change_tmp[1] == '동일':
            change = 0
        else:
            val = int(change_tmp[0].split('단')[0])
            change = val * flag[change_tmp[1]]

        # 좋아요
        like_url = f'https://www.melon.com/commonlike/getSongLike.json?contsIds={song_num}'
        response = requests.get(like_url, headers=headers)
        like = json.loads(response.text)['contsLike'][0]['SUMMCNT']

        # --------------------- depth ---------------------
        song_num = body.xpath(".//a[@class='btn button_icons type03 song_info']/@href")[0].split('(\'')[1][:-3]
        song_url = f'https://www.melon.com/song/detail.htm?songId={song_num}'
        song_html_req = requests.get(song_url, headers=headers)
        song_tree = html.fromstring(song_html_req.content)

        singer_num = body.xpath(".//div[@class='ellipsis rank02']/a/@href")[0].split('(\'')[1]


        # 발매일
        meta_data = song_tree.xpath(
            "//div[@class='section_info']/div[@class='wrap_info']/div[@class='entry']/div[@class='meta']/dl/dd")
        release_date = meta_data[1].text

        # 곡 장르
        song_genre = meta_data[2].text

        # 댓글 수
        n4c_url = f'https://www.melon.com/song/songReviewCnt.json?songId={song_num}'
        response = requests.get(n4c_url, headers=headers)
        n_of_comment = json.loads(response.text)['reviewValidCmtCnt']

        singer_num = body.xpath(".//div[@class='ellipsis rank02']/a/@href")[0].split('(\'')[1][:-3]
        singer_url = f'https://www.melon.com/artist/getArtistFanNTemper.json?artistId={singer_num}'
        response = requests.get(singer_url, headers=headers)

        n_of_fan = json.loads(response.text)['fanInfo']['SUMMCNT']
        results.append((rank, singer, title, change, like, release_date, song_genre, n_of_comment, song_url, n_of_fan))
        fwrite_contents(rank, singer, title, change, like, release_date, song_genre, n_of_comment, song_url, n_of_fan,
                        output_file_name)
    return results

def fmain():
    for keyword in keywords:
        for genre in genres:
            output_file_name = fmake_file(keyword, genre)
            results = fcrawl_contents(keyword, genre, output_file_name)
            print(results)
            time.sleep(4)

fmain()
