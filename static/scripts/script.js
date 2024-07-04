const wrapper = document.querySelector('.wrapper');
const btnPopup = document.querySelector('.btnLogin-popup');
const iconClose = document.querySelector('.icon-close');
const removeMain = document.querySelector('.main-body');
const loginBtn = document.querySelector('.btn')




btnPopup.addEventListener('click', () => {
    removeMain.classList.add('hidden');
    wrapper.classList.add('active-popup');
})

iconClose.addEventListener('click', () => {
    wrapper.classList.remove('active-popup');
    removeMain.classList.remove("hidden");

})

loginBtn.addEventListener('click', () => {

})

document.getElementById("login-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const data = new FormData(e.target);
    console.log(data.get("email"), data.get("password"));
    // const res = await fetch("http://localhost:5000/login", {
    //     method: "POST",
    //     headers: { "Content-Type": "form-data" },
    //     data: data
    // })
    const formdata = new FormData();
    formdata.append("email", data.get("email"));
    formdata.append("password", data.get("password"));

    const requestOptions = {
        method: "POST",
        body: formdata,
        redirect: "follow"
    };

    const res = await fetch("http://127.0.0.1:5000/login", requestOptions)
    if (!res.ok) {
        alert("Invalid Username or Password!");
        return;
    }
    const jsonData = await res.json();
    console.log(jsonData);
    window.localStorage.setItem("access_token", jsonData.access_token);
    window.localStorage.setItem("expires_at", jsonData.expires_at);
    window.location.href = "/dashboard.html"
})