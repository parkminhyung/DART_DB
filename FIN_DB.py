import dart_fss as dart
import pandas as pd
import numpy as np
import os
import sqlite3
from datetime import datetime

# 데이터베이스 디렉토리 설정
db_dir = "your directory" #FIN_DB.db 파일이 저장 될 디렉토리 지정
db_path = os.path.join(db_dir, "FIN_DB.db")

# 디렉토리가 없으면 생성
if not os.path.exists(db_dir):
  os.makedirs(db_dir)
print(f"디렉토리 생성: {db_dir}")

# Open DART API KEY 설정
API_KEY = "your api key" # DART API KEY 입력
dart.set_api_key(api_key=API_KEY)

def get_financial_data(corp_name, bgn_de='20220101'):
  """회사의 재무제표 데이터를 가져와서 단일 데이터프레임으로 결합"""
# bgn_de 는 기준일
# DART에 공시된 회사 리스트 불러오기
corp_list = dart.get_corp_list()

# 회사 검색
try:
  ffs = corp_list.find_by_corp_name(corp_name, exactly=True)[0]
print(f"회사명: {ffs.corp_name}, 회사코드: {ffs.stock_code}")
except IndexError:
  print(f"'{corp_name}' 회사를 찾을 수 없습니다.")
return None

# 재무제표 불러오기
fs = ffs.extract_fs(bgn_de=bgn_de)

# 재무상태표, 손익계산서, 현금흐름표, 포괄손익계산서 가져오기
df_bs = pd.DataFrame(fs['bs'])
df_is = pd.DataFrame(fs['is'])
df_cf = pd.DataFrame(fs['cf'])
df_cis = pd.DataFrame(fs['cis'])

# 비어있지 않은 데이터프레임 처리
valid_dfs = []
date_cols = []

# 각 데이터프레임 확인 및 처리
if not df_bs.empty:
  df_bs = process_dataframe(df_bs, "연결재무제표")
valid_dfs.append(df_bs)
if len(date_cols) == 0 and df_bs.shape[1] > 2:
  # 타입 열을 제외한 항목과 날짜 열 가져오기
  date_cols = df_bs.columns[1:-1].tolist()

if not df_is.empty:
  df_is = process_dataframe(df_is, "연결손익계산서")
valid_dfs.append(df_is)
if len(date_cols) == 0 and df_is.shape[1] > 2:
  date_cols = df_is.columns[1:-1].tolist()

if not df_cf.empty:
  df_cf = process_dataframe(df_cf, "현금흐름표")
valid_dfs.append(df_cf)
if len(date_cols) == 0 and df_cf.shape[1] > 2:
  date_cols = df_cf.columns[1:-1].tolist()

if not df_cis.empty:
  df_cis = process_dataframe(df_cis, "연결포괄손익계산서")
valid_dfs.append(df_cis)
if len(date_cols) == 0 and df_cis.shape[1] > 2:
  date_cols = df_cis.columns[1:-1].tolist()

# 유효한 데이터프레임이 없는 경우
if not valid_dfs:
  print(f"'{corp_name}'의 유효한 재무제표 데이터가 없습니다.")
return None

# 최대 열 수 계산
max_cols = max(df.shape[1] for df in valid_dfs)

# 각 DataFrame의 배열에 대해 열 수가 부족한 경우 NaN으로 padding 후 배열 추출
padded_arrays = []
for df in valid_dfs:
  arr = df.values
if arr.shape[1] < max_cols:
  pad_width = max_cols - arr.shape[1]
# 오른쪽에만 NaN padding을 추가
arr = np.pad(arr, ((0, 0), (0, pad_width)), mode='constant', constant_values=np.nan)
padded_arrays.append(arr)

# 배열들을 세로로 결합
combined_array = np.vstack(padded_arrays)

# 새로운 열 이름 리스트 생성
cols = ["항목"] + date_cols + ["타입"]

# 결합된 배열을 DataFrame으로 변환
result_df = pd.DataFrame(combined_array, columns=cols)

# 열 순서 재배열 - "항목", "타입", 날짜들 순서로
reordered_cols = ["항목", "타입"] + date_cols
result_df = result_df[reordered_cols]

return result_df

def process_dataframe(df, type_name):
  """데이터프레임 처리 및 타입 추가"""
try:
  processed_df = pd.concat([
    df.loc[:, (slice(None), ('label_ko',))],
    df.loc[:, (slice(None), ('연결재무제표',))]
  ], axis=1)

# 열 이름 처리 (멀티인덱스에서 첫 번째 레벨만 가져오기)
new_cols = ['항목']
for col in processed_df.columns[1:]:
  new_cols.append(col[0])

processed_df.columns = new_cols
processed_df['타입'] = type_name

return processed_df
except KeyError as e:
  # '연결재무제표' 키가 없는 경우 '재무제표'로 시도
  try:
  processed_df = pd.concat([
    df.loc[:, (slice(None), ('label_ko',))],
    df.loc[:, (slice(None), ('재무제표',))]
  ], axis=1)

# 열 이름 처리
new_cols = ['항목']
for col in processed_df.columns[1:]:
  new_cols.append(col[0])

processed_df.columns = new_cols
processed_df['타입'] = type_name

return processed_df
except Exception as inner_e:
  print(f"{type_name} 처리 중 오류 발생: {inner_e}")
# 빈 데이터프레임 반환
return pd.DataFrame(columns=['항목', '타입'])

def save_to_db(df, company_name):
  """데이터프레임을 SQLite 데이터베이스에 저장"""
conn = sqlite3.connect(db_path)

# 테이블 이름 (회사명)
table_name = company_name.replace(' ', '_')

try:
  # 테이블이 이미 존재하는지 확인
  cursor = conn.cursor()
cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
table_exists = cursor.fetchone() is not None

if table_exists:
  # 기존 데이터 삭제
  conn.execute(f"DROP TABLE {table_name}")
print(f"기존 '{table_name}' 테이블 데이터를 업데이트합니다.")

# 새 데이터 저장
df.to_sql(table_name, conn, index=False)

# 저장 시간 기록
timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
cursor.execute("CREATE TABLE IF NOT EXISTS update_log (company TEXT, last_update TEXT)")

# 로그에 회사가 있는지 확인
cursor.execute("SELECT * FROM update_log WHERE company=?", (table_name,))
log_exists = cursor.fetchone() is not None

if log_exists:
  cursor.execute("UPDATE update_log SET last_update=? WHERE company=?", (timestamp, table_name))
else:
  cursor.execute("INSERT INTO update_log VALUES (?, ?)", (table_name, timestamp))

conn.commit()
print(f"'{table_name}' 데이터를 데이터베이스에 저장했습니다. (업데이트: {timestamp})")

except Exception as e:
  print(f"데이터베이스 저장 중 오류 발생: {e}")
finally:
  conn.close()

def update_company_financials(company_name, start_date=None):
  """회사 재무제표 데이터 수집 및 데이터베이스 업데이트"""
if start_date is None:
  # 기본값으로 3년 전 데이터부터 수집
  current_year = datetime.now().year
start_date = f"{current_year-3}0101"

# 재무제표 데이터 수집
financial_data = get_financial_data(company_name, bgn_de=start_date)

if financial_data is not None:
  # 데이터베이스에 저장
  save_to_db(financial_data, company_name)
return True
else:
  print(f"{company_name}의 재무제표 데이터를 가져오는 데 실패했습니다.")
return False

def list_companies_in_db():
  """데이터베이스에 저장된 회사 목록 조회"""
if not os.path.exists(db_path):
  print("데이터베이스 파일이 존재하지 않습니다.")
return []

conn = sqlite3.connect(db_path)
try:
  cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name != 'update_log'")
tables = cursor.fetchall()

if tables:
  companies = [table[0].replace('_', ' ') for table in tables]
print("데이터베이스에 저장된 회사 목록:")
for i, company in enumerate(companies, 1):
  # 업데이트 시간 조회
  cursor.execute("SELECT last_update FROM update_log WHERE company=?", (company.replace(' ', '_'),))
result = cursor.fetchone()
update_time = result[0] if result else "정보 없음"
print(f"{i}. {company} (마지막 업데이트: {update_time})")
return companies
else:
  print("데이터베이스에 저장된 회사가 없습니다.")
return []
finally:
  conn.close()


corp_list = dart.get_corp_list()

valid_corp_list = [corp for corp in corp_list if corp.corp_code is not None and corp.stock_code]


company_names = [corp.corp_name for corp in valid_corp_list]

if __name__ == "__main__":
  # API 키 설정 확인
  if not API_KEY:
  API_KEY = input("DART API 키를 입력해주세요: ")
dart.set_api_key(api_key=API_KEY)

# 각 회사에 대해 재무제표 업데이트 수행 (오류가 발생해도 계속 진행)
for company in company_names:
  print(f"Updating financials for: {company}")
try:
  update_company_financials(company)
except Exception as e:
  print(f"{company} 업데이트 중 오류 발생: {e}")

# 저장된 회사 목록 출력
list_companies_in_db()
