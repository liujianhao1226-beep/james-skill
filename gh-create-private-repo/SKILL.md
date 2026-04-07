---
name: gh-create-private-repo
description: 使用 GitHub CLI 创建私有仓库并推送本地项目（支持中文项目名自动翻译）
---

## 前置条件
- 已安装 Git 和 GitHub CLI
- 已通过 `gh auth login` 登录 GitHub
- 当前目录已初始化 git 仓库（如未初始化，先执行 `git init`）

## 步骤

1. 检查 git 状态和当前分支：

```powershell
git status -sb
```

2. 验证 GitHub CLI 已登录：

```powershell
gh auth status
```

> 如果 `gh` 不在 PATH 中，使用完整路径：`& "C:\Program Files\GitHub CLI\gh.exe" auth status`

3. 配置 .gitignore 忽略大文件（避免重复添加）：

```powershell
$ignorePatterns = @("*.exe", "*.pkg")
$gitignorePath = ".gitignore"

if (Test-Path $gitignorePath) {
    $existingContent = Get-Content $gitignorePath -Raw
} else {
    $existingContent = ""
}

foreach ($pattern in $ignorePatterns) {
    if ($existingContent -notmatch [regex]::Escape($pattern)) {
        Add-Content $gitignorePath $pattern
    }
}
git add .gitignore
```

4. 提交所有更改（如已有提交则跳过）：

```powershell
git add -A
git commit -m "Initial commit" --allow-empty
```

5. 获取仓库名（将中文项目名翻译为英文）：

> Agent 应读取当前目录名，如果是中文则翻译为合适的英文名称（使用短横线连接，全小写）。
> 例如：`无线性能分析` → `wireless-performance-analysis`

```powershell
$repoName = "<translated-english-repo-name>"  # 由 Agent 根据目录名翻译填入
```

6. 检查远程仓库是否已存在，决定创建或直接推送：

```powershell
# 检查 GitHub 上是否已存在同名仓库
$existingRepo = gh repo view $repoName 2>&1

if ($LASTEXITCODE -eq 0) {
    # 仓库已存在，配置 remote 并推送
    Write-Host "仓库 $repoName 已存在，直接推送代码..."
    
    # 移除旧的 origin（如果存在）
    git remote remove origin 2>$null
    
    # 添加已有仓库的 remote
    git remote add origin "https://github.com/$((gh api user --jq .login))/$repoName.git"
    
    # 推送代码（设置上游分支）
    $currentBranch = git branch --show-current
    git push -u origin $currentBranch --force
} else {
    # 仓库不存在，创建新的私有仓库
    Write-Host "创建新的私有仓库 $repoName..."
    gh repo create $repoName --private --source . --remote origin --push
}
```

7. 确认远程仓库和跟踪分支：

```powershell
git remote -v
git status -sb
```
