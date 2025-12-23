#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
江苏省高考投档/录取数据抓取脚手架（试点模板）
- 功能：发现公告、下载附件（xlsx/pdf）、尝试解析（Excel / 文本型 PDF / 图片型 PDF -> OCR）
- 输出：按 year/province/batch 的 CSV（字段见 README）
- 注意：此脚本是可运行的 scaffold，需要根据江苏招生院网站的实际页面结构填入公告列表 URL 与解析规则。
"""

import os
import argparse
import logging
import requests
from pathlib import Path
import pandas as pd

import pdfplumber

# 尝试导入 PaddleOCR（若未安装，脚本仍可处理 Excel 与文本型 PDF）
try:
    from paddleocr import PaddleOCR
    OCR_AVAILABLE = True
except Exception:
    OCR_AVAILABLE = False

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

HEADERS = {
    'User-Agent': 'gaokao-data-extractor/1.0 (for research; respect robots.txt)'
}

def ensure_dir(p):
    Path(p).mkdir(parents=True, exist_ok=True)

def download_file(url, out_dir):
    local_name = os.path.join(out_dir, url.split('/')[-1])
    logging.info(f'Downloading {url} -> {local_name}')
    r = requests.get(url, headers=HEADERS, timeout=60)
    r.raise_for_status()
    with open(local_name, 'wb') as f:
        f.write(r.content)
    return local_name

def parse_excel(path):
    logging.info(f'Parsing Excel {path}')
    try:
        df = pd.read_excel(path, sheet_name=0, dtype=str)
        return df
    except Exception:
        logging.exception('Excel parse failed')
        return None

def parse_pdf_with_pdfplumber(path):
    logging.info(f'Parsing PDF {path} with pdfplumber')
    tables = []
    try:
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                page_tables = page.extract_tables()
                for t in page_tables:
                    if len(t) < 2:
                        continue
                    df = pd.DataFrame(t[1:], columns=t[0])
                    tables.append(df)
        return tables
    except Exception:
        logging.exception('pdfplumber parse failed')
        return []

def ocr_pdf(path):
    logging.info(f'OCR PDF {path}')
    if not OCR_AVAILABLE:
        logging.warning('PaddleOCR not available. Install paddleocr for Chinese OCR.')
        return None
    ocr = PaddleOCR(use_angle_cls=True, lang='ch')
    texts = []
    try:
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                im = page.to_image(resolution=200).original
                res = ocr.ocr(im, cls=True)
                page_text = '\n'.join([''.join([w[1][0] for w in line]) for line in res])
                texts.append(page_text)
        return '\n\n'.join(texts)
    except Exception:
        logging.exception('OCR failed')
        return None

def normalize_and_write(df, meta, out_csv):
    """
    简单映射示例：将省里不同列名映射为统一字段并追加到 CSV。
    meta: {province, year, batch, source_url, source_file}
    """
    columns_map = {
        '院校代码': 'college_code',
        '院校名称': 'college_name',
        '专业组代码': 'major_group_code',
        '计划数': 'plan_quota',
        '投档人数': 'admitted_count',
        '投档最低分': 'min_score',
        '投档最低排位': 'min_rank'
    }
    df_renamed = df.rename(columns={k: v for k,v in columns_map.items() if k in df.columns})
    std_cols = ['college_code','college_name','major_group_code','plan_quota','admitted_count','min_score','min_rank']
    for c in std_cols:
        if c not in df_renamed.columns:
            df_renamed[c] = None
    out_df = df_renamed[std_cols].copy()
    out_df['province'] = meta.get('province')
    out_df['year'] = meta.get('year')
    out_df['batch'] = meta.get('batch')
    out_df['source_url'] = meta.get('source_url')
    out_df['source_file'] = meta.get('source_file')
    out_df['notes'] = ''
    # reorder
    cols = ['province','year','batch'] + std_cols + ['source_url','source_file','notes']
    out_df = out_df[cols]
    # append or write
    if not os.path.exists(out_csv):
        out_df.to_csv(out_csv, index=False)
    else:
        out_df.to_csv(out_csv, index=False, header=False, mode='a')

def main(args):
    output_dir = args.output_dir
    ensure_dir(output_dir)
    downloaded_dir = os.path.join(output_dir, 'downloaded')
    ensure_dir(downloaded_dir)

    # --------- TODO: 把下面的 ANNOUNCE_PAGES 用江苏招生考试院实际公告列表替换 ----------
    ANNOUNCE_PAGES = [
        # 示例： 'https://www.jseea.cn/xxgk/jyxx/2024-xx.html'
    ]
    # -------------------------------------------------------------------------------

    # 示范流程（需要根据真实页面细化解析逻辑）
    for page in ANNOUNCE_PAGES:
        logging.info(f'Listing page: {page}')
        r = requests.get(page, headers=HEADERS, timeout=30)
        r.raise_for_status()
        # TODO: 解析页面，找到每条公告（含年份/批次信息），并获取附件链接

    logging.info('脚手架已准备好。请把 ANNOUNCE_PAGES 与页面解析规则更新为江苏官网的真实 URL。')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output-dir', default='out', help='输出目录')
    parser.add_argument('--years', nargs='+', type=int, default=[2023,2024,2025])
    args = parser.parse_args()
    main(args)
