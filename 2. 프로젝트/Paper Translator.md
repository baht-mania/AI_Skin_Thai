# 📄 Paper Translator

**분류:** 문서 번역 / 웹 애플리케이션
**상태:** 개발 완료 (v1.0)
**최종 업데이트:** 2026-02-27
**배포 URL:** http://localhost:5001 (로컬 전용)

---

## 개요

학술 논문 PDF, CSV, Excel(XLSX) 파일을 영어에서 한국어로 번역하는 웹 애플리케이션. PDF의 경우 원본 레이아웃(이미지, 표, 벡터 그래픽)을 보존하면서 텍스트만 한국어로 교체하는 Clone-Redact-Rewrite 전략을 사용. Claude API를 통한 고품질 학술 번역과 실시간 진행률 표시(SSE) 기능을 제공.

---

## 기술 스택

| 구분 | 기술 |
|------|------|
| 프레임워크 | Flask 3.1 (Python) |
| PDF 파싱/재구성 | PyMuPDF (fitz) 1.27+ |
| 이미지 처리 | Pillow 12+ |
| 번역 엔진 | Anthropic Claude API (claude-sonnet-4-6) |
| Excel 처리 | openpyxl |
| 실시간 통신 | Server-Sent Events (SSE) |
| 프론트엔드 | HTML/CSS/JS (Jinja2 템플릿) |
| 한국어 폰트 | PyMuPDF 내장 korea / AppleSDGothicNeo / NanumGothic |
| 배포 | 로컬 실행 (Flask 내장 서버) |

---

## 주요 기능

### PDF 번역
- PDF 업로드 및 페이지별 구조화 파싱 (텍스트 블록, 이미지, 표 분리)
- Clone-Redact-Rewrite 전략으로 원본 레이아웃 완벽 보존
- 표(Table) 자동 감지 및 셀 단위 번역
- 이미지/벡터 그래픽 원본 유지
- 폰트 크기 자동 조절 (6단계 스케일링)

### CSV/Excel 번역
- CSV 파일 다중 인코딩 자동 감지 (UTF-8, CP949, Latin-1)
- XLSX 파일 서식/수식/병합셀 보존하며 텍스트만 번역
- 배치 단위 번역 (50셀/배치)

### 번역 품질
- 학술 용어 정확성 유지
- 수식/LaTeX 표현 원본 보존
- 인용 마커 ([1], Author Year 등) 유지
- API 호출 실패 시 자동 재시도 (최대 3회, 지수 백오프)

### 기타
- 실시간 진행률 표시 (SSE 스트리밍)
- 백그라운드 스레드 기반 비동기 처리
- 파일 크기 제한 (최대 50MB)
- 번역 완료 후 파일 다운로드

---

## 인프라 구성

### 로컬 서버
- **호스트:** 0.0.0.0
- **포트:** 5001
- **실행 방법:** `python app.py`

### 디렉토리 구조
- **업로드:** `uploads/`
- **출력:** `outputs/`
- **템플릿:** `templates/index.html`
- **정적 파일:** `static/`

### 환경 변수
- `ANTHROPIC_API_KEY` — Claude API 인증 키

---

## 개발 히스토리

| 날짜 | 작업 내용 |
|------|-----------|
| 2026-02-27 | PDF/CSV/XLSX 번역 기능 전체 구현 완료 |

---

## 관련 파일

- 프로젝트 경로: `/Users/baht/Desktop/5. 넥써쓰_Claude/paper-translator/`
- 메인 서버: `app.py`
- 설정: `config.py`
- PDF 파서: `pdf_parser.py`
- PDF 재구성: `pdf_rebuilder.py`
- 번역 엔진: `translator.py`
- CSV/Excel 번역: `doc_translator.py`
- 폰트 관리: `font_manager.py`
- 의존성: `requirements.txt`

---

## 알려진 이슈

- [ ] Git 저장소 미설정
- [ ] 대용량 PDF (100+ 페이지) 번역 시 메모리 사용량 최적화 필요
- [ ] 번역 완료 파일 자동 정리(cleanup) 미구현
- [ ] openpyxl이 requirements.txt에 미포함 (XLSX 번역 시 필요)

---

## 참고 링크

- 없음
