# Настройка защиты main ветки

## Автоматическая настройка (GitHub CLI)

Если у вас установлен GitHub CLI:

```bash
# Защита main ветки
gh api repos/TimShare/fun_oauth/branches/main/protection \
  --method PUT \
  --field required_status_checks='{"strict":true,"contexts":["test","quality"]}' \
  --field enforce_admins=true \
  --field required_pull_request_reviews='{"required_approving_review_count":1,"dismiss_stale_reviews":true}' \
  --field restrictions=null
```

## Ручная настройка через веб-интерфейс

1. Идите в Settings → Branches
2. Add branch protection rule для `main`
3. Настройки:

### ✅ Restrict pushes that create files
- [x] Require a pull request before merging
  - [x] Require approvals: 1
  - [x] Dismiss stale PR approvals when new commits are pushed
  - [x] Require review from code owners (если есть CODEOWNERS файл)

### ✅ Require status checks to pass
- [x] Require branches to be up to date before merging
- Добавить required checks:
  - `test` 
  - `quality`

### ✅ Other restrictions
- [x] Restrict pushes that create files
- [x] Do not allow bypassing the above settings

## Workflow после настройки

1. **Разработка**: работайте в `develop` ветке
   ```bash
   git checkout develop
   git pull origin develop
   # делаете изменения
   git add .
   git commit -m "Feature: ..."
   git push origin develop
   ```

2. **Pull Request в main**:
   - Создайте PR из `develop` в `main`
   - Дождитесь прохождения тестов и code review
   - Merge только после всех проверок

3. **Релизы**: создавайте теги в main
   ```bash
   git checkout main
   git pull origin main
   git tag v1.0.0
   git push origin v1.0.0
   ```

## Результат

После настройки:
- ❌ Прямой push в `main` запрещен
- ✅ Только merge через Pull Request  
- ✅ Обязательные проверки: тесты + code quality
- ✅ Обязательный code review (1 approver)
- ✅ Автоматическая сборка Docker образа при merge в main