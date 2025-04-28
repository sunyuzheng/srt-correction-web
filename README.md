# SRT字幕精校工具

这是一个基于Gemini API的在线SRT字幕精校工具，可以帮助您：
- 自动纠正字幕中的错误
- 处理科技术语和专业词汇
- 为英文添加对应的中文翻译

## 功能特点

- 支持上传SRT格式字幕文件
- 自动分块处理大文件
- 实时显示处理进度
- 支持直接下载处理后的文件
- 优雅的用户界面

## 技术栈

- 后端：Flask + Gemini API
- 前端：HTML + TailwindCSS
- 部署：Vercel

## 本地开发

1. 克隆仓库
```bash
git clone <repository-url>
cd srt-correction-web
```

2. 安装依赖
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. 设置环境变量
```bash
echo "GOOGLE_API_KEY=your-api-key" > .env
```

4. 运行应用
```bash
python app.py
```

## 部署

本项目已配置为可以直接部署到Vercel平台。只需要：

1. Fork 这个仓库
2. 在Vercel中导入项目
3. 设置环境变量 `GOOGLE_API_KEY`
4. 部署

## 许可证

MIT 