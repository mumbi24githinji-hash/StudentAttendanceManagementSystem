/* =========================================================
   STUDENT ATTENDANCE MANAGEMENT SYSTEM
   Main JavaScript File
========================================================= */


/* =========================================================
   DATABASE STORAGE
========================================================= */

const STUDENTS_KEY = "attendance_students";
const RECORDS_KEY = "attendance_records";
const LOGIN_KEY = "attendance_logged_in";


/* =========================================================
   HELPER FUNCTIONS
========================================================= */

function getStudents() {

    return JSON.parse(
        localStorage.getItem(STUDENTS_KEY) || "[]"
    );

}


function saveStudents(students) {

    localStorage.setItem(
        STUDENTS_KEY,
        JSON.stringify(students)
    );

}


function getRecords() {

    return JSON.parse(
        localStorage.getItem(RECORDS_KEY) || "[]"
    );

}


function saveRecords(records) {

    localStorage.setItem(
        RECORDS_KEY,
        JSON.stringify(records)
    );

}


function todayDate() {

    const today = new Date();

    const year = today.getFullYear();

    const month = String(
        today.getMonth() + 1
    ).padStart(2, "0");

    const day = String(
        today.getDate()
    ).padStart(2, "0");

    return `${year}-${month}-${day}`;

}


function showMessage(elementId, message, success = true) {

    const element = document.getElementById(elementId);

    if (!element) {
        return;
    }

    element.textContent = message;

    element.className =
        success
            ? "message success-message"
            : "message error-message";

}


/* =========================================================
   LOGIN SYSTEM
========================================================= */

function checkLogin() {

    const loggedIn =
        localStorage.getItem(LOGIN_KEY);

    const protectedPages = [
        "dashboard.html",
        "students.html",
        "attendance.html",
        "reports.html"
    ];

    const currentPage =
        window.location.pathname
            .split("/")
            .pop();

    if (
        protectedPages.includes(currentPage) &&
        loggedIn !== "true"
    ) {

        window.location.href = "login.html";

    }

}


function logout() {

    localStorage.removeItem(LOGIN_KEY);

    window.location.href = "login.html";

}


document.addEventListener(
    "DOMContentLoaded",
    function () {

        checkLogin();

        setupLogin();

        setupStudents();

        setupAttendance();

        setupReports();

        loadDashboard();

    }
);


/* =========================================================
   LOGIN
========================================================= */

function setupLogin() {

    const form =
        document.getElementById("loginForm");

    if (!form) {
        return;
    }

    form.addEventListener(
        "submit",
        function (event) {

            event.preventDefault();

            const username =
                document.getElementById(
                    "username"
                ).value.trim();

            const password =
                document.getElementById(
                    "password"
                ).value.trim();

            /*
                Demo administrator account
            */

            if (
                username === "admin" &&
                password === "admin123"
            ) {

                localStorage.setItem(
                    LOGIN_KEY,
                    "true"
                );

                window.location.href =
                    "dashboard.html";

            } else {

                showMessage(
                    "loginMessage",
                    "Invalid username or password.",
                    false
                );

            }

        }
    );

}


/* =========================================================
   STUDENT MANAGEMENT
========================================================= */

function setupStudents() {

    const form =
        document.getElementById("studentForm");

    if (!form) {
        return;
    }

    displayStudents();

    form.addEventListener(
        "submit",
        function (event) {

            event.preventDefault();

            addStudent();

        }
    );


    const search =
        document.getElementById(
            "studentSearch"
        );

    if (search) {

        search.addEventListener(
            "input",
            function () {

                displayStudents(
                    this.value
                );

            }
        );

    }

}


function addStudent() {

    const regNo =
        document.getElementById(
            "regNo"
        ).value.trim();

    const name =
        document.getElementById(
            "studentName"
        ).value.trim();

    const course =
        document.getElementById(
            "course"
        ).value.trim();

    const year =
        document.getElementById(
            "year"
        ).value;

    const gender =
        document.getElementById(
            "gender"
        ).value;


    if (
        !regNo ||
        !name ||
        !course ||
        !year ||
        !gender
    ) {

        showMessage(
            "studentMessage",
            "Please fill in all fields.",
            false
        );

        return;

    }


    const students =
        getStudents();


    const exists =
        students.some(
            student =>
                student.regNo.toLowerCase() ===
                regNo.toLowerCase()
        );


    if (exists) {

        showMessage(
            "studentMessage",
            "A student with this registration number already exists.",
            false
        );

        return;

    }


    const student = {

        id: Date.now(),

        regNo: regNo,

        name: name,

        course: course,

        year: year,

        gender: gender

    };


    students.push(student);

    saveStudents(students);


    document.getElementById(
        "studentForm"
    ).reset();


    showMessage(
        "studentMessage",
        "Student added successfully!",
        true
    );


    displayStudents();

}


function displayStudents(
    searchTerm = ""
) {

    const table =
        document.getElementById(
            "studentsTable"
        );

    if (!table) {
        return;
    }


    const students =
        getStudents();


    const search =
        searchTerm.toLowerCase();


    const filtered =
        students.filter(
            student =>
                student.name
                    .toLowerCase()
                    .includes(search) ||

                student.regNo
                    .toLowerCase()
                    .includes(search) ||

                student.course
                    .toLowerCase()
                    .includes(search)
        );


    table.innerHTML = "";


    if (filtered.length === 0) {

        table.innerHTML = `
            <tr>
                <td colspan="7" class="empty-row">
                    No students found.
                </td>
            </tr>
        `;

        return;

    }


    filtered.forEach(
        function (student, index) {

            const row =
                document.createElement("tr");


            row.innerHTML = `

                <td>${index + 1}</td>

                <td>
                    <strong>
                        ${escapeHTML(student.regNo)}
                    </strong>
                </td>

                <td>
                    ${escapeHTML(student.name)}
                </td>

                <td>
                    ${escapeHTML(student.course)}
                </td>

                <td>
                    ${escapeHTML(student.year)}
                </td>

                <td>
                    ${escapeHTML(student.gender)}
                </td>

                <td>

                    <button
                        class="action-btn delete-btn"
                        onclick="deleteStudent(${student.id})"
                    >
                        Delete
                    </button>

                </td>

            `;


            table.appendChild(row);

        }
    );

}


function deleteStudent(id) {

    const students =
        getStudents();


    const student =
        students.find(
            s => s.id === id
        );


    if (!student) {
        return;
    }


    const confirmed =
        confirm(
            `Are you sure you want to delete ${student.name}?`
        );


    if (!confirmed) {
        return;
    }


    const updated =
        students.filter(
            student =>
                student.id !== id
        );


    saveStudents(updated);


    /*
        Also remove attendance records
        belonging to the deleted student.
    */

    const records =
        getRecords().filter(
            record =>
                record.studentId !== id
        );


    saveRecords(records);


    displayStudents();

    loadDashboard();

}


/* =========================================================
   ATTENDANCE
========================================================= */

function setupAttendance() {

    const table =
        document.getElementById(
            "attendanceTable"
        );

    if (!table) {
        return;
    }


    const dateInput =
        document.getElementById(
            "attendanceDate"
        );


    if (dateInput) {

        dateInput.value =
            todayDate();

    }


    displayAttendance();


    if (dateInput) {

        dateInput.addEventListener(
            "change",
            displayAttendance
        );

    }


    const courseInput =
        document.getElementById(
            "attendanceCourse"
        );


    if (courseInput) {

        courseInput.addEventListener(
            "input",
            displayAttendance
        );

    }

}


function displayAttendance() {

    const table =
        document.getElementById(
            "attendanceTable"
        );

    if (!table) {
        return;
    }


    const students =
        getStudents();


    const date =
        document.getElementById(
            "attendanceDate"
        ).value;


    const course =
        document.getElementById(
            "attendanceCourse"
        ).value
        .trim()
        .toLowerCase();


    const filtered =
        students.filter(
            student =>
                !course ||
                student.course
                    .toLowerCase()
                    .includes(course)
        );


    const records =
        getRecords();


    table.innerHTML = "";


    if (filtered.length === 0) {

        table.innerHTML = `
            <tr>
                <td colspan="6" class="empty-row">
                    No students available.
                    Please add students first.
                </td>
            </tr>
        `;

        updateAttendanceSummary();

        return;

    }


    filtered.forEach(
        function (student, index) {

            const existing =
                records.find(
                    record =>
                        record.studentId === student.id &&
                        record.date === date
                );


            let presentChecked = "";

            let absentChecked = "";


            if (
                existing &&
                existing.status === "Present"
            ) {

                presentChecked = "checked";

            }


            if (
                existing &&
                existing.status === "Absent"
            ) {

                absentChecked = "checked";

            }


            const row =
                document.createElement("tr");


            row.innerHTML = `

                <td>
                    ${index + 1}
                </td>

                <td>
                    ${escapeHTML(student.regNo)}
                </td>

                <td>
                    ${escapeHTML(student.name)}
                </td>

                <td>
                    ${escapeHTML(student.course)}
                </td>

                <td>

                    <label>
                        <input
                            type="radio"
                            name="attendance_${student.id}"
                            value="Present"
                            ${presentChecked}
                        >

                        Present
                    </label>

                </td>

                <td>

                    <label>
                        <input
                            type="radio"
                            name="attendance_${student.id}"
                            value="Absent"
                            ${absentChecked}
                        >

                        Absent
                    </label>

                </td>

            `;


            table.appendChild(row);

        }
    );


    updateAttendanceSummary();

}


function saveAttendance() {

    const date =
        document.getElementById(
            "attendanceDate"
        ).value;


    if (!date) {

        showMessage(
            "attendanceMessage",
            "Please select an attendance date.",
            false
        );

        return;

    }


    const students =
        getStudents();


    if (students.length === 0) {

        showMessage(
            "attendanceMessage",
            "Please register students first.",
            false
        );

        return;

    }


    let records =
        getRecords();


    let savedCount = 0;


    students.forEach(
        function (student) {

            const selected =
                document.querySelector(
                    `input[name="attendance_${student.id}"]:checked`
                );


            if (!selected) {
                return;
            }


            const status =
                selected.value;


            const existingIndex =
                records.findIndex(
                    record =>
                        record.studentId === student.id &&
                        record.date === date
                );


            const attendanceRecord = {

                id:
                    existingIndex >= 0
                        ? records[existingIndex].id
                        : Date.now() +
                          Math.random(),

                studentId:
                    student.id,

                regNo:
                    student.regNo,

                studentName:
                    student.name,

                date:
                    date,

                status:
                    status

            };


            if (existingIndex >= 0) {

                records[existingIndex] =
                    attendanceRecord;

            } else {

                records.push(
                    attendanceRecord
                );

            }


            savedCount++;

        }
    );


    saveRecords(records);


    showMessage(
        "attendanceMessage",
        `${savedCount} attendance record(s) saved successfully!`,
        true
    );


    updateAttendanceSummary();

    loadDashboard();

}


function updateAttendanceSummary() {

    const dateInput =
        document.getElementById(
            "attendanceDate"
        );


    if (!dateInput) {
        return;
    }


    const date =
        dateInput.value;


    const records =
        getRecords().filter(
            record =>
                record.date === date
        );


    const present =
        records.filter(
            record =>
                record.status === "Present"
        ).length;


    const absent =
        records.filter(
            record =>
                record.status === "Absent"
        ).length;


    const presentElement =
        document.getElementById(
            "attendancePresent"
        );


    const absentElement =
        document.getElementById(
            "attendanceAbsent"
        );


    const totalElement =
        document.getElementById(
            "attendanceTotal"
        );


    if (presentElement) {
        presentElement.textContent =
            present;
    }


    if (absentElement) {
        absentElement.textContent =
            absent;
    }


    if (totalElement) {
        totalElement.textContent =
            present + absent;
    }

}


/* =========================================================
   DASHBOARD
========================================================= */

function loadDashboard() {

    const totalStudentsElement =
        document.getElementById(
            "totalStudents"
        );


    if (!totalStudentsElement) {
        return;
    }


    const students =
        getStudents();


    const records =
        getRecords();


    const today =
        todayDate();


    const todayRecords =
        records.filter(
            record =>
                record.date === today
        );


    const present =
        todayRecords.filter(
            record =>
                record.status === "Present"
        ).length;


    const absent =
        todayRecords.filter(
            record =>
                record.status === "Absent"
        ).length;


    const totalToday =
        present + absent;


    let rate = 0;


    if (totalToday > 0) {

        rate =
            Math.round(
                (present / totalToday) * 100
            );

    }


    document.getElementById(
        "totalStudents"
    ).textContent =
        students.length;


    document.getElementById(
        "presentCount"
    ).textContent =
        present;


    document.getElementById(
        "absentCount"
    ).textContent =
        absent;


    document.getElementById(
        "attendanceRate"
    ).textContent =
        `${rate}%`;


    displayRecentAttendance();

}


function displayRecentAttendance() {

    const table =
        document.getElementById(
            "recentAttendanceTable"
        );


    if (!table) {
        return;
    }


    const records =
        getRecords();


    table.innerHTML = "";


    if (records.length === 0) {

        table.innerHTML = `
            <tr>
                <td colspan="4" class="empty-row">
                    No attendance records yet.
                </td>
            </tr>
        `;

        return;

    }


    const sorted =
        [...records]
            .sort(
                (a, b) =>
                    new Date(b.date) -
                    new Date(a.date)
            )
            .slice(0, 10);


    sorted.forEach(
        function (record) {

            const row =
                document.createElement("tr");


            const statusClass =
                record.status === "Present"
                    ? "performance-excellent"
                    : "performance-poor";


            row.innerHTML = `

                <td>
                    ${escapeHTML(record.regNo)}
                </td>

                <td>
                    ${escapeHTML(record.studentName)}
                </td>

                <td>
                    ${escapeHTML(record.date)}
                </td>

                <td class="${statusClass}">
                    ${escapeHTML(record.status)}
                </td>

            `;


            table.appendChild(row);

        }
    );

}


/* =========================================================
   REPORTS
========================================================= */

function setupReports() {

    const table =
        document.getElementById(
            "reportsTable"
        );


    if (!table) {
        return;
    }


    const dateElement =
        document.getElementById(
            "reportDate"
        );


    if (dateElement) {

        dateElement.textContent =
            "Generated on: " +
            new Date().toLocaleDateString();

    }


    displayReports();


    const search =
        document.getElementById(
            "reportSearch"
        );


    if (search) {

        search.addEventListener(
            "input",
            function () {

                displayReports(
                    this.value
                );

            }
        );

    }

}


function displayReports(
    searchTerm = ""
) {

    const table =
        document.getElementById(
            "reportsTable"
        );


    if (!table) {
        return;
    }


    const students =
        getStudents();


    const records =
        getRecords();


    const search =
        searchTerm.toLowerCase();


    const filtered =
        students.filter(
            student =>
                student.name
                    .toLowerCase()
                    .includes(search) ||

                student.regNo
                    .toLowerCase()
                    .includes(search) ||

                student.course
                    .toLowerCase()
                    .includes(search)
        );


    table.innerHTML = "";


    let totalRecords = 0;

    let totalPresent = 0;


    filtered.forEach(
        function (student) {

            const studentRecords =
                records.filter(
                    record =>
                        record.studentId ===
                        student.id
                );


            const total =
                studentRecords.length;


            const present =
                studentRecords.filter(
                    record =>
                        record.status ===
                        "Present"
                ).length;


            const absent =
                studentRecords.filter(
                    record =>
                        record.status ===
                        "Absent"
                ).length;


            const percentage =
                total > 0
                    ? Math.round(
                        (present / total) *
                        100
                    )
                    : 0;


            let performance =
                "Poor";


            let performanceClass =
                "performance-poor";


            if (percentage >= 75) {

                performance =
                    "Excellent";

                performanceClass =
                    "performance-excellent";

            } else if (percentage >= 50) {

                performance =
                    "Average";

                performanceClass =
                    "performance-average";

            }


            totalRecords += total;

            totalPresent += present;


            const row =
                document.createElement("tr");


            row.innerHTML = `

                <td>
                    ${table.rows.length + 1}
                </td>

                <td>
                    ${escapeHTML(student.regNo)}
                </td>

                <td>
                    ${escapeHTML(student.name)}
                </td>

                <td>
                    ${escapeHTML(student.course)}
                </td>

                <td>
                    ${total}
                </td>

                <td>
                    ${present}
                </td>

                <td>
                    ${absent}
                </td>

                <td>
                    <strong>
                        ${percentage}%
                    </strong>
                </td>

                <td class="${performanceClass}">
                    ${performance}
                </td>

            `;


            table.appendChild(row);

        }
    );


    if (filtered.length === 0) {

        table.innerHTML = `
            <tr>
                <td colspan="9" class="empty-row">
                    No students found.
                </td>
            </tr>
        `;

    }


    const overallRate =
        totalRecords > 0
            ? Math.round(
                (totalPresent /
                totalRecords) *
                100
            )
            : 0;


    const totalStudentsElement =
        document.getElementById(
            "reportTotalStudents"
        );


    const totalRecordsElement =
        document.getElementById(
            "reportTotalRecords"
        );


    const overallRateElement =
        document.getElementById(
            "reportOverallRate"
        );


    if (totalStudentsElement) {

        totalStudentsElement.textContent =
            filtered.length;

    }


    if (totalRecordsElement) {

        totalRecordsElement.textContent =
            totalRecords;

    }


    if (overallRateElement) {

        overallRateElement.textContent =
            `${overallRate}%`;

    }

}


/* =========================================================
   SECURITY / DISPLAY HELPER
========================================================= */

function escapeHTML(value) {

    const div =
        document.createElement("div");

    div.textContent =
        value;

    return div.innerHTML;

}