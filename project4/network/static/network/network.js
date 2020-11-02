document.addEventListener("DOMContentLoaded", function() {

    console.log("Loaded!")
    // Follow button
    document.querySelector("#follow-form").onsubmit = function() {
        follow();
        return false;
    };

});

function follow() {

    // Grab page elements to update
    const btn = document.querySelector("#follow-btn");
    const followers_span = document.querySelector("#num-followers")
    let num_followers = parseInt(followers_span.innerHTML)

    // Grab the username and CSRF Token 
    // https://docs.djangoproject.com/en/3.1/ref/csrf/#acquiring-the-token-if-csrf-use-sessions-and-csrf-cookie-httponly-are-false
    const profile_username_path = window.location.pathname.slice(9);
    const csrftoken = Cookies.get('csrftoken');

    // Set request object
    const request = new Request(
        `/profile/${profile_username_path}`,
        {method: 'PUT',
        headers: {'X-CSRFToken': csrftoken}}
    );

    // Toggle active user following profile username
    fetch(request, {
        method: "PUT",
        mode: 'same-origin'
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert(`Sorry: ${data.error}`);
        }
        else {
            if (data.following) {
                btn.value = "Unfollow";
                followers_span.innerHTML = ++num_followers;
            }
            else {
                btn.value = "Follow";
                followers_span.innerHTML = --num_followers;
            }

        }
    })

};
