# 빌드 방법

번역 대본·원문은 저장소에 없으므로, 아래는 자신이 가진 원본과 번역 파일로 다시 빌드하는 절차입니다.

## 준비물
- 원본 `Final Fantasy Explorers (Japan).3ds` (MD5 `8635aea2d5034d2975df5bbfc7e3c475`)
- Python 3.12+ : `pip install pillow numpy scipy`
- .NET 6 SDK (`tools/blztool`, `tools/mobi` 빌드)
- 글꼴 `NanumSquareNeo-dEb.ttf`(본문 폰트), `NanumSquareNeo-cBd.ttf`(동영상 자막)

## 폴더 구성
```
<작업 폴더>/
  Final Fantasy Explorers (Japan).3ds
  NanumSquareNeo-dEb.ttf, NanumSquareNeo-cBd.ttf
  tools/            (이 저장소의 tools)
  translation/      all_jp.json, out/*.json, layout_ko.json, movie_subs.json  (번역 — 저장소 미포함)
  work/
```

## 순서
1. 도구 빌드: `dotnet build -c Release -o tools/blztool/bin tools/blztool`, `dotnet build -c Release -o tools/mobi/bin tools/mobi`
2. 추출: `python tools/ctr.py "Final Fantasy Explorers (Japan).3ds" work/ext`, `python tools/codeblz.py work/ext/exefs/.code work/ext/code.bin`, `tools/blztool/bin/blztool dec work/ext/romfs work/dec`
3. 번역 작성: 메시지 고유 문장을 `translation/all_jp.json`(제어 문자는 `{XX}`)으로 뽑고, `translation/out/<청크>.json` = `{번호: 한국어}` 로 번역합니다. 검사: `python tools/check.py chunks/<청크>.json`
4. 동영상:
   - moflex에서 비디오 패킷을 뽑아 `tools/mobi/bin/mobi decode` 로 프레임을 복원합니다.
   - 자막 위치와 페이드를 `caps.json` 에 적고, `python tools/mktargets.py` 로 목표 프레임을 만듭니다.
   - `MOBI_NOBUDGET=1 tools/mobi/bin/mobi transcode <pkts> 400 240 <목표 폴더> <시작> <끝> <출력>` 을 구간마다 실행합니다.
   - `python tools/rebuild_mov.py <원본 moflex> work/op_00_ko.moflex <출력…>` 으로 영상을 다시 조립합니다.
5. 빌드: `python tools/final.py` → `Final Fantasy Explorers (Korean).3ds`
6. 차분: `xdelta3 -e -s 원본.3ds 한글.3ds 패치.xdelta` (압축 옵션 없이)
