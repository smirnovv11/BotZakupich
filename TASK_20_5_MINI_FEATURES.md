# Task 20.5. List edit mode, checklist pagination, and catalog expansion

Дата: 2026-08-21

## Зачем

Перед Task 21 нужно закрыть маленький UX-долг в текущем Telegram flow: длинные списки неудобно смотреть и использовать, товары нельзя удалить из текущего списка через бот, а локальный categorizer пока не узнает часть обычных продуктов.

MVP по-прежнему остается personal-only, без OpenAI/AI runtime, без shared lists, без `list_members`, без Redis/FSM.

## Scope

### 1. Удаление товаров из текущего списка

Добавить кнопку `Удалить` при просмотре текущего списка покупок.

Flow:

1. Пользователь открывает текущий список.
2. Под списком есть кнопка `Удалить`.
3. После нажатия бот показывает inline checklist товаров текущего списка.
4. Нажатие на товар отмечает/снимает его для удаления.
5. Пользователь подтверждает удаление отдельной inline-кнопкой.
6. Выбранные товары удаляются из текущего draft/shopping list.

UX notes:

- Не задавать уточняющих вопросов.
- Если ничего не выбрано, не удалять товары и показать понятный короткий ответ.
- Не удалять archived items через этот flow.
- Старый shopping/archive restore flow не ломать.

Suggested button labels:

- Main action: `Удалить`
- Confirm action: `Удалить выбранное`
- Cancel/back action: `Назад`

### 2. Pagination для checklist flows

Добавить pagination для всех inline checklist, где пользователь нажимает товары:

- edit/delete checklist текущего списка;
- shopping checklist;
- restore selected checklist из архива, если текущая реализация показывает много товаров inline.

Правило страниц:

- Основная модель: `1 страница = 1 категория`.
- Внутри категории показывать не больше 10 товаров на странице.
- Если в категории больше 10 товаров, разбивать эту категорию на несколько страниц.
- Навигация: `Назад` и `Вперед`.
- На первой странице не показывать `Назад`.
- На последней странице не показывать `Вперед`.

Technical notes:

- Pagination и callback data должны жить в presentation layer: callback builders/parsers и keyboard builders.
- Use cases не должны знать про страницы Telegram UI.
- Callback values, prefixes, button text, page size и mode strings вынести в `*Enum` / constants.
- Не добавлять Redis/FSM; selection state должен быть encoded in callback data или восстановим из текущего списка/сообщения без внешнего state. Если callback data станет слишком длинной, выбрать минимальный server-side подход только после отдельного решения.

### 3. Расширение локального categorizer/parser vocabulary

Добавить больше обычных товаров в локальные правила без AI.

Минимальный список:

- `кола` -> `Напитки`
- `coca-cola`, `кока-кола` -> `Напитки`
- `чипсы` -> `Сладости и снеки`
- `сливки` -> `Молочные продукты`
- `мясо` -> `Мясо и птица`
- `курица` -> `Мясо и птица`
- `свинина` -> `Мясо и птица`
- `бедра`, `бедро` -> `Мясо и птица`
- `голень`, `голени` -> `Мясо и птица`

Сохранить текущее поведение:

- исходная позиция сохраняется как `display_text`;
- количество и единица остаются soft-parsed;
- неизвестные товары сохраняются в `Прочие`;
- OpenAI/AI runtime не добавлять.

## Suggested implementation order

1. Найти текущие keyboard/callback builders для list, checklist и archive restore.
2. Вынести общий pagination helper для grouped checklist pages, если он реально уменьшает дублирование.
3. Добавить callback models для paginated checklist modes.
4. Добавить use case удаления выбранных current-list items, если существующие repositories не дают безопасной операции.
5. Подключить кнопку `Удалить` в current-list view.
6. Подключить paginated keyboard в shopping checklist.
7. Подключить paginated keyboard в edit/delete checklist.
8. При необходимости подключить pagination к restore selected checklist.
9. Расширить локальный словарь categorizer/parser.
10. Добавить focused unit/integration tests.

## Acceptance criteria

- При просмотре текущего списка есть кнопка `Удалить`.
- Пользователь может выбрать товары в inline checklist и удалить выбранные из текущего списка.
- Удаление не затрагивает archived trips.
- Shopping checklist paginated по категориям и не показывает больше 10 товаров на странице.
- Edit/delete checklist paginated по тем же правилам.
- Кнопки `Назад`/`Вперед` появляются только там, где есть предыдущая/следующая страница.
- Товары `кола`, `чипсы`, `сливки`, `мясо`, `курица`, `свинина`, `бедра`, `голень` распознаются локально.
- MVP не содержит OpenAI/AI runtime calls.
- `list_members`, shared lists, Redis/FSM не добавлены.

## Verification

```bash
pytest --basetemp .pytest_tmp
ruff check .
ruff format --check .
```

Manual Telegram smoke:

1. Add 20+ mixed-category items.
2. Open current list and enter `Удалить`.
3. Navigate pages, select a few items, confirm deletion.
4. Start shopping, navigate checklist pages, toggle items.
5. Add `кола, чипсы, сливки, мясо, курица, свинина, бедра, голень` and check categories.
