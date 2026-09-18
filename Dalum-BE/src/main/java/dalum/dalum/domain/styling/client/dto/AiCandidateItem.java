package dalum.dalum.domain.styling.client.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.annotation.JsonRawValue;

public record AiCandidateItem(
        @JsonProperty("id") Long id,
        @JsonProperty("category") String category,
        @JsonProperty("style") String style,
        @JsonProperty("material_vector") @JsonRawValue String materialVectorJson,
        @JsonProperty("dominant_colors") @JsonRawValue String dominantColorsJson
) {
}