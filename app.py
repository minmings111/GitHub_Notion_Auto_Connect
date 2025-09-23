# %%
# !pip install streamlit
import streamlit as st

# %%
import message
import notion_handler

# %%
# 페이지 제목 
st.title("CODE Diary")

st.write("새로 업로드된 GitHub 내용을 개인 Notion 페이지로 연결합니다.")
st.write("아래에 필요한 정보를 입력해 주세요.")

# --- 입력 필드 ---
st.header("1. GitHub 정보")
github_owner = st.text_input("GitHub ID (Owner)", placeholder="예: 'human1234'")
github_repo = st.text_input("GitHub repository", placeholder="예: 'TensorFlow'")
commit_hash = st.text_input("특정 커밋 해시 (Commit Hash)", placeholder="업데이트를 확인할 commit의 해시를 입력하세요.")
github_token = st.text_input("GitHub 개인 액세스 토큰 (Token)", type="password", help="리포지토리 접근 권한이 있는 토큰을 입력하세요.")

st.header("2. Notion 정보")
notion_page_url = st.text_input("Notion 페이지 URL", placeholder="내용을 추가할 Notion 페이지의 전체 URL을 입력하세요.")
notion_token = st.text_input("Notion 개인 액세스 토큰 (Token)", type="password", help="토큰을 입력하세요.")

# %%
# --- 실행 버튼 ---
st.write("---") 
# %%

# 'summary'라는 기억 공간이 없으면 만들어 둡니다.
if 'summary' not in st.session_state:
    st.session_state.summary = None



# %%

# 1. 미리보기가 생성되지 않은 경우 (초기 화면)
if st.session_state.summary is None:
    if st.button("Notion에 요약본 작성하기", icon="🔎"):
        if github_owner and github_repo and commit_hash and github_token:
            with st.spinner("GitHub에서 커밋 변경 내역을 가져오는 중..."):
                commit_changes = message.get_commit_changes(
                    owner=github_owner, repo=github_repo, commit_hash=commit_hash, github_token=github_token
                )
            
            if commit_changes:
                with st.spinner("LLM이 학습 내용을 요약하는 중..."):
                    changes_text = "\n\n".join(f"📄 파일명: {c['filename']} ({c['status']})\n{c['patch']}" for c in commit_changes)
                    prompt = message.make_prompt(changes_text)
                    response = message.client.chat.completions.create(
                        model="gpt-4o-mini",
                        temperature=0,
                        messages=[
                            {"role": "system", "content": "너는 학습 요약 도우미다."},
                            {"role": "user", "content": prompt}
                        ]
                    )
                    # 💡 LLM 결과를 세션 상태(단기 기억 장치)에 저장!
                    st.session_state.summary = response.choices[0].message.content
                    st.rerun() # 페이지를 새로고침하여 미리보기 화면을 보여줌
            else:
                st.error("❗ 변경 내역을 가져오지 못했습니다. 입력 정보를 확인해 주세요.")
        else:
            st.warning("❗ 입력 정보를 모두 작성해주세요.")

# 2. 미리보기가 생성된 경우 (확인/취소 화면)
else:
    st.caption("Notion에 작성될 내용 미리보기")
    st.markdown(st.session_state.summary)
    st.markdown("---")
    
    # 버튼을 옆으로 나란히 놓기 위해 컬럼 사용
    col1, col2 = st.columns(2)

    with col1:
        if st.button("확정 및 Notion 전송", type="primary"):
            with st.spinner("Notion 페이지에 요약 내용을 작성하는 중..."):
                try:
                    page_id = notion_page_url.split('/')[-1].split('?')[0]
                    notion_handler.send_to_notion(
                        notion_token=notion_token,
                        page_id=page_id,
                        title=f"Commit 요약 ({commit_hash[:7]})",
                        summary_content=st.session_state.summary # 세션 상태에서 요약 내용을 가져옴
                    )
                    st.success("🎉 Notion 페이지 작성이 완료되었습니다!")
                    st.balloons()
                    # 💡 작업 완료 후, 세션 상태를 초기화하여 다시 처음 화면으로 돌아감
                    del st.session_state.summary

                except Exception as e:
                    st.error(f"Notion 작성 중 오류 발생: {e}")

    with col2:
        if st.button("취소"):
            # 💡 취소 버튼을 누르면 세션 상태를 초기화하여 처음 화면으로 돌아감
            del st.session_state.summary
            st.rerun()