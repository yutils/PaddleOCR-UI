
# python实现 本地离线 图片文本识别
## 采用PaddleOCR

首先安装
```shell
pip install paddleocr paddlepaddle -i https://pypi.tuna.tsinghua.edu.cn/simple
pip install customtkinter
```
运行，首次运行会自动下模型
```shell
python.exe main.py
```

## 简单实现
```python
from paddleocr import PaddleOCR
ocr = PaddleOCR(
    use_doc_orientation_classify=False,
    use_doc_unwarping=False,
    use_textline_orientation=False)

result = ocr.predict(input="01.png")

for res in result:
    #res.print()
    #res.save_to_img("output")
    #res.save_to_json("output")
    data = res.json['res']
    rec_texts = data.get('rec_texts', [])
    rec_scores = data.get('rec_scores', [])
    for i, text in enumerate(rec_texts):
        score = rec_scores[i] if i < len(rec_scores) else "N/A"
        print(f"{text} (置信度: {score:.4f})")
```