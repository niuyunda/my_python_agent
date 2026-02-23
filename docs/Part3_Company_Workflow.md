# 第三部分：真实软件公司协作流程

在正规的软件公司，一个需求从产生到最终上线，要经历一套严密的工程化流程（通常采用敏捷开发 Agile / Scrum 模式）。我们来看看大家是如何各司其职的。

## 1. 团队角色分工

- **产品经理 (PM / Product Manager)**：负责弄清楚“做什么”，产出 PRD (产品需求文档) 和 UI 设计稿。
- **技术负责人 (Tech Lead)**：负责弄清楚“怎么做”，定义技术架构、数据库表结构和 API 接口定义。
- **开发工程师 (Dev / SWE)**：负责写代码、写单元测试，提交 PR。
- **测试工程师 (QA / Quality Assurance)**：负责编写测试用例，进行系统级别的集成测试和手工探索测试。
- **运维 / SRE (DevOps)**：负责 CI/CD 流程、服务器资源分配、线上监控和报警设置。

## 2. 从需求到上线的完整流程 (The Software Development Life Cycle - SDLC)

以“增加用户注册功能”为例：

1. **需求评审 (Sprint Planning)**：PM 拿着设计稿给所有工程师讲解，大家评估这个功能需要多长时间（估算 Story Points）。
2. **系统设计 (Design Doc)**：开发人员不急着写代码，先写一个简短的设计文档 (RFC: Request For Comments)，说明自己打算在哪个表加字段、加几个 API。找同事 Review 设计。
3. **开发与自测 (Implementation & Unit Testing)**：Dev 从 `main` 分支切出一个新的 `feature/user-registration` 分支开始写代码。完成核心逻辑，并写好自动化的**单元测试**（就像我们示例中的 `tests/unit/`）。
4. **代码审查 (Pull Request / Code Review)**：开发把代码 Push 到 GitHub，发起一个 PR 请求将 `feature` 分支合并回 `main`。同事收到通知，开始查阅你的代码。
5. **持续集成验证 (CI Checks)**：在同事看代码的同时，GitHub Actions 自动在云端把你的代码拉取下来，运行所有的单元测试和代码风格检查 (Lint)。如果有任何一个测试没过，就**不允许合并**。
6. **QA 环境集成测试 (Staging/Integration Testing)**：PR 被批准 (Approved) 并合并后，代码会自动部署到一个专供内部使用的测试环境 (Staging)。QA 在这里进行功能测试（包括我们刚才写的 Integration Test）。
7. **生产发布 (Production Release)**：测试无误后，创建一个版本标签（如 `v1.2.0`），触发自动部署管道，把代码推送到真实的线上服务器。
8. **监控 (Monitoring/Observability)**：上线后，留出半小时盯着监控仪表盘（Grafana / Datadog），确保错误率没有飙升。

## 3. PR 审查机制 (Code Review)

为什么要在合并代码前让同事 Review？
1. **防低级错误**：多一双眼睛，能发现逻辑漏洞、没处理的异常。
2. **传播知识**：让团队里的其他人都知道你改了什么模块，以后你休假了别人也能接手。
3. **统一风格**：保证 10 个人写出来的代码像 1 个人写的。

**如何 Review？**
Reviewer 会在 PR 页面逐行看代码并留评论。例如：“这里有个潜在的空指针异常”、“这个方法太长了，把它抽离出一个独立函数吧”。作者根据建议修改后再次 Push，直到 Reviewer 满意并点下 `Approve`。

## 4. 如何处理冲突 (Conflict Resolution)

如果在你写 `feature/A` 分支的时候，你的同事把 `feature/B` 合并到了主干，并且你们俩修改了同一个文件的同一行代码。此时你发起 PR 就会发生冲突 (Conflict)。
解决方法很简单：
1. 你在自己的分支执行 `git pull origin main --rebase`（或者 `git merge`）拉取最新主干代码。
2. Git 会提示冲突，你打开编辑器，手工解决保留哪一部分代码。
3. 跑一遍测试，确保解决冲突后没有弄坏项目，然后再 Push 你的修改。在正规流程下，**永远是谁的分支滞后，谁负责解决冲突**。

## 5. 如何版本发布与回滚

- **版本发布 (Release)**：通常遵循 **语义化版本 (Semantic Versioning, 格式 `Major.Minor.Patch`，如 `v1.2.3`)**。重大不兼容更新升 Major，增加新功能升 Minor，修复 Bug 升 Patch。
- **灰度发布 (Canary Release / Feature Flags)**：为了安全，新功能一开始可能只对 5% 的真实用户展现。如果没发现问题，再慢慢放大到 10%、50%，最后 100%。如果一出现大量报错，立刻把功能开关关掉（这也叫 Feature Flag）。
- **回滚 (Rollback)**：如果发布后服务器大面积宕机。绝对不要立刻在线上修 Bug！第一原则是**止血**：马上通过 CI 部署上一个稳定的版本（通常就是点个按钮的事），或者使用 `git revert` 撤销刚刚合并的 PR。等服务恢复平稳了，再在本地慢慢查找 Bug 的原因。
