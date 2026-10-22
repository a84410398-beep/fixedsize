```python
from flask import Flask, request, jsonify
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

CAPACITY = 20

INITIAL_DATA = [
    19, 15, 29, 25, 33, 35, 49,
    42, 50, 55, 62, 66, 77, 80
]


class FixedSizeQueue:

    def __init__(self, capacity=20):
        self.capacity = capacity
        self.data = [None] * capacity
        self.front_index = 0
        self.count = 0

    def init(self, values=None):
        self.data = [None] * self.capacity
        self.front_index = 0
        self.count = 0

        if values is not None:
            for value in values:
                self.push(value)

        return self.dump()

    def push(self, value):
        if self.is_full():
            raise ValueError("큐가 가득 찼습니다.")

        rear_index = (
            self.front_index + self.count
        ) % self.capacity

        self.data[rear_index] = value
        self.count += 1

        return self.dump()

    def pop(self):
        if self.is_empty():
            raise ValueError("큐가 비어 있습니다.")

        removed_value = self.data[self.front_index]

        self.data[self.front_index] = None

        self.front_index = (
            self.front_index + 1
        ) % self.capacity

        self.count -= 1

        if self.count == 0:
            self.front_index = 0

        return removed_value

    def size(self):
        return self.count

    def is_full(self):
        return self.count == self.capacity

    def is_empty(self):
        return self.count == 0

    def state(self):
        return {
            "full": self.is_full(),
            "empty": self.is_empty()
        }

    def front(self):
        if self.is_empty():
            return None

        return self.data[self.front_index]

    def clear(self):
        self.data = [None] * self.capacity
        self.front_index = 0
        self.count = 0

        return self.dump()

    def index(self, value):
        items = self.dump()

        for i, item in enumerate(items):
            if item == value:
                return i

        return -1

    def value_count(self, value):
        return sum(
            1 for item in self.dump()
            if item == value
        )

    def contains(self, value):
        return self.index(value) != -1

    def dump(self):
        result = []

        for i in range(self.count):
            index = (
                self.front_index + i
            ) % self.capacity

            result.append(self.data[index])

        return result

    def status(self):
        return {
            "capacity": self.capacity,
            "size": self.size(),
            "full": self.is_full(),
            "empty": self.is_empty(),
            "front": self.front(),
            "items": self.dump()
        }


queue = FixedSizeQueue(CAPACITY)

queue.init()


@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "service": "Fixed-Size Queue",
        "status": "running",
        "capacity": CAPACITY
    })


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"ok": True})


@app.route(
    "/api/queue",
    methods=["GET", "POST", "OPTIONS"]
)
def queue_api():

    if request.method == "OPTIONS":
        return "", 204

    if request.method == "GET":
        return jsonify({
            "ok": True,
            "status": queue.status()
        })

    payload = request.get_json(silent=True) or {}
    action = payload.get("action", "status")

    try:

        if action == "init":
            result = queue.init()
            message = "빈 큐로 초기화했습니다."

        elif action == "load":
            queue.init()

            for value in INITIAL_DATA:
                queue.push(value)

            result = queue.dump()
            message = "제시된 배열을 push했습니다."

        elif action == "push":
            value = payload.get("value")

            if value is None:
                raise ValueError("삽입할 값을 입력하세요.")

            result = queue.push(value)
            message = f"{value}를 삽입했습니다."

        elif action == "pop":
            result = queue.pop()
            message = f"삭제한 값: {result}"

        elif action == "size":
            result = queue.size()
            message = "현재 데이터 개수입니다."

        elif action == "state":
            result = queue.state()
            message = "큐 상태를 확인했습니다."

        elif action == "front":
            result = queue.front()
            message = "Front 데이터를 확인했습니다."

        elif action == "clear":
            result = queue.clear()
            message = "큐 전체 데이터를 삭제했습니다."

        elif action == "index":
            value = payload.get("value")

            if value is None:
                raise ValueError("검색할 값을 입력하세요.")

            result = queue.index(value)
            message = "값의 인덱스를 검색했습니다."

        elif action == "count":
            value = payload.get("value")

            if value is None:
                raise ValueError("개수를 셀 값을 입력하세요.")

            result = queue.value_count(value)
            message = "값의 개수를 확인했습니다."

        elif action == "contains":
            value = payload.get("value")

            if value is None:
                raise ValueError("확인할 값을 입력하세요.")

            result = queue.contains(value)
            message = "값의 존재 여부를 확인했습니다."

        elif action == "dump":
            result = queue.dump()
            message = "큐 전체 데이터를 출력했습니다."

        elif action == "exam":
            queue.init()

            for value in INITIAL_DATA:
                queue.push(value)

            result = {
                "1_capacity": queue.capacity,
                "2_pushed_array": queue.dump(),
                "3_current_size": queue.size(),
                "4_current_state": queue.state(),
                "5_front_data": queue.front(),
                "6_index_of_42": queue.index(42),
                "6_count_of_42": queue.value_count(42),
                "7_contains_88": queue.contains(88),
                "8_full_array": queue.dump()
            }

            message = "사진의 시험 항목 1~8을 완료했습니다."

        else:
            raise ValueError(
                f"지원하지 않는 기능입니다: {action}"
            )

        return jsonify({
            "ok": True,
            "action": action,
            "message": message,
            "result": result,
            "status": queue.status()
        })

    except (ValueError, TypeError) as error:
        return jsonify({
            "ok": False,
            "action": action,
            "error": str(error),
            "status": queue.status()
        }), 400


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8080"))

    app.run(
        host="0.0.0.0",
        port=port
    )
```
