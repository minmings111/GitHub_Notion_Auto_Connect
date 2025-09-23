# 파일명: notion_handler.py

import time
from notion_client import Client
import httpx

# --- Markdown을 Notion 블록으로 변환하는 함수 (원본 유지) ---
def md_to_notion_blocks(md: str):
    # (이전 답변의 md_to_notion_blocks 함수 내용 전체를 여기에 붙여넣으세요.)
    # ... (생략) ...
    blocks, lines = [], md.splitlines()
    code_mode, code_buf, code_lang = False, [], "plain text"

    def flush_code():
        nonlocal code_buf, code_lang
        if not code_buf: return
        code_text = "\n".join(code_buf)[:2000]
        blocks.append({"object":"block","type":"code",
                       "code":{"language":code_lang,
                               "rich_text":[{"type":"text","text":{"content":code_text}}]}})
        code_buf.clear(); code_lang = "plain text"

    for raw in lines:
        line = raw.rstrip("\n")
        if line.strip().startswith("```"):
            fence = line.strip()[3:].strip()
            if not code_mode:
                code_mode, code_lang, code_buf = True, (fence or "plain text"), []
            else:
                code_mode = False; flush_code()
            continue
        if code_mode: code_buf.append(line); continue
        if not line.strip(): continue
        if line.startswith("### "):
            blocks.append({"object":"block","type":"heading_3", "heading_3":{"rich_text":[{"type":"text","text":{"content":line[4:]}}]}})
            continue
        if line.startswith("## "):
            blocks.append({"object":"block","type":"heading_2", "heading_2":{"rich_text":[{"type":"text","text":{"content":line[3:]}}]}})
            continue
        if line.startswith("# "):
            blocks.append({"object":"block","type":"heading_1", "heading_1":{"rich_text":[{"type":"text","text":{"content":line[2:]}}]}})
            continue
        if line.lstrip().startswith(("- ", "* ")):
            content = line.lstrip()[2:]
            blocks.append({"object":"block","type":"bulleted_list_item", "bulleted_list_item":{"rich_text":[{"type":"text","text":{"content":content[:1900]}}]}})
            continue
        blocks.append({"object":"block","type":"paragraph", "paragraph":{"rich_text":[{"type":"text","text":{"content":line[:1900]}}]}})
    if code_mode: flush_code()
    return blocks
# --- Notion API를 안전하게 호출하는 함수 ---
def safe_notion_call(fn, *args, **kwargs):
    max_retries, delay = 5, 0.6
    for attempt in range(max_retries):
        try:
            return fn(*args, **kwargs)
        except httpx.HTTPStatusError as e:
            if e.response.status_code in (409, 429, 503):
                time.sleep(delay); delay *= 1.7; continue
            raise
        except Exception:
            time.sleep(delay); delay *= 1.7
            if attempt == max_retries - 1: raise

# --- 🚀 Streamlit을 위한 메인 함수 ---
def send_to_notion(notion_token, page_id, title, summary_content):
    """
    LLM이 생성한 요약 내용을 Notion 페이지에 추가합니다.
    """
    notion = Client(auth=notion_token)
    
    title_block = {"object": "block", "type": "heading_2", "heading_2": {"rich_text": [{"type": "text", "text": {"content": title}}]}}
    summary_blocks = md_to_notion_blocks(summary_content)
    divider_block = {"object": "block", "type": "divider", "divider": {}}
    
    all_blocks = [divider_block, title_block] + summary_blocks
    
    for i in range(0, len(all_blocks), 100):
        safe_notion_call(
            notion.blocks.children.append,
            block_id=page_id,
            children=all_blocks[i:i+100]
        )
        time.sleep(0.3)