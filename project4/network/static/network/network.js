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

function editPost(elmnt) {

    // Grab the clicked post, content, and edit button
    const postElmnt = elmnt.parentNode;
    const contentElmnt = postElmnt.querySelector(".content");
    const editBtn = postElmnt.querySelector(".edit-btn");

    // Create textarea and remove previous div
    const textareaElmnt = createPostContent("textarea", contentElmnt.innerHTML);
    postElmnt.insertBefore(textareaElmnt, contentElmnt);
    contentElmnt.remove();

    // Create save button and remove edit button
    const saveBtn = createPostBtn("save");
    postElmnt.insertBefore(saveBtn, editBtn);
    editBtn.remove();
};

function savePost(elmnt) {

    // Grab the post, textarea, and save button
    const postElmnt = elmnt.parentNode;
    const textArea = postElmnt.querySelector(".new-content");
    const saveBtn = postElmnt.querySelector(".save-btn");

    // Grab the post data, and CSRF token
    const postID = postElmnt.dataset.postId;
    const userID = postElmnt.dataset.userId;
    const csrftoken = Cookies.get('csrftoken');

    // Set request object
    const request = new Request(
        `/edit/${postID}`,
        {
            method: 'PUT',
            headers: {'X-CSRFToken': csrftoken},
            mode: 'same-origin',
            body: JSON.stringify({
                userID: userID,
                postContent: textArea.value
            })
        }
    );

    // Query DB
    fetch(request)
    .then(response => response.json())
    .then(data => {

        // Invalid request
        if (data.error) {
            alert(`Sorry: ${data.error}`);
        }

        // Post successfully updated
        else {

            // Create content div and remove textarea
            const contentDiv = createPostContent("div", textArea.value);
            postElmnt.insertBefore(contentDiv, textArea);
            textArea.remove();

            // Create edit button and remove save button
            const editBtn = createPostBtn("edit");
            postElmnt.insertBefore(editBtn, saveBtn);
            saveBtn.remove();
        };
    });
};

function createPostBtn(btnType) {
/**
 * Returns a button element node
 * 
 * {btnType} must be equal to "edit" or "save"
 * returns button element node, or null
 */
    let newElmnt = null;
    if (btnType == "edit" || btnType == "save") {
        newElmnt = document.createElement("button");
        newElmnt.classList.add(`${btnType}-btn`, "btn", "btn-link", "btn-sm");
        newElmnt.setAttribute("type", "button");
        newElmnt.setAttribute("onclick", `${btnType}Post(this)`);

        // Upper case "btnType"
        let firstChar = btnType.charAt(0);
        let endChars = btnType.slice(1);
        let firstUpper = firstChar.toUpperCase();
        const btnLabel = firstUpper.concat(endChars);
        newElmnt.innerHTML = btnLabel;
    };
    return newElmnt;
}

function createPostContent(elmntType, text) {
/**
 * Returns a HTML element node based upon the {elmntType} with value {text}
 * 
 * {elmntType} must be equal to "textarea" or "div"
 * {text} string value for return element
 * returns HTML element node, or null
 */
    let newElmnt = null;
    if (elmntType == "textarea") {
        newElmnt = document.createElement("textarea");
        newElmnt.classList.add("new-content", "form-control");
        newElmnt.setAttribute("rows", "3");
        newElmnt.innerHTML = text;
    }
    else if (elmntType == "div") {
        newElmnt = document.createElement("div");
        newElmnt.classList.add("content");
        newElmnt.innerHTML = text;
    };
    return newElmnt;
}
