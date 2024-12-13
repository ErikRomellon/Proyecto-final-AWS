package mx.uady.aws.tests;

import io.restassured.builder.RequestSpecBuilder;
import io.restassured.http.ContentType;
import io.restassured.specification.RequestSpecification;
import mx.uady.aws.Constants;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;

import java.io.File;
import java.util.Map;

import static io.restassured.RestAssured.given;
import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.core.IsEqual.equalTo;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

public class S3ApiTest extends AlumnosApiTest {

    @BeforeAll
    public static void setUrl() {
        URL = Constants.URL;
        SPEC = new RequestSpecBuilder().setBaseUri(URL).build();
    }

    @Test
    public void testUploadProfilePicture() {

        Map<String, Object> alumno = getAlumno();

        int alumnoId = crearAlumno(alumno);

        String url = given().spec(SPEC)
            .contentType(ContentType.MULTIPART)
            .multiPart("foto", new File("src/test/resources/cat_test.jpg"))
            .post("alumnos/" + alumnoId + "/fotoPerfil")
            .then()
            .statusCode(200).contentType(ContentType.JSON)
            .extract()
            .path("fotoPerfilUrl");

        assertFalse(url.isEmpty());
        assertTrue(url.contains("s3.amazonaws.com"));

        url = given().spec(SPEC)
                .contentType(ContentType.JSON)
                .body(alumno)
                .get("/alumnos/" + alumnoId)
                .then()
                .statusCode(200).contentType(ContentType.JSON)
                .extract().path("fotoPerfilUrl");

        assertFalse(url.isEmpty());
        assertTrue(url.contains("s3.amazonaws.com"));

    }

    @Test
    public void testCheckS3Picture() {

        Map<String, Object> alumno = getAlumno();

        int alumnoId = crearAlumno(alumno);

        String url = given().spec(SPEC)
                .contentType(ContentType.MULTIPART)
                .multiPart("foto", new File("src/test/resources/cat_test.jpg"))
                .post("alumnos/" + alumnoId + "/fotoPerfil")
                .then()
                .statusCode(200).contentType(ContentType.JSON)
                .extract()
                .path("fotoPerfilUrl");

        assertFalse(url.isEmpty());

        System.out.println(url);

        given().baseUri(url).head().then().statusCode(200);

    }
}
