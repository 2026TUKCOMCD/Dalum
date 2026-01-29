package dalum.dalum.global.security.social.dto.response;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;

@JsonIgnoreProperties(ignoreUnknown = true)
public record NaverUserInfoResponse(
        String resultCode,
        String message,
        Response response
) {

    @JsonIgnoreProperties(ignoreUnknown = true)
    public record Response(
            String id,
            String nickname,
            String name,
            String email,
            String mobile,
            String gender,
            String birthyear,
            String birthday
    ) {}
}


