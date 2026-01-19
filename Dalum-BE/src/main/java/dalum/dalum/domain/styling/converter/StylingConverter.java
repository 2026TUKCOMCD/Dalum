package dalum.dalum.domain.styling.converter;

import dalum.dalum.domain.product.dto.response.ProductDto;
import dalum.dalum.domain.styling.dto.response.StylingRecommendationResponse;
import dalum.dalum.domain.styling.entity.Styling;
import org.springframework.stereotype.Component;

import java.util.List;

@Component
public class StylingConverter {

    public StylingRecommendationResponse toResponse(Styling styling, ProductDto mainItem, List<ProductDto> resultItems) {
        return StylingRecommendationResponse.builder()
                .stylingId(styling.getId())
                .createdAt(styling.getCreatedAt())
                .mainItem(mainItem)
                .resultItems(resultItems)
                .build();
    }
}
