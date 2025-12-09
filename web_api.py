# web_api.py
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import tempfile
from paddleocr import PaddleOCR
import webbrowser
import threading
import time
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # 允许所有跨域请求

# 初始化 PaddleOCR 实例，按照demo方式
ocr = PaddleOCR(
    use_doc_orientation_classify=False,
    use_doc_unwarping=False,
    use_textline_orientation=False
)

@app.route('/')
def index():
    return send_file('index.html')

@app.route('/ocr', methods=['POST'])
def ocr_endpoint():
    logger.info(f"API 调用开始: 来自 {request.remote_addr}, 文件: {request.files.get('file').filename if 'file' in request.files else '无'}")
    
    if 'file' not in request.files:
        logger.warning("API 调用失败: 无文件上传")
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if file.filename == '':
        logger.warning("API 调用失败: 未选择文件")
        return jsonify({'error': 'No file selected'}), 400
    
    # 保存上传的文件到临时路径
    with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_file:
        file.save(temp_file.name)
        temp_path = temp_file.name
    
    try:
        # 标准调用方式
        result = ocr.predict(input=temp_path)
        
        # 解析结果，按照demo方式
        parsed_results = []
        for res in result:
            data = res.json['res']
            rec_texts = data.get('rec_texts', [])
            rec_scores = data.get('rec_scores', [])
            for i, text in enumerate(rec_texts):
                score = rec_scores[i] if i < len(rec_scores) else 0.0
                parsed_results.append({
                    'text': text,
                    'score': float(score)
                })
        
        logger.info(f"OCR 识别完成: 识别到 {len(parsed_results)} 条文本")
        
        # 删除临时文件
        os.unlink(temp_path)
        
        return jsonify({'results': parsed_results})
    
    except Exception as e:
        logger.error(f"OCR 识别异常: {str(e)}")
        # 删除临时文件
        if os.path.exists(temp_path):
            os.unlink(temp_path)
        return jsonify({'error': str(e)}), 500

def open_browser():
    time.sleep(1)  # 等待服务器启动
    webbrowser.open('http://127.0.0.1:5000/')

if __name__ == '__main__':
    # 在新线程中打开浏览器
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    app.run(host='0.0.0.0', port=5000, debug=False)