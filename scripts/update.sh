#!/usr/bin/env bash
# self-expression-audit 自更新脚本
# 用法: bash scripts/update.sh
#
# 功能：
# 1. 检查远程仓库是否有新提交
# 2. 如果有更新，备份本地状态文件
# 3. 拉取远程更新
# 4. 恢复状态文件
# 5. 报告更新内容

set -e

# 定位 skill 根目录（脚本所在目录的上一级）
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
STATE_DIR="$SKILL_DIR/state"
REMOTE_URL="https://github.com/guihuai0552/self-expression-audit.git"

echo "🔍 检查 self-expression-audit 更新..."
echo ""

# 进入 skill 目录
cd "$SKILL_DIR"

# 检查是否有 git 仓库
if [ ! -d ".git" ]; then
    echo "⚠️  未检测到 git 仓库。此脚本需要 skill 通过 git 克隆安装。"
    echo "   如果你是通过手动方式安装的，请手动同步：git pull origin main"
    exit 1
fi

# 确保远程仓库配置正确
CURRENT_REMOTE=$(git remote get-url origin 2>/dev/null || echo "")
if [ "$CURRENT_REMOTE" != "$REMOTE_URL" ]; then
    echo "📡 配置远程仓库地址..."
    git remote set-url origin "$REMOTE_URL"
fi

# 获取远程信息
git fetch origin main 2>/dev/null || {
    echo "❌ 无法连接到远程仓库。请检查网络连接。"
    exit 1
}

LOCAL_COMMIT=$(git rev-parse HEAD)
REMOTE_COMMIT=$(git rev-parse origin/main)

if [ "$LOCAL_COMMIT" = "$REMOTE_COMMIT" ]; then
    echo "✅ 已是最新版本。"
    echo "   本地提交: ${LOCAL_COMMIT:0:8}"
    exit 0
fi

echo "🆕 发现新版本！"
echo "   本地: ${LOCAL_COMMIT:0:8}"
echo "   远程: ${REMOTE_COMMIT:0:8}"
echo ""

# 查看更新内容
echo "📋 更新内容："
echo ""
git log --oneline "${LOCAL_COMMIT}..origin/main" | sed 's/^/   /'
echo ""

# 检查是否有未完成的访谈（状态文件）
HAS_STATE=false
if [ -d "$STATE_DIR" ] && ls "$STATE_DIR"/*-state.json >/dev/null 2>&1; then
    HAS_STATE=true
fi

if [ "$HAS_STATE" = true ]; then
    echo "⚠️  检测到未完成的访谈状态文件："
    ls "$STATE_DIR"/*-state.json | while read f; do
        echo "   - $(basename "$f")"
    done
    echo ""
    echo "   更新前会自动备份这些状态文件到: $STATE_DIR/.backup/"
    echo ""
fi

# 确认更新
echo "是否继续更新？(y/N)"
read -r CONFIRM
if [ "$CONFIRM" != "y" ] && [ "$CONFIRM" != "Y" ]; then
    echo "已取消更新。"
    exit 0
fi

echo ""
echo "🔄 正在更新..."

# 备份状态文件
if [ "$HAS_STATE" = true ]; then
    BACKUP_DIR="$STATE_DIR/.backup/$(date +%Y%m%d-%H%M%S)"
    mkdir -p "$BACKUP_DIR"
    cp "$STATE_DIR"/*-state.json "$BACKUP_DIR/" 2>/dev/null || true
    echo "   ✓ 状态文件已备份到: $BACKUP_DIR"
fi

# 暂存本地修改（如果有）
git stash push -m "auto-stash before update $(date +%Y-%m-%d)" 2>/dev/null || true

# 拉取更新
git pull --rebase origin main 2>/dev/null || {
    # 如果 rebase 失败，尝试普通 merge
    echo "   ⚠️  rebase 失败，尝试普通合并..."
    git merge origin/main --no-edit 2>/dev/null || {
        echo "❌ 更新失败。请手动解决冲突后运行 git merge --continue"
        exit 1
    }
}

# 恢复状态文件（备份已在，无需额外操作）
# 但清理可能由 git 产生的冲突标记
if [ "$HAS_STATE" = true ]; then
    # 确保状态目录存在
    mkdir -p "$STATE_DIR"
    # 备份文件保留在原位，不删除
    echo "   ✓ 状态文件已保留"
fi

echo ""
echo "✅ 更新完成！"
echo ""
echo "📊 更新摘要："
echo ""
git log --oneline -5 2>/dev/null | sed 's/^/   /' || echo "   (无法获取提交历史)"
echo ""

# 清理备份（保留最近 3 次）
if [ -d "$STATE_DIR/.backup" ]; then
    BACKUP_COUNT=$(ls -d "$STATE_DIR/.backup"/*/ 2>/dev/null | wc -l)
    if [ "$BACKUP_COUNT" -gt 3 ]; then
        echo "🧹 清理旧备份（保留最近 3 次）..."
        ls -dt "$STATE_DIR/.backup"/*/ 2>/dev/null | tail -n +4 | while read d; do
            rm -rf "$d"
        done
    fi
fi

echo ""
echo "提示：如果在更新后遇到问题，可以从备份恢复状态文件。"
