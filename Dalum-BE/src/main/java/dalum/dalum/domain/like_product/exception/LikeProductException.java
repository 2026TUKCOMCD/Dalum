package dalum.dalum.domain.like_product.exception;

import dalum.dalum.global.apipayload.code.BaseErrorCode;
import dalum.dalum.global.apipayload.exception.GeneralException;

public class LikeProductException extends GeneralException {
    public LikeProductException(BaseErrorCode code) {
        super(code);
    }
}
