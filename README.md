# CODE Diary - GitHub to Notion Auto Connector

> GitHub 커밋 변경 내역을 AI로 분석하여 Notion에 자동으로 학습 일지를 작성해주는 도구

## 프로젝트 소개

개발자가 학습한 코드를 GitHub에 커밋하면, 그 변경사항을 자동으로 분석하여 **"무엇을 배웠는지, 왜 중요한지, 어떻게 활용하는지"**를 정리해 Notion 학습 일지에 자동으로 기록해주는 자동화 도구입니다.

### 주요 기능

- GitHub 특정 커밋의 변경 내역 자동 추출
- OpenAI GPT를 활용한 학습 요약 자동 생성
- Markdown을 Notion 블록으로 변환하여 자동 작성
- Notion 전송 전 미리보기 기능
- Streamlit 기반의 직관적인 웹 UI

---

## 프로젝트 구조

```
GitHub_Notion_Auto_Connect/
├── app.py                # Streamlit 웹 UI (메인 애플리케이션)
├── message.py            # GitHub API 연동 및 OpenAI 학습 요약 생성
├── notion_handler.py     # Notion API 연동 및 블록 변환
├── requirements.txt      # Python 패키지 의존성
└── README.md            # 프로젝트 문서
```

### 각 파일 설명

#### **`app.py`** - 웹 인터페이스
- Streamlit 기반의 사용자 인터페이스 제공
- GitHub/Notion 정보 입력 폼
- 요약 미리보기 및 확정/취소 기능
- 세션 상태 관리

#### **`message.py`** - 핵심 로직
- GitHub API를 통한 커밋 diff 가져오기
- OpenAI GPT-4o-mini로 학습 요약 생성
- 프롬프트 템플릿 관리
- CLI 모드 지원 (독립 실행 가능)

#### **`notion_handler.py`** - Notion 연동
- Markdown → Notion 블록 변환
- Notion API 안전 호출 (재시도 로직 포함)
- Rate Limit 대응

---

## 설치 및 실행 방법

### 1. 리포지토리 클론

```bash
git clone https://github.com/YOUR_USERNAME/GitHub_Notion_Auto_Connect.git
cd GitHub_Notion_Auto_Connect
```

### 2. 가상환경 생성

```bash
python -m venv venv
venv\Scripts\activate
```
### 3. 패키지 설치

```bash
pip install -r requirements.txt
```

### 4. API 키 설정

#### **로컬 실행 시**

프로젝트 루트에 `.env` 파일 생성:

```env
OPENAI_API_KEY=your_openai_api_key_here
GITHUB_TOKEN=your_github_personal_access_token_here
```

#### **Streamlit Cloud 배포 시**

Streamlit Cloud 앱 설정에서 **Secrets** 추가:

```toml
OPENAI_API_KEY = "your_openai_api_key_here"
```

### 5. 실행

```bash
streamlit run app.py
```

브라우저에서 `http://localhost:8501` 자동 실행됩니다.

---

## API 키 발급 방법

### GitHub Personal Access Token

1. GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. **Generate new token** 클릭
3. 권한 선택: `repo` (Full control of private repositories)
4. 토큰 생성 후 복사 (한 번만 표시됨!)

### Notion Integration Token

1. [Notion Integrations](https://www.notion.so/my-integrations) 페이지 접속
2. **New integration** 클릭
3. Integration 이름 입력 및 생성
4. **Internal Integration Token** 복사
5. Notion 페이지에서:
   - 우측 상단 `···` → `Add connections` → 생성한 Integration 연결

### OpenAI API Key

1. [OpenAI Platform](https://platform.openai.com/api-keys) 접속
2. **Create new secret key** 클릭
3. API 키 복사 (한 번만 표시됨!)

---

## 사용 방법

### 1. GitHub 정보 입력

- **GitHub ID (Owner)**: 리포지토리 소유자 이름
- **GitHub repository**: 리포지토리 이름
- **Commit Hash**: 분석할 커밋의 해시 값 (예: `abc123def456...`)
- **GitHub Token**: Personal Access Token

### 2. Notion 정보 입력

- **Notion 페이지 URL**: 내용을 추가할 Notion 페이지의 전체 URL
  - 예: `https://www.notion.so/My-Learning-Page-abc123...`
- **Notion Token**: Integration Token

### 3. 요약 생성

1. **"Notion에 요약본 작성하기"** 버튼 클릭
2. GitHub에서 커밋 변경 내역 가져오기 (자동)
3. AI가 학습 요약 생성 (자동)
4. 미리보기 화면에서 내용 확인

### 4. Notion에 전송

- **확정 및 Notion 전송**: Notion 페이지에 자동 작성
- **취소**: 요약 내용 삭제 및 처음 화면으로 돌아가기

---

## 생성되는 학습 요약 형식

AI가 다음 7가지 항목으로 구조화된 학습 일지를 자동 생성합니다:
1. **무엇을 했나요? (What)** - 주제와 변경사항 요약
2. **핵심 코드 (Key Code)** - 중요한 코드 발췌 (10-15줄)
3. **어떻게 작동하나요? (How)** - 단계별 동작 설명
4. **왜 이렇게 했나요? (Why)** - 문제 상황, 선택 이유, 핵심 개념
5. **실무에서는? (Real-world Application)** - 실제 프로젝트 적용 시나리오
6. **더 알아보기 (Further Learning)** - 관련 개념 및 심화 질문
7. **체크리스트 (Self-check)** - 학습 완성도 자가 점검
모든 설명은 **초보자도 이해할 수 있도록** 쉽게 작성되며, 기술 용어는 한글과 영문을 병기합니다.

---

## CLI 모드 사용

`message.py`를 직접 실행하여 CLI 모드로 사용할 수 있습니다:

```bash
python message.py
```

코드 내 설정 수정:
```python
REPO_OWNER = "YOUR_GITHUB_ID"
REPO_NAME = "YOUR_REPO_NAME"
TARGET_COMMIT_HASH = "YOUR_COMMIT_HASH"
```

결과:
- `commit_summary_YYYY-MM-DD.md` - 학습 요약 마크다운
- `commit_infographic_YYYY-MM-DD.html` - 인포그래픽 HTML
- 클립보드에 요약 내용 자동 복사

---

## 주의사항

1. **API 사용량**: OpenAI API는 사용량에 따라 과금됩니다.
2. **Notion Rate Limit**: 대량의 블록 추가 시 속도 제한이 있을 수 있습니다 (자동 재시도 구현됨).
3. **Private Repository**: GitHub Private Repo 접근 시 반드시 Token이 필요합니다.
4. **Notion 페이지 권한**: Integration이 해당 페이지에 접근 권한이 있어야 합니다.

---

## Streamlit Cloud 배포

1. [Streamlit Cloud](https://share.streamlit.io) 접속
2. **New app** 클릭
3. GitHub 리포지토리 연결
4. Main file: `app.py` 선택
5. **Secrets** 설정에서 `OPENAI_API_KEY` 추가
6. **Deploy** 클릭


