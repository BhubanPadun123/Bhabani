import {
    getUser,
    renderLoginPage
} from "./utils/sidebar.js"
import {
    renderDashboard
} from "./utils/dashboard.js"


async function ___init__(){
    const dashboard = document.getElementById("dashboard")
    const courses = document.getElementById("courses")
    const students = document.getElementById("students")
    const reports = document.getElementById("reports")
    const setting = document.getElementById("setting")
    const login = document.getElementById("login")

    console.log(login)


    const contentRenderArea = document.querySelector(".content")

    const user = await getUser()
    console.log(user)
    if(!user && login ){
        renderLoginPage(contentRenderArea)
    }else{
        login.addEventListener("click",(e)=> {
            if(!contentRenderArea) return
            e.preventDefault()
            contentRenderArea.innerHTML = ""
            renderLoginPage(contentRenderArea)
        })
        dashboard.addEventListener("click",(e)=> {
            e.preventDefault()
            contentRenderArea.innerHTML = ""
            renderDashboard(contentRenderArea)
        })


        const user_name = document.getElementById("user_name")
        if(user_name){
            user_name.innerHTML = `<h4>${user.user_name}</h4>`
        }
    }
}
___init__()