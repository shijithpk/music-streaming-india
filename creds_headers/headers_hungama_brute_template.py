import copy

headers_search = {
    'authority': 'www.hungama.com',
    'accept': 'application/json, text/javascript, */*; q=0.01',
    'accept-language': 'en-US,en;q=0.9',
    'cookie': 'XXXXXXXXXXXXXX',
    'referer': 'https://www.hungama.com/music/',
    'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="101", "Google Chrome";v="101"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Linux"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.41 Safari/537.36',
    'x-requested-with': 'XMLHttpRequest',
}

params_search = {
    '_country': 'IN',
}

headers_specific_album_temp = copy.deepcopy(headers_search)
del headers_specific_album_temp['accept']
headers_specific_album_temp['accept'] = 'text/html, */*; q=0.01'
headers_specific_album_temp['content-type'] =\
							'application/x-www-form-urlencoded; charset=UTF-8'
headers_specific_album_temp['x-pjax'] = 'true'
headers_specific_album_temp['x-pjax-container'] = '#wrapper'
headers_specific_album = headers_specific_album_temp

params_specific_album_temp = copy.deepcopy(params_search)
params_specific_album_temp['_pjax'] = '#wrapper'
params_specific_album = params_specific_album_temp