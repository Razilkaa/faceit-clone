# Как взять данные матча из FACEIT API в Git Bash

Для первых задач можно использовать учебный `match.json`, но реальный источник данных - FACEIT Data API.

Важно: API key не коммить в репозиторий и не вставляй прямо в код. Храни его в переменной окружения.

## Что нужно получить

Для анализа матча обычно нужны три шага:

1. Найти свой `player_id` по nickname.
2. Получить историю матчей игрока и взять `match_id`.
3. Скачать статистику конкретного матча по `match_id`.

Все команды ниже рассчитаны на Git Bash.

## 1. Сохрани API key и nickname

```bash
export FACEIT_API_KEY="PASTE_YOUR_KEY_HERE"
export FACEIT_NICKNAME="YOUR_NICKNAME"
```

Эти переменные живут только в текущем окне Git Bash. После перезапуска терминала их нужно задать снова.

Проверка без вывода ключа:

```bash
test -n "$FACEIT_API_KEY" && echo "FACEIT_API_KEY is set"
test -n "$FACEIT_NICKNAME" && echo "FACEIT_NICKNAME is set: $FACEIT_NICKNAME"
```

## 2. Получи свой player_id

```bash
mkdir -p data

curl -s \
  -H "Authorization: Bearer $FACEIT_API_KEY" \
  "https://open.faceit.com/data/v4/players?nickname=$FACEIT_NICKNAME&game=cs2" \
  -o data/player.json
```

Красиво посмотреть ответ:

```bash
python -m json.tool data/player.json
```

Достать `player_id` в переменную:

```bash
export FACEIT_PLAYER_ID=$(
  python -c "import json; print(json.load(open('data/player.json', encoding='utf-8'))['player_id'])"
)

echo "$FACEIT_PLAYER_ID"
```

## 3. Получи последние матчи игрока

```bash
curl -s \
  -H "Authorization: Bearer $FACEIT_API_KEY" \
  "https://open.faceit.com/data/v4/players/$FACEIT_PLAYER_ID/history?game=cs2&limit=5" \
  -o data/player_history.json
```

Вывести последние матчи в коротком виде:

```bash
python - <<'PY'
import json

with open("data/player_history.json", encoding="utf-8") as file:
    history = json.load(file)

for index, match in enumerate(history.get("items", []), start=1):
    print(index, match.get("match_id"), match.get("status"), match.get("game_mode"))
PY
```

## 4. Возьми match_id и скачай статистику матча

Взять первый матч из истории:

```bash
export FACEIT_MATCH_ID=$(
  python -c "import json; print(json.load(open('data/player_history.json', encoding='utf-8'))['items'][0]['match_id'])"
)

echo "$FACEIT_MATCH_ID"
```

Скачать статистику:

```bash
curl -s \
  -H "Authorization: Bearer $FACEIT_API_KEY" \
  "https://open.faceit.com/data/v4/matches/$FACEIT_MATCH_ID/stats" \
  -o data/match_stats.json
```

Красиво посмотреть начало файла:

```bash
python -m json.tool data/match_stats.json | head -80
```

Именно `data/match_stats.json` потом можно использовать как реальный источник для задач по парсингу.

## Где лежат игроки внутри match_stats.json

Обычно нужный путь такой:

```text
rounds -> teams -> players -> player_stats
```

Упрощенно:

```python
for round_data in data["rounds"]:
    for team in round_data["teams"]:
        for player in team["players"]:
            nickname = player["nickname"]
            stats = player["player_stats"]
```

Названия ключей внутри `player_stats` могут отличаться от учебных `kills` и `deaths`. Поэтому сначала нужно вывести ключи и посмотреть, как FACEIT назвал поля в твоем матче.

```bash
python - <<'PY'
import json

with open("data/match_stats.json", encoding="utf-8") as file:
    data = json.load(file)

first_player = data["rounds"][0]["teams"][0]["players"][0]

print(first_player["nickname"])
print(first_player["player_stats"].keys())
PY
```

## Как это связано с задачей 1A

Для первого прохода проще взять учебный `match.json`, чтобы не застрять на API key и структуре ответа.

После этого можно сделать второй проход:

1. Скачать `data/match_stats.json` из FACEIT.
2. Найти реальные поля kills/deaths в `player_stats`.
3. Превратить FACEIT-структуру в простой список игроков.
4. Уже потом посчитать K/D.

Это нормальный инженерный путь: сначала понять алгоритм на простых данных, потом подключить реальный источник.

## Официальные ссылки

- FACEIT Data API: https://docs.faceit.com/docs/data-api/
- Data API endpoints: https://docs.faceit.com/docs/data-api/data/
