package dalum.dalum.global.security.social.dto.response;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.annotation.JsonProperty;

@JsonIgnoreProperties(ignoreUnknown = true)
public record GoogleUserInfoResponse(
        String sub,
        String name,
        @JsonProperty("given_name") String givenName,
        @JsonProperty("family_name") String familyName,
        String picture,
        String email,
        @JsonProperty("email_verified") Boolean emailVerified,
        String locale
) {}
