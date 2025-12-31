# 파일명: notion_handler.py

import time
from notion_client import Client
import httpx
import streamlit as st

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
    max_retries, delay = 8, 1.0
    for attempt in range(max_retries):
        try:
            st.write(f"API call attempt {attempt + 1}/{max_retries}")
            result = fn(*args, **kwargs)
            st.write("API call succeeded")
            return result
        except httpx.HTTPStatusError as e:
            st.write(f"HTTP error: {e.response.status_code}")
            if e.response.status_code in (409, 429, 503):
                st.write(f"Retrying in {delay:.1f}s...")
                time.sleep(delay); delay *= 1.7; continue
            st.write("Non-retryable HTTP error")
            raise
        except Exception as ex:
            st.write(f"Exception: {type(ex).__name__}: {str(ex)}")
            time.sleep(delay); delay *= 1.7
            if attempt == max_retries - 1:
                st.write("Max retries exceeded")
                raise

# --- Streamlit function for sending content to Notion ---
def send_to_notion(notion_token, page_id, title, summary_content):
    """
    LLM이 생성한 요약 내용을 Notion 페이지에 추가합니다.
    """
    st.write("Initializing Notion client...")
    try:
        notion = Client(auth=notion_token)
        st.write("Notion client initialized successfully")
    except Exception as e:
        st.error(f"Failed to initialize Notion client: {type(e).__name__}: {str(e)}")
        raise
    
    st.write("Creating title block...")
    title_block = {"object": "block", "type": "heading_2", "heading_2": {"rich_text": [{"type": "text", "text": {"content": title}}]}}
    
    st.write("Converting markdown to Notion blocks...")
    try:
        summary_blocks = md_to_notion_blocks(summary_content)
        st.write(f"Created {len(summary_blocks)} blocks from markdown")
    except Exception as e:
        st.error(f"Failed to convert markdown: {type(e).__name__}: {str(e)}")
        raise
    
    divider_block = {"object": "block", "type": "divider", "divider": {}}
    all_blocks = [divider_block, title_block] + summary_blocks
    st.write(f"Total blocks to send: {len(all_blocks)}")
    
    for i in range(0, len(all_blocks), 100):
        batch_size = min(100, len(all_blocks) - i)
        st.write(f"Sending blocks {i+1} to {i+batch_size} of {len(all_blocks)}...")
        
        try:
            safe_notion_call(
                notion.blocks.children.append,
                block_id=page_id,
                children=all_blocks[i:i+100]
            )
            st.write(f"Successfully sent blocks {i+1} to {i+batch_size}")
        except Exception as e:
            st.error(f"Failed to send blocks: {type(e).__name__}: {str(e)}")
            raise
        
        time.sleep(0.3)
    
    st.write("All blocks sent successfully!")