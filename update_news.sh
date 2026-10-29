#!/usr/bin/env bash

set -Eeuo pipefail
umask 077

export HOME="/home/k-numano"
export PATH="/home/k-numano/.nvm/versions/node/v24.15.0/bin:/usr/local/bin:/usr/bin:/bin"
export LANG="C.UTF-8"
export LC_ALL="C.UTF-8"

readonly WORK_DIR="/home/k-numano/workspace/switchbot"
readonly CODEX="/home/k-numano/.nvm/versions/node/v24.15.0/bin/codex"
readonly JQ="/usr/bin/jq"
readonly SCHEMA="${WORK_DIR}/news-output.schema.json"

tmp_json="$(mktemp "${WORK_DIR}/.news-output.XXXXXX.json")"
tmp_error="$(mktemp "${WORK_DIR}/.news-error.XXXXXX.log")"
tmp_japan="$(mktemp "${WORK_DIR}/.japan-news.XXXXXX.txt")"
tmp_world="$(mktemp "${WORK_DIR}/.world-news.XXXXXX.txt")"
tmp_ai="$(mktemp "${WORK_DIR}/.ai-news.XXXXXX.txt")"

cleanup() {
  rm -f "$tmp_json" "$tmp_error" "$tmp_japan" "$tmp_world" "$tmp_ai"
}
trap cleanup EXIT HUP INT TERM

readonly PROMPT='ライブWeb検索を使い、実行時点の最新ニュースを調査してください。直近24時間の重要な動きを優先し、十分なニュースがなければ直近数日まで広げてください。信頼できる複数の報道・一次情報で事実を確認し、未確認情報は除外してください。

次の3分野について、それぞれ全体の重要な動きが分かる自然な日本語に要約してください。
- japan_news: 国内ニュース全般
- world_news: 海外ニュース全般
- ai_news: 生成AIニュース全般

各要約は必ず日本語45文字以上55字以内にしてください。見出し、項目名、箇条書き、Markdown、URL、出典表記、改行は要約本文に含めないでください。指定されたJSONスキーマに一致するデータだけを返してください。'

if ! "$CODEX" --search exec \
  --ephemeral \
  --ignore-user-config \
  --ignore-rules \
  --sandbox read-only \
  --skip-git-repo-check \
  --cd "$WORK_DIR" \
  --color never \
  --output-schema "$SCHEMA" \
  --output-last-message "$tmp_json" \
  "$PROMPT" >/dev/null 2>"$tmp_error"; then
  printf '%s Codexによるニュース取得に失敗しました。\n' "$(date --iso-8601=seconds)" >&2
  /bin/cat "$tmp_error" >&2
  exit 1
fi

if ! "$JQ" -e '
  type == "object" and
  (.japan_news | type == "string" and length > 0 and length <= 80 and (contains("\n") | not)) and
  (.world_news | type == "string" and length > 0 and length <= 80 and (contains("\n") | not)) and
  (.ai_news | type == "string" and length > 0 and length <= 80 and (contains("\n") | not))
' "$tmp_json" >/dev/null; then
  printf '%s Codexの出力が要件（各1～80文字）を満たしませんでした。\n' "$(date --iso-8601=seconds)" >&2
  exit 1
fi

"$JQ" -r '.japan_news' "$tmp_json" >"$tmp_japan"
"$JQ" -r '.world_news' "$tmp_json" >"$tmp_world"
"$JQ" -r '.ai_news' "$tmp_json" >"$tmp_ai"

mv "$tmp_japan" "${WORK_DIR}/japan_news.txt"
mv "$tmp_world" "${WORK_DIR}/world_news.txt"
mv "$tmp_ai" "${WORK_DIR}/ai_news.txt"

printf '%s ニュース要約3件を更新しました。\n' "$(date --iso-8601=seconds)"
