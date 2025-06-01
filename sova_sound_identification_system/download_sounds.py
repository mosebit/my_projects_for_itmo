import requests

headers = {
    'Authorization': 'Bearer {{aSetf9Iu9pHfgYRaVYZP5BId5Eq3BlJGPlMHfHBK}}',
}

response = requests.get('https://freesound.org/apiv2/sounds/14854/download/', headers=headers)
print(response)
