document.addEventListener('DOMContentLoaded', function () {
    document.getElementById('membership').addEventListener('click', function () {
        loadContent('membership');
    });

    document.getElementById('classes').addEventListener('click', function () {
        loadContent('classes');
    });

    document.getElementById('payments').addEventListener('click', function () {
        loadContent('payments');
    });

    document.getElementById('equipment').addEventListener('click', function () {
        loadContent('equipment');
    });

    document.getElementById('trainer').addEventListener('click', function () {
        loadContent('trainer');
    });
});

function loadContent(type) {
    let content = document.getElementById('content');
    switch (type) {
        case 'membership':
            content.innerHTML = `
                <h2>Apply for Membership</h2>
                <form id="membershipForm">
                    
                    <label for="membershipType">Membership Type:</label>
                    <select id="membershipType">
                        <option value="basic">Basic</option>
                        <option value="premium">Premium</option>
                        <option value="vip">VIP</option>
                    </select>
                    <button type="submit">Apply</button>
                </form>
            `;
            break;
        case 'classes':
            content.innerHTML = `
                <h2>Apply for Classes</h2>
                <form id="classesForm">
                    <label for="classType">Class Type:</label>
                    <select id="classType">
                        <option value="yoga">Yoga</option>
                        <option value="cardio">Cardio</option>
                        <option value="strength">Strength Training</option>
                    </select>
                    <button type="submit">Apply</button>
                </form>
            `;
            break;
        case 'payments':
            content.innerHTML = `
                <h2>Check Payments</h2>
                <p>No payment information available.</p>
            `;
            break;
        case 'equipment':
            content.innerHTML = `
                <h2>View Equipment</h2>
                <ul>
                    <li>Treadmill</li>
                    <li>Dumbbells</li>
                    <li>Bench Press</li>
                    <li>Rowing Machine</li>
                </ul>
            `;
            break;
        case 'trainer':
            content.innerHTML = `
            <h2>Apply for Trainer</h2>
            <form id="trainerForm">
                <label>Select Trainer:</label>
                <select id="trainerType">
                    <option value="Trainer1"> Trainer 1</option>
                    <option value="Trainer2"> Trainer 2</option>
                    <option value="Trainer3"> Trainer 3</option>
                </select>
                <button type="submit">Submit</button>
            `;
            break;
        default:
            content.innerHTML = `<h2>Welcome to the Gym Management Dashboard</h2><p>Select an option from the menu to get started.</p>`;
    }
}

window.addEventListener("load", async (e) => {
    const data = await fetch("http://127.0.0.1:5000/members", {
        method: "GET",
        headers: { "Authorization": `Bearer ${localStorage.getItem("access_token")}` }
    });
    if (data.status === 401) {
        window.location.href = "/";
    }
    const jsonData = await data.json();
    document.getElementById("members-div").innerHTML = `
        <table cellspacing="15">
            <thead>
                <tr>
                    <th>Member Name</th>
                    <th>Member Phone</th>
                </tr>
            </thead>
            <tbody>
                ${jsonData.map((e) => "<tr><td>" + e.name + "</td><td>" + e.phno + "</td></tr>")}
            </tbody>
        </table>
    `
})