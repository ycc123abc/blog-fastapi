import requests

url = "http://127.0.0.1:8000/articles/upload-markdown"

payload = {'title': '标题',
'tag_ids': '1eabf918-1899-4def-a0b5-e90b1022572d',
'category_id': '005ca2e8-5e8d-44a3-8395-e80294bd6cf7'}
files=[
  ('markdown_file',('单表格.md',open('D:/工作/2025/广西2025高考指南/提示词/单表格.md','rb'),'application/octet-stream'))
]
headers = {}

response = requests.request("POST", url, headers=headers, data=payload, files=files)

print(response.text)