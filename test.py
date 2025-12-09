from paddleocr import PaddleOCR
# 初始化 PaddleOCR 实例
ocr = PaddleOCR(
    use_doc_orientation_classify=False,
    use_doc_unwarping=False,
    use_textline_orientation=False)

result = ocr.predict(input="01.png") # 标准调用方式，而不是使用ocr.ocr

#解析
for res in result:
    # res.print()
    # res.save_to_img("output")
    # res.save_to_json("output")
    data = res.json['res']
    rec_texts = data.get('rec_texts', [])
    rec_scores = data.get('rec_scores', [])
    for i, text in enumerate(rec_texts):
        score = rec_scores[i] if i < len(rec_scores) else "N/A"
        print(f"{text} (置信度: {score:.4f})") # text=识别的文字内容，score=置信度 
