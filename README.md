```markdown
# Gaokao Admissions Data Extractor (2023-2025)

此仓库用于抓取与解析中国各省 2023–2025 年高考投档/录取数据（试点：江苏省），目标输出按 年-省-批次 组织的 CSV 文件，字段包含：

province, year, batch, college_code, college_name, major_group_code, plan_quota, admitted_count, min_score, min_rank, source_url, source_file, notes

重要说明：
- 数据来源：省级招生考试院官网、阳光高考信息平台等公开公告/附件。请在使用时注明原始来源及抓取日期。
- 合规：脚本遵守 robots.txt，不绕过登录或反爬措施；请勿以高频率并发抓取对官方服务器造成压力。
- OCR：对图片/扫描 PDF 使用 OCR（PaddleOCR 推荐），扫描质量差的条目会被标注为“需人工复核”。

快速使用：
1. 克隆仓库到本地：
   git clone https://github.com/<your-username>/gaokao-admissions-2023-2025.git
2. 在项目目录中创建并激活虚拟环境，安装依赖：
   python -m venv venv
   source venv/bin/activate  # Linux / macOS
   venv\Scripts\activate     # Windows
   pip install -r requirements.txt
3. 运行江苏试点（示例）：
   python scraper/jiangsu_scraper.py --output-dir out/ --years 2023 2024 2025
4. 若使用 Docker：
   docker build -t gaokao-extractor .
   docker run --rm -v $(pwd)/out:/app/out gaokao-extractor --output-dir out --years 2023 2024 2025

交付物（江苏试点完成后）：
- 按 年-省-批次 的 CSV 文件（文件命名示例：2024_江苏_本科批.csv）
- 原始下载文件（附件、PDF、Excel）及解析日志
- 需要人工复核的条目清单（Excel）
- 代码仓库（公开），含 Dockerfile 与运行说明

如果你希望我把仓库名换成你指定的其他名字，请告诉我。
```
