package mx.uady.aws.tests;

import io.restassured.builder.RequestSpecBuilder;
import io.restassured.http.ContentType;
import io.restassured.specification.RequestSpecification;
import mx.uady.aws.Constants;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;

import java.util.HashMap;
import java.util.Map;

import static io.restassured.RestAssured.get;
import static io.restassured.RestAssured.given;
import static org.hamcrest.core.IsEqual.equalTo;

public class ProfesoresApiTest {

    private static String URL;
    private static RequestSpecification SPEC;

    @BeforeAll
    public static void setUrl() {
        URL = Constants.URL;
        SPEC = new RequestSpecBuilder().setBaseUri(URL).build();
    }

    @Test
    public void testInvalidPath() {
        given().spec(SPEC)
                .get("/profesoresinvaidpath")
                .then()
                .statusCode(404);
    }

    @Test
    public void testUnsuportedMethod() {
        given().spec(SPEC)
                .delete("/profesores")
                .then()
                .statusCode(405);
    }

    @Test
    public void testGetProfesores() {
        given().spec(SPEC)
                .get("/profesores")
                .then()
                .statusCode(200).contentType(ContentType.JSON);
    }

    @Test
    public void testPostProfesor() {

        Map<String, Object> alumno = getProfesor();

        given().spec(SPEC)
                .contentType(ContentType.JSON)
                .body(alumno)
                .post("/profesores")
                .then()
                .statusCode(201).contentType(ContentType.JSON);
    }

    @Test
    public void testGetProfesorById() {

        Map<String, Object> profesor = getProfesor();

        int profesorId = crearProfesor(profesor);

        given().spec(SPEC)
                .contentType(ContentType.JSON)
                .body(profesor)
                .get("/profesores/" + profesorId)
                .then()
                .statusCode(200).contentType(ContentType.JSON)
                .body("nombres", equalTo(profesor.get("nombres")))
                .body("horasClase", equalTo(profesor.get("horasClase")));
    }

    @Test
    public void testPutProfesor() {

        Map<String, Object> profesor = getProfesor();

        int profesorId = crearProfesor(profesor);

        given().spec(SPEC)
                .contentType(ContentType.JSON)
                .body(profesor)
                .get("/profesores/" + profesorId)
                .then()
                .statusCode(200).contentType(ContentType.JSON)
                .body("nombres", equalTo(profesor.get("nombres")))
                .body("horasClase", equalTo(profesor.get("horasClase")));

        profesor.put("nombres", "Nuevo Profesor");
        profesor.put("horasClase", Constants.getRandomHoras());

        given().spec(SPEC)
                .contentType(ContentType.JSON)
                .body(profesor)
                .put("/profesores/" + profesorId)
                .then()
                .statusCode(200).contentType(ContentType.JSON);

        given().spec(SPEC)
                .contentType(ContentType.JSON)
                .body(profesor)
                .get("/profesores/" + profesorId)
                .then()
                .statusCode(200).contentType(ContentType.JSON)
                .body("nombres", equalTo(profesor.get("nombres")))
                .body("horasClase", equalTo(profesor.get("horasClase")));

    }

    @Test
    public void testPutProfesorWithWrongFields() {

        Map<String, Object> profesor = getProfesor();

        int profesorId = crearProfesor(profesor);

        given().spec(SPEC)
                .contentType(ContentType.JSON)
                .body(profesor)
                .get("/profesores/" + profesorId)
                .then()
                .statusCode(200).contentType(ContentType.JSON)
                .body("nombres", equalTo(profesor.get("nombres")))
                .body("horasClase", equalTo(profesor.get("horasClase")));

        profesor.put("nombres", null);
        profesor.put("horasClase", -1.26d);

        given().spec(SPEC)
                .contentType(ContentType.JSON)
                .body(profesor)
                .put("/profesores/" + profesorId)
                .then()
                .statusCode(400).contentType(ContentType.JSON);

    }

    @Test
    public void testPostProfesorWithWrongFields() {

        Map<String, Object> profesor = new HashMap<>();
        profesor.put("id", 0);
        profesor.put("nombres", "");
        profesor.put("apellidos", null);
        profesor.put("numeroEmpleado", -3688);
        profesor.put("horasClase", -1.26d);

        given().spec(SPEC)
                .contentType(ContentType.JSON)
                .body(profesor)
                .post("/profesores")
                .then()
                .statusCode(400).contentType(ContentType.JSON);
    }

    @Test
    public void testDeleteProfesor() {

        Map<String, Object> profesor = getProfesor();

        int profesorId = crearProfesor(profesor);

        given().spec(SPEC)
                .contentType(ContentType.JSON)
                .body(profesor)
                .get("/profesores/" + profesorId)
                .then()
                .statusCode(200).contentType(ContentType.JSON);

        given().spec(SPEC)
                .delete("/profesores/" + profesorId)
                .then()
                .statusCode(200);

        given().spec(SPEC)
                .get("/profesores/" + profesorId)
                .then()
                .statusCode(404);

    }

    @Test
    public void testDeleteWrongProfesor() {

        Map<String, Object> profesor = getProfesor();

        given().spec(SPEC)
                .contentType(ContentType.JSON)
                .body(profesor)
                .post("/profesores")
                .then()
                .statusCode(201).contentType(ContentType.JSON);

        given().spec(SPEC)
                .delete("/profesores/" + Constants.getRandomId())
                .then()
                .statusCode(404);
    }

    private int crearProfesor(Map<String, Object> profesor) {
        return given().spec(SPEC)
                .contentType(ContentType.JSON)
                .body(profesor)
                .post("/profesores")
                .then()
                .statusCode(201).contentType(ContentType.JSON)
                .extract().path("id");
    }

    private Map<String, Object> getProfesor() {
        Map<String, Object> profesor = new HashMap<>();
        profesor.put("nombres", "Profesor");
        profesor.put("apellidos", "Rodriguez");
        profesor.put("numeroEmpleado", Constants.getRandomId());
        profesor.put("horasClase", Constants.getRandomHoras());
        return profesor;
    }

}
