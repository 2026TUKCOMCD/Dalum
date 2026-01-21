package dalum.dalum.domain.like_product.converter;

import dalum.dalum.domain.like_product.dto.response.LikeToggleResponse;
import org.springframework.stereotype.Component;

@Component
public class LikeProductConverter {

    public LikeToggleResponse toLikeToggleResponse(boolean liked) {
        return new LikeToggleResponse(liked);
    }
}
