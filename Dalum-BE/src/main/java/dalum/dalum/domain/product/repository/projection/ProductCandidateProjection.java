package dalum.dalum.domain.product.repository.projection;

import dalum.dalum.domain.product.enums.LargeCategory;

public interface ProductCandidateProjection {
    Long getId();
    LargeCategory getLargeCategory();
    String getStyle();
    String getMaterialVectorJson();
    String getDominantColorsJson();
}