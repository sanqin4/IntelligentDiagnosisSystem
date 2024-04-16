# 智能问诊系统使用说明
## 项目概述
智能问诊系统是一个集成了知识库管理与在线问诊功能的系统。它通过使用讯飞API实现智能问诊功能，用户可以通过上传知识库文本，并通过Streamlit web应用与系统交互。
## 项目结构
系统的文件结构如下：
- `data`文件夹：
  - `knowledge`子文件夹：用于存放知识库文本文件。
  - `knowledgeUpload.py`脚本：用于上传知识库到系统中。
- `param`文件夹：包含了API的ID等参数配置文件。API可以从[讯飞API申请地址](https://xinghuo.xfyun.cn/sparkapi)获取。
- `app.py`：Streamlit的主要应用程序文件。
## 如何使用
1. **安装Streamlit**：
   - 打开命令行工具（如：Terminal, Command Prompt等）。
   - 输入以下命令安装Streamlit库：
     ```bash
     pip install streamlit
     ```
2. **运行应用程序**：
   - 在命令行中导航到包含`app.py`的文件夹。
   - 输入以下命令启动Streamlit应用：
     ```bash
     streamlit run app.py
     ```
3. **上传知识库**：
   - 将你的知识库文本文件放置在`data/knowledge`文件夹中。
   - 运行`knowledgeUpload.py`脚本，将知识库上传到系统中。
4. **交互问诊**：
   - 打开Streamlit web应用提供的本地URL（通常为`http://localhost:8501`）。
   - 在web界面上，你可以与智能问诊系统进行交互，提出你的健康问题，系统将基于知识库提供回答。
## 注意事项
- 确保你的环境满足Streamlit的安装要求。
- 讯飞API的ID和密钥需在`param`文件夹中配置正确，否则系统无法正常工作。
- 知识库的更新需要通过`knowledgeUpload.py`脚本进行，上传后系统才能使用最新的知识库信息。
- 语音输入功能效果不佳，不建议使用
## 结语
智能问诊系统旨在提供便捷、快速的医疗咨询服务。通过简单的安装与配置，即可在本地搭建一个智能问诊环境，帮助用户获得即时的医疗建议。
