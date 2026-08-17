from fastapi import FastAPI, HTTPException, status,Query
import database
from pydantic import BaseModel, Field

class RecordCreate(BaseModel):  #职责:客户端创建记录时提交什么
    content: str = Field(min_length=1, max_length=200)


class RecordUpdate(BaseModel):
    content: str | None = Field(
        default=None,
        min_length=1,
        max_length=200
    )
    completed: bool | None = None

class RecordResponse(BaseModel):  #职责:服务器返回一条记录时包含什么
    id: str
    content: str
    completed: bool
    created_at: str
    updated_at: str | None = None

class RecordListResponse(BaseModel):  #职责:服务器返回多条记录时包含什么
    total: int
    count: int
    limit: int
    offset: int
    items: list[RecordResponse]  #items 是列表，列表中的每个元素都应该符合 RecordResponse。

class DeleteRecordResponse(BaseModel): #职责:服务器返回删除记录时包含什么
    message: str
    record: RecordResponse

app = FastAPI(title="AI学习助手 API")
database.init_db()

@app.get("/")
def read_root():
    return{
        "message": "AI学习助手 API 已启动"
    }

@app.get("/health")
def read_health():
    return {
        "status": "ok"
    }

@app.get(
    "/records",
         response_model=RecordListResponse
    )
def list_records(
    q: str | None = Query(
        default=None,
        max_length=50
    ),
    completed: bool | None = None,
    limit: int = Query(
        default=10,
        ge=1,
        le=100
    ),
    offset: int = Query(
        default=0,
        ge=0
    ),
):  #FastAPI会自动把?completed=true转换为Python completed= true`
    if q is not None:
        q = q.strip()

        if not q:  #空字符串在判断中相当于 False
            raise HTTPException(
                status_code=422,
                detail="搜索条件不能为空"
            )

    items = database.list_records(
        q=q,
        completed=completed,
        limit=limit,
        offset=offset
    )

    total = database.count_records(completed=completed,q=q)

    return{
        "total": total,
        "count": len(items),
        "limit": limit,
        "offset": offset,
        "items": items
    }

@app.post(
    "/records",
    response_model=RecordResponse,
    status_code=status.HTTP_201_CREATED
)# 创建记录
def create_record_api(request: RecordCreate):
    content = request.content.strip()

    if not content:
        raise HTTPException(
            status_code=422,
            detail="记录不能为空"
        )

    # history = record_service.load_history()
    # record = record_service.add_record(history,content)
    # saved = record_service.save_history(history)
    record = database.insert_record(content)

    # if not saved:
    #     raise HTTPException(
    #         status_code=500,
    #         detail="记录保存失败"
    #     )

    return record

@app.get(
    "/records/{record_id}",
    response_model=RecordResponse
)  #{record_id}是路径参数
def get_record(record_id: str):
    # history = record_service.load_history()
    # record = record_service.find_record_by_id(history,record_id)
    record = database.get_record_by_id(record_id)

    if record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="记录不存在"
        )
    return record

@app.delete(
    "/records/{record_id}",
    response_model=DeleteRecordResponse
)
def delete_record_api(record_id: str):
    # history = record_service.load_history()
    # delete_record = record_service.delete_record_by_id(history,record_id)
    delete_record = database.delete_record_by_id(record_id)

    if delete_record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="记录不存在"
        )

    # if not record_service.save_history(history):
    #     raise HTTPException(
    #         status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    #         detail="删除记录但保存失败"
    #     )

    return {
        "message": "记录删除成功",
        "record": delete_record
    }

@app.patch(
    "/records/{record_id}",
    response_model=RecordResponse
)
def updated_record_api(record_id: str, request: RecordUpdate):
    updates = request.model_dump(exclude_none=True)  # 映射成字典,将None值排除

    if not updates:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="至少需要提供一个修改字段"
        )

    if "content" in updates:
        content = updates["content"].strip()

        if not content:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail="记录内容不能为空"
            )

        updates["content"] = content


    # history = record_service.load_history()
    # updated_record = record_service.update_record_by_id(history,
    #                                                    record_id,
    #                                                    updates)
    updated_record = database.update_record_by_id(record_id,updates)

    if updated_record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="记录不存在"
        )

    # if not record_service.save_history(history):
    #     raise HTTPException(
    #         status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    #         detail="修改记录但保存失败"
    #     )#数据库内部函数已经commit()

    return updated_record








