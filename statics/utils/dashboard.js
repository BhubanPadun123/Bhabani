export function renderDashboard(container) {
    container.innerHTML = `
    <div>
       <div class="cards">
                <div class="card">
                    <h3>📚 Courses</h3>
                    <p>25</p>
                </div>
                <div class="card">
                    <h3>👩‍🎓 Students</h3>
                    <p>120</p>
                </div>
                <div class="card">
                    <h3>📊 Reports</h3>
                    <p>8</p>
                </div>
            </div>

            <!-- Table -->
            <div class="table-container">
                <h3>Recent Activities</h3>
                <table>
                    <thead>
                        <tr>
                            <th>Student</th>
                            <th>Course</th>
                            <th>Status</th>
                            <th>Date</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>Alice</td>
                            <td>Python Basics</td>
                            <td>Completed</td>
                            <td>2025-09-01</td>
                        </tr>
                        <tr>
                            <td>Bob</td>
                            <td>Data Science</td>
                            <td>In Progress</td>
                            <td>2025-09-03</td>
                        </tr>
                        <tr>
                            <td>Charlie</td>
                            <td>Web Development</td>
                            <td>Enrolled</td>
                            <td>2025-09-05</td>
                        </tr>
                    </tbody>
                </table>
            </div>
    </div>
    `;
}
