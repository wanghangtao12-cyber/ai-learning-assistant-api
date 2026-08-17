import pytest
from fastapi.testclient import TestClient

import database
from api import app


@pytest.fixture
def client(tmp_path,monkeypatch):
    test_db = tmp_path / "test.db"

    monkeypatch.setattr(
        database,
        "DB_FILE",
        test_db
    )
    database.init_db()

    return TestClient(app)


def test_health(client):
    response = client.get("/health")  #response是一个响应体对象

    assert response.status_code == 200
    assert response.json() == {"status" : "ok"}

def test_create_and_get_record(client):
    create_response = client.post(
        "/records",
        json ={"content": "学习自动化测试"}
    )

    assert create_response.status_code == 201

    create_record = create_response.json()
    record_id = create_record["id"]

    assert create_record["content"] == "学习自动化测试"
    assert create_record["created_at"] is not None

    get_response = client.get(f"/records/{record_id}")

    assert get_response.status_code == 200
    assert get_response.json()["id"] == record_id
    assert get_response.json()["content"] == "学习自动化测试"

def test_create_rejects_blank_content(client):
    # POST /records
    create_response = client.post(
        "/records",
        json ={"content": "   "}
    )

    assert create_response.status_code == 422


def test_update_record(client):
    create_response = client.post(
        "/records",
        json={"content": "更新测试"}
    )

    assert create_response.status_code == 201
    create_record = create_response.json()
    record_id = create_record["id"]

    updated_response = client.patch(
        f"/records/{record_id}",
        json={"content": "已更新"}
    )

    assert updated_response.status_code == 200
    assert updated_response.json()["content"] == "已更新"
    assert updated_response.json()["updated_at"] is not None


def test_delete_record(client):
    create_response = client.post(
        "/records",
        json={"content": "删除测试"}
    )

    assert create_response.status_code == 201

    create_record = create_response.json()  # 获取创建的记录的id
    record_id = create_record["id"]

    delete_response = client.delete(
        f"/records/{record_id}"
    )

    assert delete_response.status_code == 200

    find_response = client.get(
        f"/records/{record_id}"
    )

    assert find_response.status_code == 404

def test_mark_record_complete(client):
    create_response = client.post(
        "/records",
        json={"content": "完成测试"}
    )

    assert create_response.status_code == 201

    create_record = create_response.json()
    record_id = create_record["id"]

    assert create_record["completed"] is False

    update_response = client.patch(
        f"/records/{record_id}",
        json={"completed": True}
    )

    assert update_response.status_code == 200

    updated_record = update_response.json()

    assert updated_record["completed"] is True
    assert updated_record["updated_at"] is not None
    assert updated_record["id"] == record_id
    assert updated_record["content"] == "完成测试"


    get_response = client.get(
        f"/records/{record_id}"
    )

    assert get_response.status_code == 200
    assert get_response.json()["completed"] is True

def test_update_rejects_empty_body(client):
    create_response = client.post(
        "/records",
        json={"content": "测试空更新"}
    )

    assert create_response.status_code == 201

    record_id = create_response.json()["id"]  # 获取创建的记录的id

    update_response = client.patch(
        f"/records/{record_id}",
        json={}
    )

    assert update_response.status_code == 422

def test_filter_records_by_completed(client):
    first_response  = client.post(
        "/records",
        json={"content": "测试-已完成的学习任务"}
    )

    second_response  = client.post(
        "/records",
        json={"content": "测试-未完成的学习任务"}
    )

    first_id = first_response.json()["id"]
    second_id = second_response.json()["id"]

    update_response = client.patch(
        f"/records/{first_id}",
        json={"completed": True}
    )

    assert update_response.status_code == 200

    completed_records = client.get(
        "/records?completed=true"
    )

    assert completed_records.status_code == 200

    completed_data = completed_records.json()

    assert completed_data["count"] == 1
    assert completed_data["total"] == 1

    assert completed_data["items"][0]["id"] == first_id
    assert completed_data["items"][0]["completed"] is True
    assert completed_data["items"][0]["content"] == "测试-已完成的学习任务"

    pending_records = client.get(
        "/records?completed=false"
    )

    assert pending_records.status_code == 200

    pending_data = pending_records.json()
    assert pending_data["count"] == 1
    assert pending_data["total"] == 1
    assert pending_data["items"][0]["id"] == second_id
    assert pending_data["items"][0]["completed"] is False
    assert pending_data["items"][0]["content"] == "测试-未完成的学习任务"

def test_filter_rejects_invalid_completed(client):
    response = client.get(
        "/records?completed=invalid"
    )

    assert response.status_code == 422


def test_list_records_pagination(client):
    created_ids = []

    for index in range(10):
        response = client.post(
            "/records",
            json={"content": f"分页测试-第{index}条记录"}
        )

        assert response.status_code == 201

        created_ids.append(
            response.json()["id"]
        )

    page_one_response = client.get(
        "/records?limit=4&offset=0"

    )
    page_two_response = client.get(
        "/records?limit=4&offset=4"

    )
    page_three_response = client.get(
        "/records?limit=4&offset=8"
    )

    assert page_one_response.status_code == 200
    assert page_two_response.status_code == 200
    assert page_three_response.status_code == 200

    page_one_data = page_one_response.json()

    assert page_one_data["total"] == 10
    assert page_one_data["count"] == 4
    assert page_one_data["limit"] == 4
    assert page_one_data["offset"] == 0

    page_two_data = page_two_response.json()
    assert page_two_data["total"] == 10
    assert page_two_data["count"] == 4
    assert page_two_data["limit"] == 4
    assert page_two_data["offset"] == 4

    page_three_data = page_three_response.json()
    assert page_three_data["total"] == 10
    assert page_three_data["count"] == 2
    assert page_three_data["limit"] == 4
    assert page_three_data["offset"] == 8


def test_pagination_rejects_invalid_parameters(client):
    invalid_urls = [
        "/records?limit=0",
        "/records?limit=101",
        "/records?offset=-1",
    ]

    for url in invalid_urls:
        response = client.get(url)
        assert response.status_code == 422

def test_search_records_by_keywords(client):
    contents = [
        "学习FastAPI接口测试",
        "FastAPI分页功能",
        "学习SQLite"
    ]

    for content in contents:
        response = client.post(
            "/records",
            json={"content": content}
        )
        assert response.status_code == 201

    search_response = client.get(
        "/records?q=FastAPI"
    )

    assert search_response.status_code == 200

    search_data = search_response.json()

    assert search_data["count"] == 2
    assert search_data["total"] == 2

    results = [
        "FastAPI" in item["content"]
        for item in search_data["items"]
    ]

    assert all(results) # 所有结果都包含"FastAPI"即都为True

@pytest.mark.parametrize(
    "keyword,expected_status",
    [
        ("F",200),
        ("a" * 50, 200),
        ("", 422),
        ("   ", 422),
        ("a" * 51, 422)
    ],
    ids= [
        "TC-SEARCH-006",
        "TC-SEARCH-007",
        "TC-SEARCH-004",
        "TC-SEARCH-005",
        "TC-SEARCH-008",
    ]
)

def test_search_keywords_validation(
        client,
        keyword,
        expected_status
):
    response = client.get(
        "/records",
        params={"q": keyword}  #会自动生成查询参数
    )

    assert response.status_code == expected_status

def test_tc_search_002_return_empty_when_no_match(client):
    test_contents = [
        "FastAPI查询功能测试1",
        "FastAPI查询功能测试2"
    ]

    for content in test_contents:
        create_response = client.post(
            "/records",
            json={"content": content}
        )

        assert create_response.status_code == 201

    search_response = client.get(
        "/records",
        params={"q": "绝对不存在_TC_SEARCH_002"}
    )

    assert search_response.status_code == 200

    search_data = search_response.json()
    assert search_data["count"] == 0
    assert search_data["total"] == 0
    assert search_data["items"] == []
    assert search_data["limit"] == 10
    assert search_data["offset"] == 0


