export const getUser = async () => {
    const user = await localStorage.getItem("currentUser")
    if (!user) {
        return null
    } else {
        return JSON.parse(user)
    }
}

export const renderLoginPage = (container) => {
    container.innerHTML = `
        <div style="max-width: 400px; width: 100%; margin: auto; background: #fff; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
            <h2 style="text-align:center; color:#4a90e2;">Login</h2>
            <form id="loginForm">
                <div style="margin-bottom: 15px;">
                    <label for="email">Email</label>
                    <input type="email" id="email" name="email" style="width:100%; padding:10px; margin-top:5px;"/>
                </div>
                <div style="margin-bottom: 15px;">
                    <label for="password">Password</label>
                    <input type="password" id="password" name="password" style="width:100%; padding:10px; margin-top:5px;"/>
                </div>
                <button type="submit" style="width:100%; padding:12px; background:#4a90e2; color:#fff; border:none; border-radius:5px; cursor:pointer;">Login</button>
                <button type="submit" style="width:100%; padding:12px; background:#4a90e2; color:#fff; border:none; border-radius:5px; cursor:pointer;">Logout</button>
            </form>
        </div>
    `;

    const loginForm = document.getElementById("loginForm");
    loginForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const email = document.getElementById("email").value;
        const password = document.getElementById("password").value;
        try {
            const dataInfo={
                email:email,
                password:password
            }
            const response = await fetch(`/auth/users/login/${email}/${password}`, {
                method: "GET",
                headers: {
                    "Content-Type": "application/json"
                }
            });
    
            if (!response.ok) {
                const error = await response.json();
                alert(error.detail || "Login failed");
                return;
            }
    
            const data = await response.json();
            console.log("Login success:", data);
            alert("Login successful!");
    
            // Optionally, save user to localStorage
            localStorage.setItem("currentUser", JSON.stringify(data.user));
    
            // Then render dashboard or reload content
        } catch (err) {
            console.error("Login error:", err);
            alert("Login error. Check console.");
        }
    });
};
