# 현재 체크아웃된 브랜치 이름을 가져오기
BRANCH_NAME=$(git rev-parse --abbrev-ref HEAD)

# 원하는 형식으로 커밋 메시지 앞에 브랜치 이름 삽입
PREFIX="$BRANCH_NAME "

# 커밋 메시지 파일 경로를 변수에 저장
COMMIT_MSG_FILE=$1

# 임시 파일 생성
TMP_FILE=$(mktemp)

# 커밋 메시지 앞에 브랜치 이름 삽입
echo "$PREFIX$(cat "$COMMIT_MSG_FILE")" > "$TMP_FILE"
mv "$TMP_FILE" "$COMMIT_MSG_FILE"
