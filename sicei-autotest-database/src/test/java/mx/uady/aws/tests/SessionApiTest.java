package mx.uady.aws.tests;

import io.restassured.http.ContentType;
import mx.uady.aws.Constants;
import org.junit.jupiter.api.Test;

import java.util.HashMap;
import java.util.Map;

import static io.restassured.RestAssured.given;

public class SessionApiTest extends AlumnosApiTest {

    @Test
    public void createSession() {
        Map<String, Object> alumno = getAlumno();
        String password = (String) alumno.get("password");
        int alumnoId = crearAlumno(alumno);

        Map<String, Object> body = new HashMap<>();
        body.put("password", password);

        String sessionString = given().spec(SPEC)
                .contentType(ContentType.JSON)
                .body(body)
                .post("/alumnos/" + alumnoId + "/session/login")
                .then()
                .statusCode(200).contentType(ContentType.JSON)
                .extract()
                .path("sessionString");

        assert (sessionString.length() == 128);
    }

    @Test
    public void createSessionWithWrongPassword() {
        Map<String, Object> alumno = getAlumno();
        String password = (String) alumno.get("password");
        int alumnoId = crearAlumno(alumno);

        Map<String, Object> body = new HashMap<>();
        body.put("password", password + "abc"); // WRONG password

        given().spec(SPEC)
                .contentType(ContentType.JSON)
                .body(body)
                .post("/alumnos/" + alumnoId + "/session/login")
                .then()
                .statusCode(400);
    }

    @Test
    public void verifySession() {
        Map<String, Object> alumno = getAlumno();
        String password = (String) alumno.get("password");
        int alumnoId = crearAlumno(alumno);

        Map<String, Object> body = new HashMap<>();
        body.put("password", password);

        String sessionString = given().spec(SPEC)
                .contentType(ContentType.JSON)
                .body(body)
                .post("/alumnos/" + alumnoId + "/session/login")
                .then()
                .statusCode(200).contentType(ContentType.JSON)
                .extract()
                .path("sessionString");

        Map<String, Object> sessionBody = new HashMap<>();
        sessionBody.put("sessionString", sessionString);

        given().spec(SPEC)
                .contentType(ContentType.JSON)
                .body(sessionBody)
                .post("/alumnos/" + alumnoId + "/session/verify")
                .then()
                .statusCode(200).contentType(ContentType.JSON);
    }

    @Test
    public void verifyInvalidSession() {
        Map<String, Object> alumno = getAlumno();
        String password = (String) alumno.get("password");
        int alumnoId = crearAlumno(alumno);

        Map<String, Object> body = new HashMap<>();
        body.put("password", password);

        String sessionString = given().spec(SPEC)
                .contentType(ContentType.JSON)
                .body(body)
                .post("/alumnos/" + alumnoId + "/session/login")
                .then()
                .statusCode(200).contentType(ContentType.JSON)
                .extract()
                .path("sessionString");

        Map<String, Object> sessionBody = new HashMap<>();
        sessionBody.put("sessionString", Constants.getRandomString(128)); // Invalid Session

        given().spec(SPEC)
                .contentType(ContentType.JSON)
                .body(sessionBody)
                .post("/alumnos/" + alumnoId + "/session/verify")
                .then()
                .statusCode(400).contentType(ContentType.JSON);
    }

    @Test
    public void expireSession() {
        Map<String, Object> alumno = getAlumno();
        String password = (String) alumno.get("password");
        int alumnoId = crearAlumno(alumno);

        Map<String, Object> body = new HashMap<>();
        body.put("password", password);

        String sessionString = given().spec(SPEC)
                .contentType(ContentType.JSON)
                .body(body)
                .post("/alumnos/" + alumnoId + "/session/login")
                .then()
                .statusCode(200).contentType(ContentType.JSON)
                .extract()
                .path("sessionString");

        Map<String, Object> sessionBody = new HashMap<>();
        sessionBody.put("sessionString", sessionString);

        given().spec(SPEC)
                .contentType(ContentType.JSON)
                .body(sessionBody)
                .post("/alumnos/" + alumnoId + "/session/verify")
                .then()
                .statusCode(200).contentType(ContentType.JSON);

        // --- logout
        given().spec(SPEC)
                .contentType(ContentType.JSON)
                .body(sessionBody)
                .post("/alumnos/" + alumnoId + "/session/logout")
                .then()
                .statusCode(200).contentType(ContentType.JSON);

        given().spec(SPEC)
                .contentType(ContentType.JSON)
                .body(sessionBody)
                .post("/alumnos/" + alumnoId + "/session/verify")
                .then()
                .statusCode(400).contentType(ContentType.JSON);
    }

}
