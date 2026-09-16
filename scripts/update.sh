#!/usr/bin/env bash
# self-expression-audit 自更新
# 用法:
#   bash scripts/update.sh          # 交互确认
#   bash scripts/update.sh --yes    # 非交互（工作区必须干净）
#
# 安全约束：
# - 不改写 git remote origin（以当前 origin 为准）
# - 工作区有未提交改动则拒绝；不 stash，避免更新后不 pop 导致改动消失
# - 访谈数据在 workspace/expression-audit/，不在本 skill 包内
# - 若设置 EXPRESSION_AUDIT_DIR，更新前备份其中的 *.state.json

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
YES=false
if [ "${1:-}" = "--yes" ] || [ "${1:-}" = "-y" ]; then
    YES=true
fi

echo "检查 self-expression-audit 更新..."
echo ""

cd "$SKILL_DIR"

if [ ! -d ".git" ]; then
    echo "未检测到 git 仓库。此脚本需要 skill 通过 git 克隆安装。"
    echo "手动安装请自行同步上游，不要改 remote。"
    exit 1
fi

CURRENT_REMOTE="$(git remote get-url origin 2>/dev/null || true)"
if [ -z "$CURRENT_REMOTE" ]; then
    echo "没有 origin remote。请先配置后再更新；本脚本不会写入远程地址。"
    exit 1
fi
echo "远程 origin: $CURRENT_REMOTE"
echo "（本脚本不会 set-url。若地址不对，请人工修改。）"
echo ""

if [ -n "$(git status --porcelain)" ]; then
    echo "工作区有未提交改动，拒绝自动更新。"
    echo "请先提交或自行 stash，再重跑本脚本。"
    git status -sb
    exit 2
fi

git fetch origin

DEFAULT_BRANCH=""
if git rev-parse --abbrev-ref origin/HEAD >/dev/null 2>&1; then
    DEFAULT_BRANCH="$(git rev-parse --abbrev-ref origin/HEAD | sed 's#^origin/##')"
fi
if [ -z "$DEFAULT_BRANCH" ] || ! git rev-parse --verify "origin/${DEFAULT_BRANCH}" >/dev/null 2>&1; then
    if git rev-parse --verify origin/main >/dev/null 2>&1; then
        DEFAULT_BRANCH="main"
    elif git rev-parse --verify origin/master >/dev/null 2>&1; then
        DEFAULT_BRANCH="master"
    else
        echo "无法确定远程默认分支。"
        exit 1
    fi
fi

LOCAL_COMMIT="$(git rev-parse HEAD)"
REMOTE_COMMIT="$(git rev-parse "origin/${DEFAULT_BRANCH}")"

if [ "$LOCAL_COMMIT" = "$REMOTE_COMMIT" ]; then
    echo "已是最新版本。"
    echo "   本地提交: ${LOCAL_COMMIT:0:8}"
    echo "   分支: ${DEFAULT_BRANCH}"
    exit 0
fi

echo "发现新版本："
echo "   本地: ${LOCAL_COMMIT:0:8}"
echo "   远程 origin/${DEFAULT_BRANCH}: ${REMOTE_COMMIT:0:8}"
echo ""
echo "更新内容："
git log --oneline "${LOCAL_COMMIT}..origin/${DEFAULT_BRANCH}" | sed 's/^/   /'
echo ""

backup_states() {
    local src="$1"
    local dest="$2"
    mkdir -p "$dest"
    local copied=0
    shopt -s nullglob
    for f in "$src"/*.state.json "$src"/*-state.json; do
        [ -f "$f" ] || continue
        cp "$f" "$dest/"
        copied=$((copied + 1))
    done
    shopt -u nullglob
    if [ "$copied" -gt 0 ]; then
        echo "   已备份 ${copied} 个 state → $dest"
    fi
}

STAMP="$(date +%Y%m%d-%H%M%S)"
if [ -n "${EXPRESSION_AUDIT_DIR:-}" ] && [ -d "$EXPRESSION_AUDIT_DIR" ]; then
    echo "备份 EXPRESSION_AUDIT_DIR=$EXPRESSION_AUDIT_DIR"
    backup_states "$EXPRESSION_AUDIT_DIR" "$EXPRESSION_AUDIT_DIR/.backup/${STAMP}"
fi
if [ -d "$SKILL_DIR/state" ]; then
    echo "备份遗留 skill/state/"
    backup_states "$SKILL_DIR/state" "$SKILL_DIR/state/.backup/${STAMP}"
fi

if [ "$YES" != true ]; then
    if [ ! -t 0 ]; then
        echo "非交互环境：请附加 --yes 才会 pull。"
        exit 3
    fi
    echo "是否继续更新（fast-forward only）？(y/N)"
    read -r CONFIRM
    if [ "$CONFIRM" != "y" ] && [ "$CONFIRM" != "Y" ]; then
        echo "已取消更新。"
        exit 0
    fi
fi

echo ""
echo "正在 fast-forward 到 origin/${DEFAULT_BRANCH}..."
git pull --ff-only origin "$DEFAULT_BRANCH"

echo ""
echo "更新完成。"
echo "最近提交："
git log --oneline -5 | sed 's/^/   /'
echo ""
echo "访谈数据在 workspace/expression-audit/，不会随 skill 更新被覆盖。"
