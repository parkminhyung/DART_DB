# DART_DB
- 공시시스템 DART에서 재무제표를 SQL의 db파일로 저장하는 코드입니다.

1. DART에서 API KEY를 발급받아주세요 <br>
   1.1 사이트 접속 : https://opendart.fss.or.kr/mng/userApiKeyListView.do <br>
   1.2 인증키 신청 -> 약관에 동의 및 이메일과 비밀번호 등록 후 하단에 등록 버튼 클릭 <br>
   1.3 왼쪽 "인증키 관리" 항목에 발급받은 API KEY 확인 <br>
   1.4 DART의 API KEY의 일일 제한량은 20000건, 사용에 유의
 <br>
  
2. FIN_DB.py 파일 수정 <br>
   2.1 9번째 줄 "your directory" 에 DB파일이 저장 될 디렉토리 지정 <br>
   2.2 18번째 줄 1.3번에 발급받은 API KEY 입력 후 구동 <br>
 <br>
 
3. DB파일 내 구성 <br>
   3.1 리스트는 상장회사 이름으로 되어 있음 <br>
   3.2 테이블은 "항목","타입","분기날짜" 의 열로 구성되어 있음 <br>
   3.2 항목은 매출액, 영업이익, 투자활동으로 인한 현금흐름 등의 여러 항목으로 구성되어 있음 <br>
   3.3 타입은 "연결재무제표", "손익계산서" 등으로 구성되어 있음 <br>
   3.4 분기날짜 아래 행들은 해당 항목의 데이터로 구성되어 있음. <br>
   3.5 SQL기능을 이용하여 csv로 export 가능, 전처리 가능, 및 재무표를 클릭 후 ctrl+a (window) cmd+a(mac) 전체선택 후 복사 붙여넣기를 통해 프롬프트 입력 후 GPT 혹은 Glok 등 LLM모델을 이용하여 분석 가능 <br>
 <br>
 DB 예시 (삼성전자)<br>
 
<img width="1408" alt="image" src="https://github.com/user-attachments/assets/4fa62f61-f344-4b74-8c4a-fbc7c937a395" />

<img width="1402" alt="image" src="https://github.com/user-attachments/assets/97d5b3d4-74d9-4472-bb09-bb906c5ef29a" />



Further Update <br>
1. Steamlit 을 이용하여 어플 형태로 제작할 예정 <br>
2. 모든 종목이 아닌, 개별 종목 재무표도 다운받을 수 있도록 할 것. 다만 개별종목의 경우, db형태가 아닌 csv형태로 제공되게 할 것  <br>
3. 영문 버전 제작 

