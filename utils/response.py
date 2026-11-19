from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
def sussess_response(msg : str ='success',data = None) :
    content = {
        'code' : 200,
        'msg' : msg,
        'data' : data
    }

    # 把任何的 fastapi、pydantic、orm对象 都正常响应 -> code message data
    return JSONResponse(content=jsonable_encoder(content))

