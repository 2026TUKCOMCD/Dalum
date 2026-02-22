package dalum.dalum.global.s3;

import io.awspring.cloud.s3.ObjectMetadata;
import io.awspring.cloud.s3.S3Template;
import lombok.RequiredArgsConstructor;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.util.UUID;

@Service
@RequiredArgsConstructor
public class S3Service {

    private final S3Template s3Template;

    @Value("${spring.cloud.aws.s3.bucket}")
    private String bucketName;

    public String uploadFile(MultipartFile file) throws IOException {
        // 1. 파일 이름 중복 방지를 위해 UUID 추가
        String originalFileName = file.getOriginalFilename();
        String uuidFileName = UUID.randomUUID() + "_" + originalFileName;

        // 2. 메타데이터 설정
        ObjectMetadata metadata = ObjectMetadata.builder()
                .contentType(file.getContentType())
                .contentLength(file.getSize())
                .build();

        // 3. 업로드 (InputStream)
        s3Template.upload(bucketName, uuidFileName, file.getInputStream(), metadata);

        // URL 반환
        return s3Template.download(bucketName, uuidFileName).getURL().toString();
    }

    // 삭제 기능(필요하다면)
    public void deleteFile(String fileName) {
        s3Template.deleteObject(bucketName, fileName);
    }
}
