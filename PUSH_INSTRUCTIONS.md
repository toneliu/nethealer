# 推送到 GitHub 远程仓库

## 方法 1: 使用 Personal Access Token

1. 在 GitHub 生成 Personal Access Token:
   - 访问: https://github.com/settings/tokens
   - 生成新 token (Classic)
   - 勾选 `repo` 权限

2. 在终端执行:

```bash
cd /workspace/network-agent

# 添加远程仓库
git remote add origin https://github.com/toneliu/nethealer.git
git branch -M main

# 使用 token 推送 (将 YOUR_TOKEN 替换为你的 token)
git push https://YOUR_TOKEN@github.com/toneliu/nethealer.git main
```

## 方法 2: 使用 SSH

1. 生成 SSH 密钥:
```bash
ssh-keygen -t ed25519 -C "your_email@example.com"
cat ~/.ssh/id_ed25519.pub
```

2. 将公钥添加到 GitHub:
   - 访问: https://github.com/settings/keys
   - 添加新 SSH key

3. 修改远程仓库为 SSH 方式:
```bash
git remote set-url origin git@github.com:toneliu/nethealer.git
git push -u origin main
```

## 方法 3: 使用 GitHub CLI

```bash
gh auth login
gh repo clone toneliu/nethealer
# 然后复制代码到克隆的仓库
```

## 验证推送成功

推送成功后，访问 https://github.com/toneliu/nethealer 确认代码已上传。
