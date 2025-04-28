import os
import time
from flask import Flask, request, render_template, send_file, jsonify
import google.generativeai as genai
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

app = Flask(__name__)

# 在Vercel环境中使用/tmp目录
UPLOAD_FOLDER = '/tmp/uploads' if os.environ.get('VERCEL') else 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 限制上传文件大小为16MB

# 确保上传目录存在
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# 配置Gemini API
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY', 'AIzaSyAVjKu9nuVHn6kqEW68ubXpm1EEulxTbyg')
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-1.5-pro')

def process_srt_chunk(content):
    """处理单个SRT文件块"""
    prompt = f"""我给你我的访谈字幕，你来帮我精校一下，纠正其中的错误。注意几点：
1. 我会直接使用你精校好的字幕，所以你在原文里直接修改好
2. 一些科技术语字幕里可能出错，你应该根据对话内容和嘉宾身份进行猜测和修改
3. 为了避免中英夹杂的现象，你帮我所有的英文都加入对应中文

以下是字幕内容：
{content}"""
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            if attempt == max_retries - 1:
                raise e
            time.sleep(5)

def split_srt_content(content, chunk_size=500):
    """将SRT内容分割成较小的块"""
    lines = content.split('\n')
    chunks = []
    current_chunk = []
    line_count = 0
    
    for line in lines:
        current_chunk.append(line)
        if line.strip() == '':
            line_count += 1
            if line_count >= chunk_size:
                chunks.append('\n'.join(current_chunk))
                current_chunk = []
                line_count = 0
    
    if current_chunk:
        chunks.append('\n'.join(current_chunk))
    
    return chunks

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': '没有上传文件'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': '没有选择文件'}), 400
    
    if not file.filename.endswith('.srt'):
        return jsonify({'error': '请上传.srt格式的文件'}), 400
    
    try:
        # 保存上传的文件
        filename = secure_filename(file.filename)
        upload_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(upload_path)
        
        # 读取文件内容
        with open(upload_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 分割内容
        chunks = split_srt_content(content)
        
        # 处理每个块
        corrected_chunks = []
        for i, chunk in enumerate(chunks):
            try:
                corrected_chunk = process_srt_chunk(chunk)
                corrected_chunks.append(corrected_chunk)
            except Exception as e:
                # 清理临时文件
                if os.path.exists(upload_path):
                    os.remove(upload_path)
                return jsonify({'error': f'处理第{i+1}块时出错: {str(e)}'}), 500
        
        # 合并处理后的内容
        corrected_content = '\n'.join(corrected_chunks)
        
        # 保存处理后的文件
        output_filename = f'corrected_{filename}'
        output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(corrected_content)
        
        # 读取处理后的文件内容
        with open(output_path, 'r', encoding='utf-8') as f:
            file_content = f.read()
        
        # 清理临时文件
        if os.path.exists(upload_path):
            os.remove(upload_path)
        if os.path.exists(output_path):
            os.remove(output_path)
        
        # 直接返回处理后的内容
        return jsonify({
            'message': '处理完成',
            'content': file_content
        })
        
    except Exception as e:
        # 清理临时文件
        if os.path.exists(upload_path):
            os.remove(upload_path)
        return jsonify({'error': f'处理文件时出错: {str(e)}'}), 500

# Vercel需要的wsgi应用
app.wsgi_app = app.wsgi_app

if __name__ == '__main__':
    app.run(debug=True) 