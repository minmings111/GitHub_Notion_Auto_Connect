# 📒 학습 요약
## 1. 오늘 배운 주제
- LangGraph를 활용한 LLM 기반의 에이전트 및 챗봇 구축 방법

## 2. 핵심 코드
```python
# 1. 상태 정의
class State(TypedDict):
    messages: Annotated[list, add_messages]

# 2. 웹 검색도구 정의
from langchain_teddynote.tools.tavily import TavilySearch
tool_tavily = TavilySearch(max_results=2)

# 3. 챗봇 노드 정의
def chatbot(state: State):
    return {"messages": [llm_with_tools.invoke(state["messages"])]}

# 4. 그래프 생성 및 노드 추가
graph_builder = StateGraph(State)
graph_builder.add_node('chatbot', chatbot)

# 5. 엣지 추가
graph_builder.add_edge(START, 'chatbot')
```

## 3. 코드 해설
- **상태 정의**: `State` 클래스를 정의하여 메시지 리스트를 포함하는 타입을 설정한다.
- **웹 검색 도구 정의**: `TavilySearch`를 사용하여 웹 검색 기능을 추가한다.
- **챗봇 노드 정의**: 사용자의 메시지를 받아 LLM을 호출하여 응답을 생성하는 함수를 정의한다.
- **그래프 생성 및 노드 추가**: `StateGraph` 객체를 생성하고 챗봇 노드를 추가한다.
- **엣지 추가**: 그래프의 시작점과 챗봇 노드를 연결하는 엣지를 추가한다.

## 4. 언제 & 왜
- 언제? LLM 기반의 챗봇이나 에이전트를 구축할 때.
- 왜? 사용자의 요청에 따라 동적으로 도구를 호출하고, 상태를 관리하여 보다 유연한 응답을 제공하기 위해.

## 5. 실무 적용 아이디어
- 고객 지원 챗봇에 LangGraph를 적용하여 사용자의 질문에 따라 웹 검색을 통해 실시간으로 정보를 제공하고, 이전 대화 내용을 기억하여 보다 개인화된 응답을 생성할 수 있다.

## 6. 확장 질문
- LangGraph를 사용하여 다른 유형의 도구(예: 계산기, 데이터베이스 쿼리 등)를 추가할 수 있는 방법은 무엇인가?