setInterval(()=> {
    let pass = document.getElementById("exampleInputPassword").value;
    let repass = document.getElementById("exampleRepeatPassword");
    let email = document.getElementById("exampleInputEmail").value;

    // RegEx Same as validation.py
    const password_regex = /^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[a-zA-Z])(?=.*[!@#$%^&*()]).{8,20}$/;
    const email_regex = /[a-zA-Z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-zA-Z0-9!#$%&'*+/=?^_`{|}~-]+)*@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?/

    if (pass === repass.value && pass != "" && password_regex.test(repass.value)) 
    {
        repass.removeAttribute("style");
        if (email_regex.test(email))
        document.getElementById("submit").disabled = false;  
    }
    else
    {
        if(repass.value != "")
        {
            repass.setAttribute("style","box-shadow:0 0 0 0.2rem rgba(240, 50, 50, 0.25)");
        }
        document.getElementById("submit").disabled = true;
    }
}, 100);