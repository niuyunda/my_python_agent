# Branch Protection Checklist (main)

在 GitHub 仓库 Settings → Branches → Add rule for `main`：

- ✅ Require a pull request before merging
- ✅ Require approvals: 1
- ✅ Dismiss stale pull request approvals when new commits are pushed
- ✅ Require status checks to pass before merging
  - required checks:
    - `test`
    - `actionlint`（当 workflow 变更时）
- ✅ Require conversation resolution before merging
- ✅ Do not allow bypassing the above settings（可选，团队时建议开启）
- ✅ Restrict who can push to matching branches（个人仓库可不设）

推荐 merge 策略：
- 默认使用 **Squash and merge**
