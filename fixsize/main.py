from flask import Flask, request, jsonify
from flask_cors import CORS
from threading import RLock
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

    # 1. 초기화
    def init(self, values=None):
        self.data = [None] * self.capacity
        self.front_index = 0
        self.count = 0

        if values is not None:
            if len(values) > self.capacity:
                raise ValueError("입력 배열이 큐 크기보다 큽니다.")

            for value in values:
                self.push(value)

        return self.dump()

    # 2. push
    def push(self, value):
        if self.is_full():
            raise ValueError("Queue is full")

        rear_index = (
            self.front_index + self.count
        ) % self.capacity

        self.data[rear_index] = value
        self.count += 1

        return self.dump()

    # 2. pop
    def pop(self):
        if self.is_empty():
            raise ValueError("Queue is empty")

        value = self.data[self.front_index]
        self.data[self.front_index] = None

        self.front_index = (
            self.front_index + 1
        ) % self.capacity

        self.count -= 1

        if self.count == 0:
            self.front_index = 0

        return value

    # 3. 현재 데이터 개수
    def size(self):
        return self.count

    # 4. 상태 검사
    def is_full(self):
        return self.count == self.capacity

    def is_empty(self):
        return self.count == 0

    def state(self):
        return {
            "full": self.is_full(),
            "empty": self.is_empty()
        }

    # 5. Front 확인
    def front(self):
        if self.is_empty():
            return None

        return self.data[self.front_index]

    # 6. 전체 삭제
    def clear(self):
        self.data = [None] * self.capacity
        self.front_index = 0
        self.count = 0

        return self.dump()

    # 7. 값의 인덱스 검색
    def index(self, value):
        for i, item in enumerate(self.dump()):
            if item == value:
                return i

        return -1

    # 8. 특정 값의 개수
    def value_count(self, value):
        return sum(
            1 for item in self.dump()
            if item == value
        )

    # 9. 값의 존재 여부
    def contains(self, value):
        return self.index(value) != -1

    # 10. Front부터 Rear까지 출력
    def dump(self):
        return [
            self.data[
                (self.front_index + i) % self.capacity
            ]
            for i in range(self.count)
        ]

    # 전체 상태 반환
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

# 전역 큐에 접근하는 요청을 동기화합니다.
queue_lock = RLock()


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

    with queue_lock:

        if request.method == "GET":
            return jsonify({
                "ok": True,
                "status": queue.status()
            })

        payload = request.get_json(silent=True) or {}
        action = payload.get("action", "dump")

        try:
            if action == "init":
                result = queue.init()
                message = "빈 큐로 초기화했습니다."

            elif action == "load":
                result = queue.init(INITIAL_DATA)
                message = "초기 배열을 삽입했습니다."

            elif action == "push":
                value = payload.get("value")

                if value is None:
                    raise ValueError("삽입할 값을 입력하세요.")

                result = queue.push(value)
                message = "push 완료"

            elif action == "pop":
                result = queue.pop()
                message = "pop 완료"

            elif action == "size":
                result = queue.size()
                message = "현재 데이터 개수"

            elif action == "state":
                result = queue.state()
                message = "큐 상태 확인"

            elif action == "front":
                result = queue.front()
                message = "Front 데이터 확인"

            elif action == "clear":
                result = queue.clear()
                message = "큐 전체 삭제 완료"

            elif action == "index":
                value = payload.get("value")

                if value is None:
                    raise ValueError("검색할 값을 입력하세요.")

                result = queue.index(value)
                message = "인덱스 검색 완료"

            elif action == "count":
                value = payload.get("value")

                if value is None:
                    raise ValueError("개수를 셀 값을 입력하세요.")

                result = queue.value_count(value)
                message = "값의 개수 확인 완료"

            elif action == "contains":
                value = payload.get("value")

                if value is None:
                    raise ValueError("확인할 값을 입력하세요.")

                result = queue.contains(value)
                message = "존재 여부 확인 완료"

            elif action == "dump":
                result = queue.dump()
                message = "전체 배열 출력 완료"

            elif action == "exam":
                queue.init(INITIAL_DATA)

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

                message = "시험 항목 1~8 완료"

            else:
                raise ValueError(
                    "지원하지 않는 기능: " + str(action)
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
