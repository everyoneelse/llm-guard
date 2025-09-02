#!/usr/bin/env python3
"""
最简单的Web界面实现 - 只需要Python标准库
无需安装任何额外依赖！
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import json
import webbrowser
import threading

# HTML模板
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>同义词替换</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        .card { background: white; border-radius: 8px; padding: 20px; margin: 20px 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .title { font-size: 2em; font-weight: bold; text-align: center; color: #333; margin-bottom: 30px; }
        .step-title { font-size: 1.5em; font-weight: bold; color: #444; margin-bottom: 15px; }
        .step-desc { color: #666; margin-bottom: 15px; }
        textarea { width: 100%; padding: 12px; border: 1px solid #ddd; border-radius: 4px; font-size: 14px; }
        button { background: #007bff; color: white; border: none; padding: 12px 24px; border-radius: 4px; cursor: pointer; font-size: 16px; }
        button:hover { background: #0056b3; }
        button.success { background: #28a745; }
        button.success:hover { background: #1e7e34; }
        .table-container { display: flex; gap: 20px; margin: 20px 0; }
        .table-half { flex: 1; }
        table { width: 100%; border-collapse: collapse; margin: 10px 0; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background: #f8f9fa; font-weight: bold; }
        input[type="text"] { width: 100%; padding: 4px; border: none; background: transparent; }
        .result-area { background: #f8f9fa; padding: 15px; border-radius: 4px; margin-top: 15px; }
        .tabs { display: flex; margin-bottom: 20px; border-bottom: 1px solid #ddd; }
        .tab { padding: 12px 24px; cursor: pointer; border-bottom: 2px solid transparent; }
        .tab.active { border-bottom-color: #007bff; color: #007bff; font-weight: bold; }
        .tab-content { display: none; }
        .tab-content.active { display: block; }
    </style>
</head>
<body>
    <div class="container">
        <h1 class="title">同义词替换</h1>
        
        <div class="tabs">
            <div class="tab active" onclick="showTab('tab1')">📝 文本处理</div>
            <div class="tab" onclick="showTab('tab2')">🔧 拒答设定</div>
            <div class="tab" onclick="showTab('tab3')">📚 原文库结论查库</div>
        </div>

        <!-- Tab 1: 文本处理 -->
        <div id="tab1" class="tab-content active">
            <div class="card">
                <h2 class="step-title">Step 1: 输入文本</h2>
                <p class="step-desc">请在下方文本框中输入需要测试的文本内容</p>
                
                <textarea id="inputText" rows="6" placeholder="西门子的DTI怎么样"></textarea>
                
                <button onclick="processStep1()" style="margin-top: 15px;">
                    🚀 开始处理 (Step1获取初步距离答案/友商以及UIH技术名)
                </button>
                
                <div id="step1Result" class="result-area" style="display: none;">
                    <strong>✅ Step 1 处理完成！</strong>
                </div>
            </div>
        </div>

        <!-- Tab 2: 拒答设定 -->
        <div id="tab2" class="tab-content">
            <div class="card">
                <h2 class="step-title">Step 2: 更新待定信息</h2>
                <p class="step-desc">Step2.1 #根据友商技术在定义上的归属</p>
                
                <div class="table-container">
                    <div class="table-half">
                        <h3>👥 友商技术信息表</h3>
                        <table>
                            <thead>
                                <tr>
                                    <th>idx</th>
                                    <th>competitor_name</th>
                                    <th>competitor_product</th>
                                    <th>uih_product</th>
                                    <th>belong_to_uih</th>
                                    <th>candidate_product</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr>
                                    <td><input type="text" value="0"></td>
                                    <td><input type="text" value="西门子"></td>
                                    <td><input type="text" value="DTI"></td>
                                    <td><input type="text" value="DTI"></td>
                                    <td><input type="text" value="false"></td>
                                    <td><input type="text" value="GE, 飞利浦"></td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                    
                    <div class="table-half">
                        <h3>🏢 UIH技术信息表</h3>
                        <table>
                            <thead>
                                <tr>
                                    <th>idx</th>
                                    <th>belong_to_which</th>
                                    <th>corresponding_product</th>
                                    <th>uih_product</th>
                                    <th>candidate_product</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr>
                                    <td><input type="text" value="0"></td>
                                    <td><input type="text" value="DTI"></td>
                                    <td><input type="text" value="DTI"></td>
                                    <td><input type="text" value='["UIH", "DTI"]'></td>
                                    <td><input type="text" value='["GE"]'></td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>

        <!-- Tab 3: 原文库结论查库 -->
        <div id="tab3" class="tab-content">
            <div class="card">
                <h2 class="step-title">Step 3: 获取最终拒答策略</h2>
                <p class="step-desc">基于前两步的选择，生成最终的拒答策略结果</p>
                
                <button class="success" onclick="processStep3()">
                    🎯 开始处理 (Step3获取最终拒答策略)
                </button>
                
                <div id="step3Result" class="result-area" style="display: none;">
                    <h3>📋 拒答结果</h3>
                    <table style="margin-top: 15px;">
                        <thead>
                            <tr>
                                <th>refuse_index</th>
                                <th>candidate_text</th>
                                <th>is_refuse</th>
                                <th>refuse_reason</th>
                                <th>refuse_tech</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td>3</td>
                                <td>西门子的DTI怎么样</td>
                                <td>true</td>
                                <td>false</td>
                                <td>您好，您的提问涉及西门子的DTI技术，很抱歉无法为您提供咨询服务。作为上海联影医疗科技股份有限公司的人工智能助手，我的职责...</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>

    <script>
        function showTab(tabId) {
            // 隐藏所有tab内容
            document.querySelectorAll('.tab-content').forEach(content => {
                content.classList.remove('active');
            });
            document.querySelectorAll('.tab').forEach(tab => {
                tab.classList.remove('active');
            });
            
            // 显示选中的tab
            document.getElementById(tabId).classList.add('active');
            event.target.classList.add('active');
        }
        
        function processStep1() {
            const text = document.getElementById('inputText').value;
            if (text.trim()) {
                document.getElementById('step1Result').style.display = 'block';
                // 这里可以发送到后端处理
                fetch('/process_step1', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({text: text})
                });
            } else {
                alert('请先输入文本内容');
            }
        }
        
        function processStep3() {
            document.getElementById('step3Result').style.display = 'block';
            // 这里可以发送到后端处理
            fetch('/process_step3', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({})
            });
        }
    </script>
</body>
</html>
"""

class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(HTML_TEMPLATE.encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        if self.path == '/process_step1':
            # 处理Step 1逻辑
            result = {"status": "success", "message": "Step 1 处理完成"}
        elif self.path == '/process_step3':
            # 处理Step 3逻辑
            result = {"status": "success", "message": "Step 3 处理完成"}
        else:
            result = {"status": "error", "message": "未知请求"}
        
        self.wfile.write(json.dumps(result).encode('utf-8'))

def start_server():
    server = HTTPServer(('localhost', 8080), RequestHandler)
    print("🚀 服务器启动成功！")
    print("📱 请在浏览器中访问: http://localhost:8080")
    server.serve_forever()

if __name__ == '__main__':
    # 在新线程中启动服务器，这样可以同时打开浏览器
    server_thread = threading.Thread(target=start_server)
    server_thread.daemon = True
    server_thread.start()
    
    # 自动打开浏览器
    try:
        webbrowser.open('http://localhost:8080')
    except:
        pass
    
    # 保持主线程运行
    server_thread.join()