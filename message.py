# !pip install openai nbformat astor pyperclip nbconvert markdown requests python-dotenv

import os
import nbformat
from nbconvert import PythonExporter
from openai import OpenAI
import datetime
import pyperclip
import textwrap
import markdown
import requests
from dotenv import load_dotenv

# 🔑 1. API Key 불러오기
load_dotenv()
with open("./key/.openai_api_key") as f:
    api_key = f.read().strip()
client = OpenAI(api_key=api_key)

# 📂 2. 코드 + 마크다운 불러오기 함수
def load_code(file_path):
    if file_path.endswith(".ipynb"):
        with open(file_path, encoding="utf-8") as f:
            nb = nbformat.read(f, as_version=4)
        exporter = PythonExporter()
        source, _ = exporter.from_notebook_node(nb)
        return source
    elif file_path.endswith(".py"):
        return open(file_path, encoding="utf-8").read()
    else:
        raise ValueError("지원하지 않는 파일 형식입니다.")

# 📝 3. 학습 요약 템플릿
def make_prompt(code):
    template = textwrap.dedent(f"""
    아래는 학습 코드와 마크다운 설명입니다.  
    이를 분석해서 반드시 원본 도메인을 반영한 학습 요약을 작성하세요.  

    조건:
    - "핵심 코드"는 반드시 원본 코드에서 중요한 부분만 발췌(최대 10줄).
    - 새로운 예제를 만들지 말고 원본 코드를 기반으로 작성.

    --- 코드 시작 ---
    {code}
    --- 코드 끝 ---

    # 📒 학습 요약
    ## 1. 오늘 배운 주제
    - (한 줄 요약)

    ## 2. 핵심 코드
    ```python
    (중요한 코드 발췌, 최대 10줄)
    ```

    ## 3. 코드 해설
    - (주석을 기반으로 설명)

    ## 4. 언제 & 왜
    - 언제? ...
    - 왜? ...

    ## 5. 실무 적용 아이디어
    - ...

    ## 6. 확장 질문
    - ...
    """)
    return template


# 📂 GitHub 커밋 변경 내역 가져오기
def get_commit_changes(owner, repo, commit_hash, github_token=None):
    """
    특정 커밋에서 변경된 모든 파일의 diff 내용을 가져옵니다.
    """
    api_url = f"https://api.github.com/repos/{owner}/{repo}/commits/{commit_hash}"
    headers = {"Accept": "application/vnd.github.v3+json"}
    if github_token:
        headers["Authorization"] = f"token {github_token}"

    try:
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()
        commit_data = response.json()

        if 'files' not in commit_data:
            return []

        changes = []
        for file_info in commit_data['files']:
            if 'patch' not in file_info:
                continue
            change_detail = {
                'filename': file_info['filename'],
                'status': file_info['status'],
                'patch': file_info['patch']
            }
            changes.append(change_detail)
        return changes

    except requests.exceptions.RequestException as e:
        print(f"❌ GitHub에서 커밋 정보를 가져오는 데 실패했습니다: {e}")
        if 'response' in locals():
            print(f"error contents: {response.text}")
        return None


# 📂 LLM 인포그래픽 생성 함수
def code_to_card_infographic_llm(code_str, output_file, title="학습 인포그래픽"):
    example_card = """
    <div class="card data">
      <div class="icon">📂</div>
      <div class="title">[단계명]</div>
      <div class="desc">[설명]</div>
      <div class="keywords">
        <div class="tag">[키워드]</div>
      </div>
    </div>
    """

    prompt = f"""
    아래는 학습 코드 또는 커밋 변경 내역입니다. 이를 분석해서 학습 과정의 주요 단계를 뽑아 인포그래픽을 만들어주세요.

    조건:
    - 반드시 아래 카드 예시와 동일한 구조/스타일을 사용하세요.
    - 예시 내용은 그대로 쓰지 말고, 코드/변경내역에서 의미를 뽑아 채우세요.
    - 각 카드에는 (아이콘, 단계명, 설명, 키워드 태그)가 있어야 합니다.
    - 키워드 태그는 실제 등장한 함수명/클래스명/메서드명 또는 주요 변경 포인트를 넣으세요.
    - 여러 카드를 grid 레이아웃 안에 넣어주세요.
    - 전체 HTML 문서 형태로 출력하세요 (<html> ~ </html> 포함).
    - 제목은 "{title}" 로 작성하세요.

    --- 카드 예시 ---
    {example_card}
    --- 입력 시작 ---
    {code_str}
    --- 입력 끝 ---
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0,
        messages=[
            {"role": "system", "content": "너는 HTML 인포그래픽 디자이너다."},
            {"role": "user", "content": prompt}
        ]
    )

    html_content = response.choices[0].message.content

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"✅ 카드형 인포그래픽 HTML 생성 완료: {output_file}")
    return html_content


# 🚀 MAIN
if __name__ == "__main__":
    # --- 사용자 입력 ---
    REPO_OWNER = "HoonYou"
    REPO_NAME = "streamlit_testt"
    TARGET_COMMIT_HASH = "25fa85e78123d7b173ee50b69f8b452977100c75"
    GITHUB_API_TOKEN = os.getenv("GITHUB_TOKEN")

    # 커밋 diff 가져오기
    commit_changes = get_commit_changes(
        owner=REPO_OWNER,
        repo=REPO_NAME,
        commit_hash=TARGET_COMMIT_HASH,
        github_token=GITHUB_API_TOKEN
    )

    if commit_changes:
        print(f"\n✅ 총 {len(commit_changes)}개의 파일에서 변경 내역 발견!\n")
        changes_text = "\n\n".join(
            f"📄 파일명: {c['filename']} ({c['status']})\n{c['patch']}"
            for c in commit_changes
        )

        # 📒 학습 요약 생성
        prompt = make_prompt(changes_text)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0,
            messages=[
                {"role": "system", "content": "너는 학습 요약 도우미다. 변경된 코드만 분석해라."},
                {"role": "user", "content": prompt}
            ]
        )
        summary = response.choices[0].message.content

        today = datetime.date.today().strftime("%Y-%m-%d")
        summary_file = f"commit_summary_{today}.md"
        with open(summary_file, "w", encoding="utf-8") as f:
            f.write(summary)
        pyperclip.copy(summary)
        print(f"✅ 학습 요약 저장 완료: {summary_file}")
        print("📋 클립보드에도 복사됨")

        # 📊 인포그래픽 HTML 생성
        html_file = f"commit_infographic_{today}.html"
        code_to_card_infographic_llm(changes_text, html_file, title="GitHub Commit 변경 인포그래픽")

    else:
        print("❌ 변경 내역을 가져오지 못했습니다.")
